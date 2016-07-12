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
                                            headers, [], False, False)
        self.payload = mock.Mock()
        self.transport = mock.Mock()
        self.writer = mock.Mock()
        req = web.Request(app, message, self.payload,
                          self.transport, self.writer, 15)
        return req

    @asyncio.coroutine
    def _create_app_with_template(self, template, func):
        """
        Helper method that creates application with single handler that process
        request to root '/' with any http method and returns response for
        rendered `template`
        """
        app = web.Application(loop=self.loop)
        aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
            'tmpl.jinja2': template
        }))

        app.router.add_route('*', '/', func)

        port = self.find_unused_port()
        handler = app.make_handler()
        srv = yield from self.loop.create_server(
            handler, '127.0.0.1', port)
        url = 'http://127.0.0.1:{}/'.format(port)

        resp = yield from aiohttp.request('GET', url, loop=self.loop)

        yield from handler.finish_connections()
        srv.close()
        self.addCleanup(srv.close)

        return resp

    def test_func(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def func(request):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            resp = yield from self._create_app_with_template(template, func)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

        self.loop.run_until_complete(go())

    def test_render_class_based_view(self):
        class MyView(web.View):
            @aiohttp_jinja2.template('tmpl.jinja2')
            @asyncio.coroutine
            def get(self):
                return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            resp = yield from self._create_app_with_template(template, MyView)

            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

        self.loop.run_until_complete(go())

    def test_meth(self):

        class Handler:

            @aiohttp_jinja2.template('tmpl.jinja2')
            @asyncio.coroutine
            def meth(self, request):
                return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            handler = Handler()

            resp = yield from self._create_app_with_template(template,
                                                             handler.meth)

            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

        self.loop.run_until_complete(go())

    def test_convert_func_to_coroutine(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        def func(request):
            return {'head': 'HEAD', 'text': 'text'}

        @asyncio.coroutine
        def go():
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            resp = yield from self._create_app_with_template(template, func)

            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

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
                  "call aiohttp_jinja2.setup(..., app_key={}" \
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
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            resp = yield from self._create_app_with_template(template, func)

            self.assertEqual(201, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

        self.loop.run_until_complete(go())

    def test_render_template(self):

        @asyncio.coroutine
        def func(request):
            return aiohttp_jinja2.render_template(
                'tmpl.jinja2', request,
                {'head': 'HEAD', 'text': 'text'})

        @asyncio.coroutine
        def go():
            template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

            resp = yield from self._create_app_with_template(template, func)
            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><h1>HEAD</h1>text</body></html>',
                             txt)

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
                {'tmpl.jinja2': 'tmpl'}))

            app.router.add_route('GET', '/', func)

            req = self.make_request(app, 'GET', '/')
            msg = "context should be mapping, not <class 'int'>"
            with self.assertRaisesRegex(web.HTTPInternalServerError,
                                        re.escape(msg)) as ctx:
                yield from func(req)

            self.assertEqual(msg, ctx.exception.text)

        self.loop.run_until_complete(go())

    def test_render_without_context(self):

        @aiohttp_jinja2.template('tmpl.jinja2')
        def func(request):
            pass

        @asyncio.coroutine
        def go():
            template = '<html><body><p>{{text}}</p></body></html>'

            resp = yield from self._create_app_with_template(template, func)

            self.assertEqual(200, resp.status)
            txt = yield from resp.text()
            self.assertEqual('<html><body><p></p></body></html>',
                             txt)

        self.loop.run_until_complete(go())
