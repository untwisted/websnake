from websnake import Put, ResponseHandle, core, die, FormData, TokenAuth

def on_done(con, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.fd.read())
    die()

if __name__ == '__main__':
    url = 'http://httpbin.org/put'
    data = {'somekey': 'somevalue'}

    request = Put(url, payload=FormData(data))

    request.add_map(ResponseHandle.DONE, on_done)
    core.gear.mainloop()


