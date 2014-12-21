import asyncio
import socket
import unittest
import aiohttp
from aiohttp import web
import aiohttp_jinja2
import jinja2


class TestSimple(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        self.loop.close()

    def find_unused_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def test_func(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def func(request, response):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            srv = yield from self.loop.create_server(
                app.make_handler(), '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_meth(self):

        class Handler:

            @aiohttp_jinja2.template('tmpl.jinja2')
            @asyncio.coroutine
            def meth(self, request, response):
                return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            handler = Handler()
            app.router.add_route('GET', '/', handler.meth)

            port = self.find_unused_port()
            srv = yield from self.loop.create_server(
                app.make_handler(), '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())
