from websnake import get, ResponseHandle, core, die

def on_done(con, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())
    die()

if __name__ == '__main__':
    con = get('http://codepad.org/')
    con.add_map(ResponseHandle.DONE, on_done)
    core.gear.mainloop()




