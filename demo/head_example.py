from websnake import Head, ResponseHandle, core, die, FormData, TokenAuth

def handle_done(con, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.fd.read())
    die()

if __name__ == '__main__':
    url = 'http://httpbin.org/head'
    request = Head(url)

    request.add_map(ResponseHandle.DONE, handle_done)
    core.gear.mainloop()



