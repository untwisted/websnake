from websnake import Post, ResponseHandle, core, die, FormData, TokenAuth

def on_done(con, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.fd.read())
    die()

if __name__ == '__main__':
    url = 'http://httpbin.org/post'
    data = {'somekey': 'somevalue'}

    request = Post(url, payload=FormData(data))

    request.add_map(ResponseHandle.DONE, on_done)
    core.gear.mainloop()

