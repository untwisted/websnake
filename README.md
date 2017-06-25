# Websnake

Asynchronous web requests in python.

It is possible to fire multiple http/https requests asynchronously with websnake. 

**client_https.py**

~~~python
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

~~~

**create_gist.py**

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

    con = post('https://api.github.com',  
    '/gists', payload=json.dumps(payload), 
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

