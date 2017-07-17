# Websnake

Asynchronous http/https requests in python (for humans).

It is possible to fire multiple http/https requests asynchronously with websnake. 

# Features

- **Http/Https**

- **Easy to play :P**

- **GET/POST requests**

- **Basic AUTH support**

- **Non-blocking I/O**

In Websnake HTTP response's code turn into events, in this way it is possible to keep track of what is going
on with your request in an simple manner. The fact of being capable of mapping a handle to a specific
HTTP response it makes applications on top of Websnake more modular.

### Basic GET Request

The following example just fire three requests and wait for the response to be printed.

~~~python
from websnake import ContextGet, core

def create_connection(addr):
    # The ContextGet automatically handles redirects.
    request = ContextGet(addr)
    
    # Get on_done handle only when '200' HTTP response happens.
    # The request.con is merely a Spin instance.
    # See: https://github.com/iogf/untwisted
    request.add_map('200', on_done)

def on_done(request, con, response):
    # The response details.
    print response.headers

    # The response code in this case '200'.
    print response.code

    # The protocol version.
    print response.version

    # The text reason.
    print response.reason 
    
    # The response body.
    print response.fd.read()

if __name__ == '__main__':
    urls = ('https://www.google.com.br/', 
    'https://www.github.com/', 'https://news.ycombinator.com/')

    for ind in urls:
        create_connection(ind)
    core.gear.mainloop()

~~~

### Basic POST Request

The example below creates a simple gist on github.

~~~python

from websnake import ContextPost, ResponseHandle, core
import json

def on_done(request, con, response):
    print response.fd.read()

def create():
    payload = {
    "description": "the description for this gist",
    "public": "true", "files": {
    "file1.txt": {"content": "String file contents"}}}

    request = ContextPost('https://api.github.com/gists',      
    payload=json.dumps(payload), 
    headers={'content-type': 'application/json'})

    # Regardless of the status code it calls on_done.
    request.add_map(ResponseHandle.DONE, on_done)

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





