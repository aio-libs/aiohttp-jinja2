import asyncio

import jinja2
from aiohttp import web

import aiohttp_jinja2


@asyncio.coroutine
def test_context_processors(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'bar': 2}

    app = web.Application(loop=loop, middlewares=[
            aiohttp_jinja2.context_processors_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         'foo: {{ foo }}, bar: {{ bar }}, path: {{ request.path }}'}))

    app['aiohttp_jinja2_context_processors'] = (
        aiohttp_jinja2.request_processor,
        asyncio.coroutine(
            lambda request: {'foo': 1, 'bar': 'should be overwriten'}),
    )

    app.router.add_get('/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt


@asyncio.coroutine
def test_context_is_response(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    def func(request):
        return web.HTTPForbidden()

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': "template"}))

    app.router.add_route('GET', '/', func)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 403 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_context_processors_new_setup_style(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'bar': 2}

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader(
            {'tmpl.jinja2':
             'foo: {{ foo }}, bar: {{ bar }}, '
             'path: {{ request.path }}'}),
        context_processors=(aiohttp_jinja2.request_processor,
                            asyncio.coroutine(
                                lambda request: {
                                    'foo': 1,
                                    'bar': 'should be overwriten'})))

    app.router.add_route('GET', '/', func)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt


@asyncio.coroutine
def test_context_not_tainted(test_client, loop):

    global_context = {'version': 1}

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return global_context

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({'tmpl.jinja2': 'foo: {{ foo }}'}),
        context_processors=[asyncio.coroutine(
                                lambda request: {'foo': 1})])

    app.router.add_get('/', func)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 1' == txt

    assert 'foo' not in global_context
