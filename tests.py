from websnake import Head, ResponseHandle, core, die, \
FormData, TokenAuth, Get, Post, Put, Delete, default_headers, Headers,\
BasicAuth, TokenAuth
from urllib.parse import urlencode, urlparse
import unittest
import json

class TestGet0(unittest.TestCase):
    def setUp(self):
        url = 'http://httpbin.org/get'
        self.args = {'key0': 'value0', 'key1': 'value2'}

        self.request = Get(url, args=self.args)
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = json.loads(response.content())

        self.assertTrue(response_data['args'], self.args)
        die()

    def test_get(self):
        core.gear.mainloop()

class TestGet1(unittest.TestCase):
    def setUp(self):
        url = 'https://httpbin.org/get'

        auth = BasicAuth('username', 'foobar')
        self.request = Get(url, auth=auth)
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = response.content()
        response_data = json.loads(response_data)
        authorization = response_data['headers']['Authorization']
        self.assertEqual(authorization, request.headers['authorization'])
        die()

    def test_get(self):
        core.gear.mainloop()

class TestGet2(unittest.TestCase):
    def setUp(self):
        self.url = 'https://httpbin.org/get?e=1&u=2'

        auth = TokenAuth('fooobar')
        self.request = Get(self.url, auth=auth)
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = response.content()
        response_data = json.loads(response_data)
        self.assertEqual(self.url, response_data['url'])
        die()

    def test_get(self):
        core.gear.mainloop()

class TestPost0(unittest.TestCase):
    def setUp(self):
        self.url = 'https://httpbin.org/post'
        self.args = {'key0': 'value0', 'key1': 'value2'}

        self.request = Post(self.url, args=self.args)
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = json.loads(response.content())

        self.assertTrue(response_data['args'], self.args)
        die()

    def test_get(self):
        core.gear.mainloop()

class TestPost1(unittest.TestCase):
    def setUp(self):
        self.url = 'https://httpbin.org/post'
        self.data = {'key0': 'value0', 'key1': 'value2'}

        self.request = Post(self.url, payload=FormData(self.data))
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = json.loads(response.content())

        self.assertTrue(response_data['form'], self.data)
        die()

    def test_get(self):
        core.gear.mainloop()

class TestPost2(unittest.TestCase):
    def setUp(self):
        self.url = 'https://httpbin.org/post'
        self.data = {'key0': 'value0', 'key1': 'value2'}
        self.args = {'key0': 'value0', 'key1': 'value2'}

        self.request = Post(self.url, args=self.args, payload=FormData(self.data))
        self.request.add_map(ResponseHandle.DONE, self.handle_done)
    
    def handle_done(self, request, response):
        response_data = json.loads(response.content())

        self.assertTrue(response_data['form'], self.data)
        self.assertTrue(response_data['args'], self.args)

        url = '%s?%s' % (self.url, urlencode(self.args))
        self.assertTrue(response_data['url'], url)

        die()

    def test_get(self):
        core.gear.mainloop()

