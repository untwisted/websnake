# Websnake

Asynchronous web requests in python.

It is possible to fire multiple http/https requests asynchronously with websnake. 

### Basic GET Request

~~~python
"""
A simple crawler.
"""

from websnake import get, ResponseHandle
from untwisted.network import xmap, core
import sys

def on_done(con, response):
    print response.headers
    print response.code
    print response.version
    print response.reason 
    print response.fd.read()

def create_connection(addr):
    headers = {
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) \
     AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 
    'accept-charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7'}

    redirect = lambda con, response: \
    create_connection(response.headers['location'])

    con = get(addr, headers=headers)
    xmap(con, '200', on_done)
    xmap(con, '302', redirect)
    xmap(con, '301', redirect)

    return con

if __name__ == '__main__':

    con = create_connection(sys.argv[1])

    core.gear.mainloop()
~~~

~~~python

"""
Overview
========

Create an anonymous gist on github.

"""

from websnake import post, ResponseHandle
from untwisted.network import xmap, core
import json

def on_done(con, response):
    print response.fd.read()

def create():
    payload = {
    "description": "the description for this gist",
    "public": "true", "files": {
    "file1.txt": {"content": "String file contents"}}}

    con = post('https://api.github.com/gists',      
    payload=json.dumps(payload), 
    headers={'content-type': 'application/json'})

    xmap(con, ResponseHandle.DONE, on_done)

if __name__ == '__main__':
    create()
    core.gear.mainloop()


~~~

# install

~~~
pip2 install -r requirements.txt
pip2 install websnake
~~~

# Documentation


[Wiki](https://github.com/iogf/websnake/wiki)




