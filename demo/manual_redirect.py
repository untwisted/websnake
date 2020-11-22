from websnake import Get, ResponseHandle, die
from untwisted import core
from untwisted.client import lose

def on_done(request, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())
    die()

def create_connection(addr):
    hredir = lambda con, response: \
    create_connection(response.headers['location'])

    con = get(addr)
    con.add_map('200', on_done)
    con.add_map('400', on_done)

    con.add_map('302', hredir)
    con.add_map('301', hredir)
    return con

if __name__ == '__main__':

    con = create_connection('https://www.google.com.br/')
    core.gear.mainloop()





