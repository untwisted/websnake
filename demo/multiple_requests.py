"""
"""

from websnake import Get, ResponseHandle, core, RequestPool, die

def handle_empty(pool):
    print('All requests done!')

    for ind in pool.responses:
        print('Code:', ind.code)
    die()

if __name__ == '__main__':
    urls = ('https://en.wikipedia.org/wiki/Leonhard_Euler', 
    'https://www.google.com.br/','https://facebook.com/') 

    pool = RequestPool()
    pool.add_map(RequestPool.EMPTY, handle_empty)

    for ind in urls:
        request = Get(ind, pool=pool)
    core.gear.mainloop()

