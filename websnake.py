from untwisted.client import lose, create_client, create_client_ssl
from urllib.parse import urlencode, urlparse
from untwisted.splits import AccUntil, TmpFile
from untwisted.dispatcher import Dispatcher
from untwisted.event import Event, SSL_CONNECT, CLOSE, CONNECT
from base64 import encodebytes
from tempfile import TemporaryFile 
from socket import getservbyname
from untwisted.core import die
from untwisted import core

default_headers = {
'user-agent':'Websnake/1.0.0', 
'accept-charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
'connection':'close'}

class Headers(dict):
    def __init__(self, data):
        for ind in data:
            field, sep, value = ind.partition(':')
            self[field.lower()] = value

    # def get(self, key, default):
        # pass

class ResponseHandle:
    class DONE(Event):
        pass

    class ERROR(Event):
        pass

    class RESPONSE(Event):
        pass

    MAX_SIZE = 1024 * 1024
    def __init__(self, request):
        self.request = request
        self.response = None

        self.acc = AccUntil(request.con)
        self.tmpfile = TmpFile(request.con)

        request.con.add_map(AccUntil.DONE, self.handle_terminator)
        request.con.add_map(TmpFile.DONE,  self.handle_bdata)
        request.con.add_map(CLOSE,  self.handle_close)
        self.acc.start()

    def handle_terminator(self, con, header, bdata):
        """
        """

        self.response = Response(header)
        size = self.response.headers.get('content-length', 0)
        size = int(size)
        self.tmpfile.start(self.response.fd, size, bdata)
        # if self.MAX_SIZE <= size:
            # request.drive(self.ERROR, response, 'Content-length too long.')
        # else:

    def handle_bdata(self, con, fd, data):
        fd.seek(0)

        self.request.drive(self.response.code, self.response)
        self.request.drive(ResponseHandle.RESPONSE, self.response)

        location = self.response.headers.get('location')
        if location is not None:
            self.request.redirect(location)
        else:
            self.request.drive(self.DONE, self.response)

    def handle_close(self, con, err):
        print('Close')

class Response:
    def __init__(self, data):
        data     = data.decode('utf8').split('\r\n')
        response = data.pop(0)
        code     = response.split(' ', 2)

        self.version = code[0]
        self.code    = code[1]
        self.reason  = code[2]

        self.headers = Headers(data)
        self.fd = TemporaryFile('w+b')

class Request(Dispatcher):
    def __init__(self, addr, headers, version, auth):
        self.headers = default_headers.copy()
        self.version = version
        self.auth = auth

        self.headers.update(headers)
        if auth: 
            self.headers['authorization'] = build_auth(*auth)

        self.con = self.connect(addr)
        super(Request, self).__init__()

    def on_connect(self, con):
        pass

    def create_con_ssl(self, addr, port):
        con = create_client_ssl(addr, port)  
        con.add_map(SSL_CONNECT,  self.on_connect)
        return con
    
    def create_con(self, addr, port):
        con = create_client(addr, port)
        con.add_map(CONNECT,  self.on_connect)
        return con

    def connect(self, addr):
        self.addr = addr.strip()
        self.addr = self.addr.rstrip()
        urlparser = urlparse(self.addr)

        port = urlparser.port
        if not port:
            port = getservbyname(urlparser.scheme)

        # The hostname has to be here in case of redirect.
        self.headers['host'] = urlparser.hostname
        if urlparser.scheme == 'https':
            return self.create_con_ssl(urlparser.hostname, port)
        return self.create_con(urlparser.hostname, port)
    
    def redirect(self, addr):
        self.con = self.connect(addr)

class Get(Request):
    def __init__(self, addr, args={}, 
        headers={}, version='HTTP/1.1', auth=()):

        self.args = args
        super(Get, self).__init__(addr, headers, version, auth)

    def on_connect(self, con):
        ResponseHandle(self)
        urlparser = urlparse(self.addr)
        resource  = ''

        resource = urlparser.path
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
        headers={}, version='HTTP/1.1', auth=()):

        self.payload = payload
        super(Post, self).__init__(addr, headers, version, auth)

    def on_connect(self, con):
        ResponseHandle(self)

        urlparser = urlparse(self.addr)

        request_text = 'POST %s %s\r\n' % (urlparser.path, self.version)
        headers_text = build_headers(self.headers)
        request_text = request_text + headers_text 
        request_text = request_text.encode('ascii') + self.payload
    
        con.dump(request_text)
    
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
