from websnake import get, ResponseHandle, TransferHandle
from untwisted.network import xmap, core
from untwisted.event import CONNECT_ERR, CONNECT, WRITE, CLOSE,  SSL_CONNECT, DUMPED, SSL_SEND_ERR, SSL_CERTIFICATE_ERR, SSL_CONNECT_ERR
import sys

def on_done(con, response):
    print 'on_done', response.code

def on_response_handle_done(con, response):
    print response.code

def on_transfer_handle_done(con, response, data):
    print 'on transfer response', response.headers

def on_ssl_connect_err(*args):
    print 'on ssl connect err'

def on_dumped(*args):
    print 'on dumped request'

def on_send_err_ssl(*args):
    print 'on send err ssl'

def on_ssl_certificate_err(*args):
    print 'on ssl certificate err'

def on_close(*args):
    print 'on close'

def on_connect(*args):
    print 'connected'

def on_ssl_connect(*args):
    print 'on ssl connect'

def on_ssl_connect_err(*args):
    print 'connect err'

def on_write(*args):
    print 'on_write'

def on_redirect(con, response):
    con = create_connection(response.headers['location'])
    print 'on redirect', response.code, response.headers

def create_connection(addr):
    headers = {
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 
    'accept-charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}

    con = get(addr, headers=headers)
    xmap(con, TransferHandle.DONE, on_transfer_handle_done)
    xmap(con, ResponseHandle.DONE, on_response_handle_done)

    xmap(con, '200', on_done)
    xmap(con, '302', on_redirect)
    xmap(con, '301', on_redirect)
    xmap(con, CLOSE, on_close)
    xmap(con, CONNECT, on_connect)
    xmap(con, SSL_CONNECT, on_ssl_connect)
    xmap(con, SSL_CONNECT_ERR, on_ssl_connect_err)

    xmap(con, DUMPED, on_dumped)
    xmap(con, SSL_SEND_ERR, on_send_err_ssl)
    xmap(con, SSL_CERTIFICATE_ERR, on_ssl_certificate_err)

    return con

if __name__ == '__main__':
    con = create_connection(sys.argv[1])

    core.gear.mainloop()




