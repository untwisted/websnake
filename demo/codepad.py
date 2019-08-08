"""
Overview
========

Post some source code onto codepad.org

Example:

    python2 codepad.py -f file.py

"""
from __future__ import print_function

from websnake import ResponseHandle, post, urlencode
from untwisted.network import Spin, xmap, core, die
import argparse

def on_done(spin, response):
    print('URL:%s' % response.headers['location'])
    die()

def create_post(filename, run=True, type='Plain Text'):
    fd   = open(args.filename, 'r')
    code = fd.read()
    fd.close()

    payload = {'code':code,
    'lang':' '.join([ind.capitalize() for ind in type.split(' ')]),
    'submit':'Submit',
    'run': run}
    
    headers={'cookie':('__utmz=106200'
    '593.1546731793.1.1.utmcsr=(direct)'
    'utmccn=(direct)|utmcmd=(none); __utma=106200593.112'
    '2846840.1546731793.1561916276.1565289788.8; __utmc=106200593;'
    'codepad-session=8cee1945a8158b2ad5c57921d6862496f4338799ec8c59042479bf972e9a92199dd18a42;'
    '__utmb=106200593.6.10.1565289788').join('')}

    con = post('http://codepad.org/', payload=urlencode(payload).encode('utf8'), headers=headers)
    xmap(con, ResponseHandle.DONE, on_done)

if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',  default='0.0.0.0', help='filename')
    parser.add_argument('-t', '--type',  default='Plain Text', 
                                help='Type should be Python, Haskell, etc..')
    parser.add_argument('-r', '--run',  action='store_true', help='run')
    args = parser.parse_args()

    create_post(args.filename, args.run, args.type)
    core.gear.mainloop()




