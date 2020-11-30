"""
"""

from websnake import Get, ResponseHandle, core, RequestPool

def handle_empty(pool):
    print('All requests done!')

if __name__ == '__main__':
    urls = ('https://en.wikipedia.org/wiki/Leonhard_Euler', 
    'https://www.google.com.br','https://facebook.com') 

    pool = RequestPool()
    for ind in urls:
        request = Get(ind, pool=pool)

    pool.add_map(RequestPool.EMPTY, handle_empty)
    responses = pool.run()
    for ind in responses:
        print(ind.code)

