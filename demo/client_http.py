from websnake import Get, ResponseHandle, core, die

def on_response(con, response):
    print(response.headers)
    print(response.code)
    print(response.version)
    print(response.reason) 
    print(response.fd.read())
    die()

if __name__ == '__main__':
    request = Get('http://codepad.org/')
    request.add_map(ResponseHandle.RESPONSE, on_response)
    core.gear.mainloop()




