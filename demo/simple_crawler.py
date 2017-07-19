"""
A simple crawler.
"""
from __future__ import print_function

from websnake import get, ResponseHandle
from untwisted.network import xmap, core
import sys

def on_done(con, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())

def create_connection(addr):
    redirect = lambda con, response: \
    create_connection(response.headers['location'])

    con = get(addr)
    xmap(con, '200', on_done)
    xmap(con, '400', on_done)

    xmap(con, '302', redirect)
    xmap(con, '301', redirect)

    return con

if __name__ == '__main__':

    # con = create_connection(sys.argv[1])
    con = create_connection('https://www.google.com.br/')

    core.gear.mainloop()




