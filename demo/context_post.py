"""
Overview
========

Create an anonymous gist on github.

"""

from websnake import ContextPost, ResponseHandle, core
import json

def on_done(request, con, response):
    print(response.fd.read())

def create():
    payload = {
    "description": "the description for this gist",
    "public": "true", "files": {
    "file1.txt": {"content": "String file contents"}}}

    request = ContextPost('https://api.github.com/gists',      
    payload=json.dumps(payload).encode('utf8'), 
    headers={'content-type': 'application/json'})

    # Regardless of the status code it calls on_done.
    request.add_map(ResponseHandle.DONE, on_done)

if __name__ == '__main__':
    create()
    core.gear.mainloop()







