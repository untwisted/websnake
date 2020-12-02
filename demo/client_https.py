from websnake import Get, ResponseHandle, core, die

def handle_done(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.content())
    die('Request done.')

if __name__ == '__main__':
    request = Get('https://www.google.com.br/')
    
    request.add_map(ResponseHandle.DONE, handle_done)
    core.gear.mainloop()

