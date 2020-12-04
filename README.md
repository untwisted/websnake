# Websnake

Asynchronous http/https requests in Python.

Websnake allows multiple http/https requests to be fired asynchronously.
In Websnake HTTP response's codes turn into events and handles can be binded to
HTTP response codes. 

A Web request in Websnake is an event emitter and its possible events are HTTP
response codes. That means one can have handles executed for specific HTTP status codes.

Websnake allow to fire new Web requests from response handles it makes implementing
a variety of other tools like Web Crawlers etc. 

# Features

- **Http/Https**

- **Basic Authentication support**

- **Token Authentication support**

- **Automatic Content Decoding**

- **Anti Throttle Mechanism**
    
- **Response Size Limit**

- **Non-blocking I/O**

### Multiple Requests

Websnake has a RequestPool event emitter to bind handles to be executed when specific
requests are finished. In the below example when all requests are finished it just quits.

~~~python
from websnake import Get, ResponseHandle, core, RequestPool, die

def handle_done(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 

def handle_empty(pool):
    print('All requests done!')
    die('Stopping...')

if __name__ == '__main__':
    urls = ('https://en.wikipedia.org/wiki/Leonhard_Euler', 
    'https://www.google.com.br','https://facebook.com/') 

    pool = RequestPool()
    pool.add_map(RequestPool.EMPTY, handle_empty)

    for ind in urls:
        Get(ind, pool=pool).add_map(ResponseHandle.DONE, handle_done)
    core.gear.mainloop()
~~~

### Basic GET 

The following example just makes a request and wait for the response to be printed.

~~~python
from websnake import Get, ResponseHandle, core, die

def handle_done(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.content())
    die('Request done.')

if __name__ == '__main__':
    request = Get('https://www.google.com.br/')
    
    request.add_map('200', handle_done)
    core.gear.mainloop()
~~~

Websnake requests are event emitters, you can bind a status code like '400' to a handle
then getting the handle executed when the response status code is '400'. When you don't care
for a specific HTTP response code you use ResponseHandle.DONE as event to map your handles.

### Basic POST 

The example below creates a simple gist on github.

~~~python
from websnake import Post, ResponseHandle, core, die, JSon, TokenAuth

def handle_done(con, response):
    print('Headers:', response.headers.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.content())
    die()

if __name__ == '__main__':
    data = {
    "description": "the description for this gist1",
    "public": True, "files": {
    "file1.txt": {"content": "String file contents"}}}

    request = Post('https://api.github.com/gists', args = {'scope': 'gist'},
    payload=JSon(data), auth = TokenAuth('API_TOKEN'))

    request.add_map(ResponseHandle.DONE, handle_done)
    core.gear.mainloop()
~~~

# install

**Note:** Websnake should work with python3 only.

~~~
pip install -r requirements.txt
pip install websnake
~~~

Documentation
=============

[Websnake Documentation](https://github.com/untwisted/websnake/wiki)
