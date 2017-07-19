from __future__ import print_function
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
    print(response.headers)

    # The response code in this case '200'.
    print(response.code)

    # The protocol version.
    print(response.version)

    # The text reason.
    print(response.reason) 
    
    # The response body.
    print(response.fd.read())

if __name__ == '__main__':
    urls = ('https://www.google.com.br/', 
    'https://www.github.com/', 'https://news.ycombinator.com/')

    for ind in urls:
        create_connection(ind)
    core.gear.mainloop()




