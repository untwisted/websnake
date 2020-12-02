"""
Overview
========

Create an anonymous gist on github.

"""

from websnake import Post, ResponseHandle, core, die, JSon, TokenAuth

def on_done(con, response):
    print('Headers:', response.headers.headers)
    print('Code:', response.code)
    print('Version:', response.version)
    print('Reason:', response.reason) 
    print('Data:', response.fd.read())
    die()

if __name__ == '__main__':
    data = {
    "description": "the description for this gist1",
    "public": True, "files": {
    "file1.txt": {"content": "String file contents"}}}

    request = Post('https://api.github.com/gists', args = {'scope': 'gist'},
    payload=JSon(data), auth = TokenAuth('API_TOKEN'))

    request.add_map(ResponseHandle.DONE, on_done)
    core.gear.mainloop()




