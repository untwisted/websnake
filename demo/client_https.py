"""
Overview
========

Retrieve user data from github.

"""

from websnake import Get, ResponseHandle, core

def on_response(request, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())

if __name__ == '__main__':
    request = Get('https://api.github.com/user', 
    auth=('iogf', 'FuinhoSaliente'))
    
    request.add_map(ResponseHandle.RESPONSE, on_response)
    core.gear.mainloop()






