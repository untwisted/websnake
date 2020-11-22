"""
Overview
========

Retrieve user data from github.

"""

from websnake import Get, ResponseHandle, core, die

def on_done(con, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())
    die()

if __name__ == '__main__':
    request = Get('https://api.github.com/user', 
    auth=('iogf', 'FuinhoSaliente'))
    
    request.add_map(ResponseHandle.RESPONSE, on_done)
    core.gear.mainloop()






