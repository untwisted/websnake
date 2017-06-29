from untwisted.iostd import LOAD, CLOSE, CONNECT, CONNECT_ERR, \
Client, Stdin, Stdout, lose, create_client
from untwisted.iossl import SSL_CONNECT, create_client_ssl
from untwisted.splits import AccUntil, TmpFile
from untwisted.network import Spin, xmap, spawn, SSL
from untwisted.event import get_event
from urllib import urlencode
from tempfile import TemporaryFile 
from urlparse import urlparse
from socket import getservbyname
import sys

class Headers(dict):
    def __init__(self, data):
        for ind in data:
            field, sep, value = ind.partition(':')
            self[field.lower()] = value

class TransferHandle(object):
    DONE = get_event()

    def __init__(self, spin):
        xmap(spin, AccUntil.DONE, lambda spin, response, data: 
        spawn(spin, TransferHandle.DONE, Response(response), data))

class ResponseHandle(object):
    DONE     = get_event()
    MAX_SIZE = 1024 * 1024

    def __init__(self, spin):
        self.response = None
        xmap(spin, TransferHandle.DONE, self.process)

    def process(self, spin, response, data):
        self.response = response

        # These handles have to be mapped here
        # otherwise it may occur of TmpFile spawning
        # done in the first cycle.
        xmap(spin, TmpFile.DONE,  lambda spin, fd, data: lose(spin))

        xmap(spin, TmpFile.DONE, 
        lambda spin, fd, data: fd.seek(0))

        xmap(spin, TmpFile.DONE,  lambda spin, fd, data: 
        spawn(spin, ResponseHandle.DONE, self.response))

        TmpFile(spin, data, int(response.headers.get(
        'content-length', self.MAX_SIZE)), response.fd)

        # Reset the fd in case of the socket getting closed
        # and there is no content-length header.
        xmap(spin, CLOSE,  lambda spin, err: 
        self.response.fd.seek(0))

        # The fact of destroying the Spin instance when on TmpFile.DONE
        # doesnt warrant the CLOSE event will not be fired.
        # So it spawns ResponseHandle.DONE only if there is 
        # a content-length header.
        if not 'content-length' in response.headers:
            xmap(spin, CLOSE,  lambda spin, err: 
                spawn(spin,  ResponseHandle.DONE, self.response))

class Response(object):
    def __init__(self, data):
        data                                 = data.split('\r\n')
        response                             = data.pop(0)
        self.version, self.code, self.reason = response.split(' ', 2)
        self.headers                         = Headers(data)
        self.fd                              = TemporaryFile('a+')

class HttpCode(object):
    def __init__(self, spin):
        xmap(spin, ResponseHandle.DONE, lambda spin, response: 
            spawn(spin, response.code, response))

def on_connect(spin, request):
    AccUntil(spin)
    TransferHandle(spin)

    ResponseHandle(spin)
    HttpCode(spin)

    spin.dump(request)

def create_con_ssl(addr, port, data):
    con = create_client_ssl(addr, port)  
    xmap(con, SSL_CONNECT,  on_connect, data)
    return con

def create_con(addr, port, data):
    con = create_client(addr, port)
    xmap(con, CONNECT,  on_connect, data)
    return con

def build_headers(headers):
    data = ''
    for key, value in headers.iteritems():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    return data

def get(addr, args={},  headers={}, version='HTTP/1.1', auth=()):

    """
    It does an http/https request.
    """

    addr    = addr.strip().rstrip()
    url     = urlparse(addr)
    default = {'user-agent':"Untwisted-requests/1.0.0", 
    'accept-charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'connection':'close',
    'host': url.hostname}

    default.update(headers)
    args = '?%s' % urlencode(args) if args else ''

    if auth: default['authorization'] = build_auth(*auth)
    data = 'GET %s%s %s\r\n' % (url.path, args, version)
    data = data + build_headers(default)
    port = url.port if url.port else getservbyname(url.scheme)

    return create_con_ssl(url.hostname, port, data) \
    if url.scheme == 'https' else create_con(url.hostname, port, data)

def post(addr, payload='', version='HTTP/1.1', headers={},  auth=()):

    """
    """

    addr    = addr.strip().rstrip()
    url     = urlparse(addr)
    default = {'user-agent':"Untwisted-requests/1.0.0", 
    'accept-charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'connection':'close',
    'host': url.hostname,
    'content-type': 'application/x-www-form-urlencoded',
    'content-length': len(payload)}

    default.update(headers)

    request  = 'POST %s %s\r\n' % (url.path, version)
    if auth: default['authorization'] = build_auth(*auth)

    request = request + build_headers(default) + payload
    port    = url.port if url.port else getservbyname(url.scheme)

    return create_con_ssl(url.hostname, port, request) \
    if url.scheme == 'https' else create_con(url.hostname, port, request)

def build_auth(username, password):
    from base64 import encodestring
    base = encodestring('%s:%s' % (username, password))
    base = base.replace('\n', '')
    return "Basic %s" % base






