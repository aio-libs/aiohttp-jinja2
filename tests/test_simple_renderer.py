import asyncio
import socket
import re
import unittest
import aiohttp
from aiohttp import web
from aiohttp.multidict import CIMultiDict
import aiohttp_jinja2
import jinja2
from unittest import mock


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

    def make_request(self, app, method, path):
        headers = CIMultiDict()
        message = aiohttp.RawRequestMessage(method, path,
                                            aiohttp.HttpVersion(1, 1),
                                            headers, False, False)
        self.payload = mock.Mock()
        self.transport = mock.Mock()
        self.writer = mock.Mock()
        req = web.Request(app, message, self.payload,
                          self.transport, self.writer, 15)
        return req

    def test_func(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def func(request):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_meth(self):

        class Handler:

            @aiohttp_jinja2.template('tmpl.jinja2')
            @asyncio.coroutine
            def meth(self, request):
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
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_convert_func_to_coroutine(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        def func(request):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_render_not_initialized(self):

        @asyncio.coroutine
        def func(request):
            return aiohttp_jinja2.render_template('template', request, {})

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)

            app.router.add_route('GET', '/', func)

            req = self.make_request(app, 'GET', '/')
            msg = "Template engine is not initialized, " \
                  "call aiohttp_jinja2.setup(app_key={}" \
                  ") first".format(aiohttp_jinja2.APP_KEY)

            with self.assertRaisesRegex(web.HTTPInternalServerError,
                                        re.escape(msg)) as ctx:
                yield from func(req)

            self.assertEqual(msg, ctx.exception.text)

        self.loop.run_until_complete(go())

    def test_set_status(self):

        @aiohttp_jinja2.template('tmpl.jinja2', status=201)
        def func(request):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(201, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_render_template(self):

        @asyncio.coroutine
        def func(request):
            return aiohttp_jinja2.render_template(
                'tmpl.jinja2', request,
                {'head': 'HEAD', 'text': 'text'})

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "<html><body><h1>{{head}}</h1>{{text}}</body></html>"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_template_not_found(self):

        @asyncio.coroutine
        def func(request):
            return aiohttp_jinja2.render_template('template', request, {})

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({}))

            app.router.add_route('GET', '/', func)

            req = self.make_request(app, 'GET', '/')

            with self.assertRaises(web.HTTPInternalServerError) as ctx:
                yield from func(req)

            self.assertEqual("Template 'template' not found",
                             ctx.exception.text)

        self.loop.run_until_complete(go())

    def test_render_not_mapping(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def func(request):
            return 123

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2': "tmpl"}))

            app.router.add_route('GET', '/', func)

            req = self.make_request(app, 'GET', '/')
            msg = "context should be mapping, not <class 'int'>"
            with self.assertRaisesRegex(web.HTTPInternalServerError,
                                        re.escape(msg)) as ctx:
                yield from func(req)

            self.assertEqual(msg, ctx.exception.text)

        self.loop.run_until_complete(go())

    def test_get_env(self):

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2': "tmpl"}))

            env = aiohttp_jinja2.get_env(app)
            self.assertIsInstance(env, jinja2.Environment)
            self.assertIs(env, aiohttp_jinja2.get_env(app))

        self.loop.run_until_complete(go())

    def test_url(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def index(request):
            return {}

        @asyncio.coroutine
        def other(request):
            return

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 "{{ url('other', parts={'name': 'John_Doe'})}}"}))

            app.router.add_route('GET', '/', index)
            app.router.add_route('GET', '/user/{name}', other, name='other')

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('/user/John_Doe', txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_context_processors(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def func(request):
            return {'bar': 2}

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop, middlewares=(
                aiohttp_jinja2.context_processors_middleware,
            ))
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2':
                 'foo: {{ foo }}, bar: {{ bar }}, path: {{ request.path }}'}))

            app['aiohttp_jinja2_context_processors'] = (
                aiohttp_jinja2.request_processor,
                asyncio.coroutine(
                    lambda request: {'foo': 1, 'bar': 'should be overwriten'}),
            )

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('foo: 1, bar: 2, path: /', txt)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())

    def test_context_is_response(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        def func(request):
            return aiohttp.web_exceptions.HTTPForbidden()

        @asyncio.coroutine
        def go():
            app = web.Application(loop=self.loop)
            aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
                {'tmpl.jinja2': "template"}))

            app.router.add_route('GET', '/', func)

            port = self.find_unused_port()
            handler = app.make_handler()
            srv = yield from self.loop.create_server(
                handler, '127.0.0.1', port)
            url = "http://127.0.0.1:{}/".format(port)

            resp = yield from aiohttp.request('GET', url, loop=self.loop)
            self.assertEqual(403, resp.status)

            yield from handler.finish_connections()
            srv.close()
            self.addCleanup(srv.close)

        self.loop.run_until_complete(go())
