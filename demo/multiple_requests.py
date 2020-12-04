"""
"""

from websnake import Get, ResponseHandle, core, RequestPool, die

def handle_done(request, response):
    print('Headers:', response.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 

def handle_empty(pool):
    print('All requests done!')
    die('Stopping...')

if __name__ == '__main__':
    urls = ('https://en.wikipedia.org/wiki/Leonhard_Euler', 
    'https://www.google.com.br','https://facebook.com/') 

    pool = RequestPool()
    pool.add_map(RequestPool.EMPTY, handle_empty)

    for ind in urls:
        Get(ind, pool=pool).add_map(ResponseHandle.DONE, handle_done)
    core.gear.mainloop()

