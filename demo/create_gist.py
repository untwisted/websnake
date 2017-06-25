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

