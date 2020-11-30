from untwisted.client import lose, create_client, create_client_ssl
from urllib.parse import urlencode, urlparse
from untwisted.task import Task, DONE
from untwisted.splits import AccUntil, TmpFile
from untwisted.dispatcher import Dispatcher
from untwisted.event import Event, SSL_CONNECT, SSL_CONNECT_ERR, CLOSE, CONNECT, CONNECT_ERR
from base64 import encodebytes
from tempfile import TemporaryFile 
from socket import getservbyname
from untwisted.core import die
from untwisted import core

default_headers = {
'user-agent':'Websnake/1.0.0', 
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
        for ind in data:
            field, sep, value = ind.partition(':')
            self.headers[field.lower()] = value

    def get(self, field, default=None):
        field = field.lower()
        return self.headers.get(field, default)

    def update(self, other):
        for ind in other.headers.items():
            self.headers[ind[0].lower()] = ind[1]

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

        if self.MAX_SIZE <= size:
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
        data = data.decode('utf8').split('\r\n')
        response = data.pop(0)
        code = response.split(' ', 2)

        self.version = code[0]
        self.code    = code[1]
        self.reason  = code[2]
        self.headers = Headers(data)
        self.fd = TemporaryFile('w+b')

class Request(Dispatcher):
    def __init__(self, addr, headers, version, auth, attempts=1, pool=None):
        super(Request, self).__init__()

        self.headers    = default_headers.copy()
        self.version    = version
        self.attempts   = attempts
        self.c_attempts = 0

        self.auth = auth
        self.addr = addr
        self.pool = pool

        self.headers.update(headers)
        if auth: 
            self.headers['authorization'] = build_auth(*auth)

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
        self.c_attempts += 1

        # The hostname has to be here in case of redirect.
        self.headers['host'] = urlparser.hostname
        if urlparser.scheme == 'https':
            return self.create_con_ssl(urlparser.hostname, port)
        return self.create_con(urlparser.hostname, port)
    
    def redirect(self, addr):
        self.con = self.connect(addr)

class Get(Request):
    def __init__(self, addr, args={}, 
        headers={}, version='HTTP/1.1', auth=(), attempts=1, pool=None):

        self.args = args
        super(Get, self).__init__(addr, headers, version, auth, attempts, pool)

    def handle_connect(self, con):
        ResponseHandle(self)
        urlparser = urlparse(self.addr)
        resource  = ''
        resource  = urlparser.path

        if self.args or urlparser.query:
            resource = ''.join(resource, 
                '?', urlparser.query, urlencode(self.args))
        
        request_text = 'GET %s %s\r\n' % (resource, self.version)
        headers_text = build_headers(self.headers)
        request_text = request_text + headers_text
        request_text = request_text.encode('ascii')
        con.dump(request_text)

class Post(Request):
    def __init__(self, addr, payload='b', 
        headers={}, version='HTTP/1.1', auth=(), pool=None):

        self.payload = payload
        super(Post, self).__init__(addr, headers, version, auth, pool)

    def handle_connect(self, con):
        ResponseHandle(self)

        urlparser    = urlparse(self.addr)
        request_text = 'POST %s %s\r\n' % (urlparser.path, self.version)
        headers_text = build_headers(self.headers)
        request_text = request_text + headers_text 
        request_text = request_text.encode('ascii') + self.payload
    
        con.dump(request_text)
    
class RequestPool(Task):
    class EMPTY(Event):
        pass

    def __init__(self):
        super(RequestPool, self).__init__()
        self.add_map(DONE, self.handle_done)
        self.responses = []

    def handle_done(self, task):
        self.drive(self.EMPTY)
        die()

    def register(self, request):
        self.add(request, ResponseHandle.DONE, ResponseHandle.ERROR)
        request.add_map(ResponseHandle.DONE, self.append_response)
        request.add_map(ResponseHandle.ERROR, self.append_response)

    def append_response(self, request, response, err=None):
        self.responses.append(response)

    def run(self):
        self.start()
        core.gear.mainloop()
        return self.responses

def build_headers(headers):
    data = ''
    for key, value in headers.items():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    return data

def build_auth(username, password):
    username = username.encode('utf8')
    password = password.encode('utf8')

    base = encodebytes(b'%s:%s' % (username, password))
    base = base.replace(b'\n', b'').decode('utf8')
    return "Basic %s" % base
