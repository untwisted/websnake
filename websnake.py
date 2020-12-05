from untwisted.client import lose, create_client, create_client_ssl
from urllib3.filepost import encode_multipart_formdata
from urllib.parse import urlencode, urlparse
from untwisted.task import Task, DONE
from untwisted.splits import AccUntil, TmpFile
from untwisted.dispatcher import Dispatcher
from untwisted.event import Event, SSL_CONNECT, SSL_CONNECT_ERR, CLOSE, CONNECT, CONNECT_ERR
from cgi import FieldStorage, parse_header
from base64 import encodebytes
from tempfile import TemporaryFile 
from socket import getservbyname
from untwisted.core import die
from re import split
from untwisted import core
import json

default_headers = {
'user-agent':'Websnake', 
'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
'connection':'close'}

RESP_ERR = 0
CON_ERR  = 1
SIZE_ERR = 2

ERR_CODES = {
    RESP_ERR : 'Corrupted response.', 
    CON_ERR  : 'Connection refused.', 
    SIZE_ERR : 'Content-length too long'
}

class Headers:
    def __init__(self, data):
        self.headers = dict()
        lines = data.split('\r\n')

        for ind in lines:
            field, value = split(' *: *', ind, 1)
            self.headers[field.lower()] = value

    def get(self, field, default=None):
        field = field.lower()
        return self.headers.get(field, default)

    def set(self, field, value):
        self.headers[field.lower()] == value

    def update(self, other):
        for ind in other.headers.items():
            self.headers[ind[0].lower()] = ind[1]

    def __str__(self):
        return self.headers.__str__()

    def __repr__(self):
        return self.headers.__repr__()

class ResponseHandle:
    class DONE(Event):
        pass

    class ERROR(Event):
        pass

    class RESPONSE(Event):
        pass

    MAX_SIZE = 1024 ** 8
    def __init__(self, request):
        self.request = request
        self.response = None
        self.acc = AccUntil(request.con)

        request.con.add_map(AccUntil.DONE, self.handle_terminator)
        request.con.add_map(CLOSE,  self.handle_close)
        self.acc.start()

    def handle_terminator(self, con, header, bdata):
        """
        """

        self.response = Response(header)
        size = self.response.headers.get('content-length', self.MAX_SIZE)
        size = int(size)

        if self.MAX_SIZE < size:
            self.handle_size_err()
        else:
            self.recv_data(size, bdata)

    def recv_data(self, size, bdata):
        tmpfile = TmpFile(self.request.con)

        self.request.con.add_map(TmpFile.DONE,  self.handle_bdata)
        tmpfile.start(self.response.fd, size, bdata)

    def handle_bdata(self, con, fd, data):
        lose(con)
        self.handle_response()

    def handle_size_err(self):
        self.request.drive(self.ERROR, self.response, SIZE_ERR)
        self.request.con.destroy()
        self.request.con.close()
        self.response.fd.close()

    def handle_redirect(self):
        # When a code means a redirect but no location then it is an error.
        location = self.response.headers.get('location')
        if location is not None:
            self.request.redirect(location)
        else:
            self.request.drive(self.ERROR, self.response, RESP_ERR)

    def handle_response(self):
        self.response.fd.seek(0)
        self.request.drive(self.response.code, self.response)
        self.request.drive(ResponseHandle.RESPONSE, self.response)

        REDIRECT_CODES = ('301', '308', '302', '303', '307')
        if self.response.code in REDIRECT_CODES:
            self.handle_redirect()
        else:
            self.request.drive(self.DONE, self.response)
        self.response.fd.close()

    def handle_close(self, con, err):
        if self.response is not None:
            self.handle_response()
        else:
            self.handle_resp_err()

    def handle_resp_err(self):
        if self.request.c_attempts >= self.request.attempts:
            self.request.drive(self.ERROR, self.response, RESP_ERR)
        else:
            self.request.reconnect()

class Response:
    def __init__(self, data):
        data = data.decode('utf8')
        method, hdata = data.split('\r\n', 1)
        code = method.split(' ', 2)
        self.version = code[0]
        self.code    = code[1]
        self.reason  = code[2]
        self.headers = Headers(hdata)
        self.fd = TemporaryFile('w+b')

    def content(self):
        data = self.fd.read()
        self.fd.seek(0)

        encoding = self.header_encoding()
        if encoding is None:
            return data

        try:
            return data.decode(encoding)
        except UnicodeDecodeError as e:
            return data

    def header_encoding(self):
        ctype = self.headers.get('content-type')
        if ctype is not None:
            return parse_header(ctype)[1].get('charset')

class RequestData:
    pass

class FormData(RequestData):
    def __init__(self, data):
        self.data = data

    def dumps(self, request):
        data, type = encode_multipart_formdata(self.data)
        request.headers['content-type'] = type
        request.headers['content-length'] = len(data)
        return data

class JSon(RequestData):
    def __init__(self, data):
        self.data = data

    def dumps(self, request):
        request.headers['content-type'] = 'application/json; charset=utf-8'
        data = json.dumps(self.data).encode('utf8')
        request.headers['content-length'] = len(data)
        return data

class RequestAuth:
    pass

class BasicAuth(RequestAuth):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def dumps(self, request):
        self.key = self.key.encode('utf8')
        self.value = self.value.encode('utf8')
    
        base = encodebytes(b'%s:%s' % (self.key, self.value))
        base = base.replace(b'\n', b'').decode('utf8')
        request.headers['authorization'] = base
    
class TokenAuth(RequestAuth):
    def __init__(self, token_value):
        self.token_value = token_value

    def dumps(self, request):
        request.headers['authorization'] = 'token %s' % self.token_value
    
class Request(Dispatcher):
    def __init__(self, addr, headers, version, auth, attempts, pool):
        super(Request, self).__init__()
        self.headers    = default_headers.copy()
        self.version    = version
        self.attempts   = attempts
        self.c_attempts = 0
        self.auth = auth
        self.addr = addr
        self.pool = pool
        self.method = None

        self.headers.update(headers)
        if auth is not None: 
            auth.dumps(self)

        self.con = self.connect(self.addr)
        if pool is not None:
            pool.register(self)

    def handle_connect(self, con):
        pass

    def handle_connect_err(self, con, err):
        # Response is None.        
        self.request.drive(self.ERROR, None, CON_ERR)

    def create_con_ssl(self, addr, port):
        con = create_client_ssl(addr, port)  
        con.add_map(SSL_CONNECT,  self.handle_connect)
        con.add_map(SSL_CONNECT_ERR,  self.handle_connect_err)
        return con
    
    def create_con(self, addr, port):
        con = create_client(addr, port)
        con.add_map(CONNECT,  self.handle_connect)
        con.add_map(CONNECT_ERR,  self.handle_connect_err)
        return con

    def reconnect(self):
        self.con = self.connect(self.addr)

    def connect(self, addr):
        self.addr = addr.strip().rstrip()
        urlparser = urlparse(self.addr)

        port = urlparser.port
        if not port:
            port = getservbyname(urlparser.scheme)
        self.c_attempts = self.c_attempts + 1

        # The hostname has to be here in case of redirect.
        self.headers['host'] = urlparser.hostname
        if urlparser.scheme == 'https':
            return self.create_con_ssl(urlparser.hostname, port)
        return self.create_con(urlparser.hostname, port)
    
    def redirect(self, addr):
        self.con = self.connect(addr)

class Get(Request):
    def __init__(self, addr, args={}, 
        headers={}, version='HTTP/1.1', auth=None, attempts=1, pool=None):
        super(Get, self).__init__(addr, headers, version, auth, attempts, pool)

        self.args = args
        self.method = 'GET'

    def handle_connect(self, con):
        ResponseHandle(self)
        
        request_text = make_method(self.method, self.addr, self.args, self.version)
        headers_text = build_headers(self.headers)
        request_text = request_text + headers_text
        con.dump(request_text)

class Post(Request):
    def __init__(self, addr, args={}, payload=FormData({}), 
        headers={}, version='HTTP/1.1', auth=None, attempts=1, pool=None):

        super(Post, self).__init__(addr, headers, version, auth, attempts, pool)

        self.args = args
        self.payload = payload
        self.method = 'POST'

    def handle_connect(self, con):
        ResponseHandle(self)

        request_text = make_method(self.method, self.addr, self.args, self.version)
        data = self.payload.dumps(self)

        headers_text = build_headers(self.headers)
        request_text = request_text + headers_text 

        request_text = request_text + data
        con.dump(request_text)
    
class Put(Post):
    def __init__(self, addr, args={}, payload=FormData({}), 
        headers={}, version='HTTP/1.1', auth=None, attempts=1, pool=None):

        super(Put, self).__init__(addr, args, payload, headers, 
        version, auth, attempts, pool)
        self.method = 'PUT'

class Delete(Get):
    def __init__(self, addr, args={}, headers={}, 
        version='HTTP/1.1', auth=None, attempts=1, pool=None):

        super(Delete, self).__init__(addr, args, headers, 
        version, auth, attempts, pool)

        self.method = 'DELETE'

class Head(Get):
    def __init__(self, addr, args={}, headers={}, 
        version='HTTP/1.1', auth=None, attempts=1, pool=None):

        super(Head, self).__init__(addr, args, headers, 
        version, auth, attempts, pool)

        self.method = 'HEAD'

class RequestPool(Task):
    class EMPTY(Event):
        pass

    def __init__(self):
        super(RequestPool, self).__init__()
        self.add_map(DONE, self.handle_done)
        self.responses = []
        self.errors = []
        self.start()

    def handle_done(self, task):
        self.drive(self.EMPTY)
        die()

    def register(self, request):
        self.add(request, ResponseHandle.DONE, ResponseHandle.ERROR)
        request.add_map(ResponseHandle.DONE, self.append_response)
        request.add_map(ResponseHandle.ERROR, self.append_request)

    def append_response(self, request, response):
        self.responses.append(response)

    def append_request(self, request, response, err=None):
        self.errors.append(request)

def make_method(method, addr, args, version):
    urlparser = urlparse(addr)
    resource  = urlparser.path if urlparser.path else '/'

    if args or urlparser.query:
        resource = ''.join((resource, '?', urlparser.query, urlencode(args, doseq=True)))
    if urlparser.fragment:
        resource = ''.join((resource, '#', urlparser.fragment))
    httpcmd = '%s %s %s\r\n' % (method, resource, version)
    return httpcmd.encode('ascii')

def build_headers(headers):
    data = ''
    for key, value in headers.items():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    return data.encode('ascii')
