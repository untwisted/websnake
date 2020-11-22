"""
Overview
========

Create an anonymous gist on github.

"""

from websnake import Post, ResponseHandle
from untwisted.network import core
import json

def on_done(con, response):
    print(response.fd.read())

def create():
    payload = {
    "description": "the description for this gist1",
    "public": "true", "files": {
    "file1.txt": {"content": "String file contents"}}}


    request = Post('https://api.github.com/gists',
    payload=json.dumps(payload).encode('utf8'), 
    headers={'content-type': 'application/json',
    'authorization': ''})

    request.add_map(ResponseHandle.RESPONSE, on_done)

if __name__ == '__main__':
    create()
    core.gear.mainloop()




