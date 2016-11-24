import asyncio

import jinja2
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

import aiohttp_jinja2


@asyncio.coroutine
def test_func(loop, test_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'
    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_render_class_based_view(loop, test_client):
    class MyView(web.View):
        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def get(self):
            return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', MyView)

    client = yield from test_client(app)

    resp = yield from client.get('/')

    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_meth(loop, test_client):

    class Handler:

        @aiohttp_jinja2.template('tmpl.jinja2')
        @asyncio.coroutine
        def meth(self, request):
            return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    handler = Handler()

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', handler.meth)

    client = yield from test_client(app)

    resp = yield from client.get('/')

    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_convert_func_to_coroutine(loop, test_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')

    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_render_not_initialized(loop):

    @asyncio.coroutine
    def func(request):
        return aiohttp_jinja2.render_template('template', request, {})

    app = web.Application(loop=loop)

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)
    msg = "Template engine is not initialized, " \
          "call aiohttp_jinja2.setup(..., app_key={}" \
          ") first".format(aiohttp_jinja2.APP_KEY)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        yield from func(req)

    assert msg == ctx.value.text


@asyncio.coroutine
def test_set_status(loop, test_client):

    @aiohttp_jinja2.template('tmpl.jinja2', status=201)
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')

    assert 201 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_render_template(loop, test_client):

    @asyncio.coroutine
    def func(request):
        return aiohttp_jinja2.render_template(
            'tmpl.jinja2', request,
            {'head': 'HEAD', 'text': 'text'})

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')

    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


@asyncio.coroutine
def test_template_not_found(loop):

    @asyncio.coroutine
    def func(request):
        return aiohttp_jinja2.render_template('template', request, {})

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({}))

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        yield from func(req)

    t = "Template 'template' not found"
    assert t == ctx.value.text
    assert t == ctx.value.reason


@asyncio.coroutine
def test_render_not_mapping(loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return 123

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': 'tmpl'}))

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)
    msg = "context should be mapping, not <class 'int'>"
    with pytest.raises(web.HTTPInternalServerError) as ctx:
        yield from func(req)

    assert msg == ctx.value.text


@asyncio.coroutine
def test_render_without_context(loop, test_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    def func(request):
        pass

    template = '<html><body><p>{{text}}</p></body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': template}))

    app.router.add_route('GET', '/', func)

    client = yield from test_client(app)
    resp = yield from client.get('/')

    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><p></p></body></html>' == txt
