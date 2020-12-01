"""
Overview
========

Create an anonymous gist on github.

"""

from websnake import Post, ResponseHandle
from untwisted.network import core
from untwisted.core import die
import json

def on_done(con, response):
    print(response.fd.read())
    die()

if __name__ == '__main__':
    API_TOKEN = ''
    payload = {
    "description": "the description for this gist1",
    "public": "true", "files": {
    "file1.txt": {"content": "String file contents"}}}


    request = Post('https://api.github.com/gists',
    payload=json.dumps(payload).encode('utf8'), 
    headers={'content-type': 'application/json',
    'authorization': 'token %s' % API_TOKEN})

    request.add_map(ResponseHandle.DONE, on_done)

    core.gear.mainloop()




