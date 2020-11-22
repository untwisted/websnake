"""
Overview
========

Retrieve user data from github.

"""

from websnake import Get, ResponseHandle, core

def on_done(request, response):
    print('Request done!')

def on_response(request, response):
    print('Request response!')

    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Body:', response.fd.read())

if __name__ == '__main__':
    request = Get('https://www.bol.com.br/')
    
    request.add_map(ResponseHandle.DONE, on_done)
    request.add_map(ResponseHandle.RESPONSE, on_response)
    core.gear.mainloop()







