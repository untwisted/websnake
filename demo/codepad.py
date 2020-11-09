"""
Overview
========

Post some source code onto codepad.org

Example:

    python2 codepad.py -f file.py

"""

from websnake import ResponseHandle, post, urlencode
from websnake import core, die
from websnake import CLOSE
import argparse

def on_done(spin, response):
    print('URL:%s' % response.headers)
    die()

def on_close(spin, err):
    print('Socket closed !')
    die()

def create_post(filename, run=True, type='Plain Text'):
    fd   = open(args.filename, 'r')
    code = fd.read()
    fd.close()

    payload = {'code':code,
    'lang':' '.join([ind.capitalize() for ind in type.split(' ')]),
    'submit':'Submit',
    'run': run}
    
    headers={}

    con = post('http://http://hilite.me/', payload=urlencode(payload).encode('utf8'), headers=headers)
    con.add_map(ResponseHandle.DONE, on_done)
    con.add_map(CLOSE, on_close)

if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',  default='0.0.0.0', help='filename')
    parser.add_argument('-t', '--type',  default='Plain Text', 
                                help='Type should be Python, Haskell, etc..')
    parser.add_argument('-r', '--run',  action='store_true', help='run')
    args = parser.parse_args()

    create_post(args.filename, args.run, args.type)
    core.gear.mainloop()




