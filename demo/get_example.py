from websnake import Get, ResponseHandle, core, die

def handle_response(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 

if __name__ == '__main__':
    request = Get('https://facebook.com/')
    
    request.add_map(ResponseHandle.RESPONSE, handle_response)
    request.add_map(ResponseHandle.DONE, lambda req, resp: die('Bye!'))

    core.gear.mainloop()


