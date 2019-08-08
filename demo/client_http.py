from websnake import get, ResponseHandle
from untwisted.network import xmap, core

def on_done(con, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())

if __name__ == '__main__':
    xmap(get('http://codepad.org/'), 
    ResponseHandle.DONE, on_done)

    core.gear.mainloop()




