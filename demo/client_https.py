"""
Overview
========

Retrieve user data from github.

"""

from websnake import get, ResponseHandle
from untwisted.network import xmap, core

def on_done(con, response):
    print response.headers
    print response.code
    print response.version
    print response.reason 
    print response.fd.read()

if __name__ == '__main__':
    con = get('https://api.github.com', '/user', 
    auth=('iogf', 'godhelpsme'))

    xmap(con, ResponseHandle.DONE, on_done)
    core.gear.mainloop()


