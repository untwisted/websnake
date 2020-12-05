from websnake import Get, BasicAuth, ResponseHandle, core, die

def handle_response(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 

if __name__ == '__main__':
    request = Get('http://httpbin.org/get', auth=BasicAuth('foo', 'bar'))
    
    request.add_map(ResponseHandle.RESPONSE, handle_response)
    request.add_map(ResponseHandle.DONE, lambda req, resp: die('Bye!'))

    core.gear.mainloop()



