import jinja2
from aiohttp import web

import aiohttp_jinja2


async def test_context_processors(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'bar': 2}

    app = web.Application(middlewares=[
            aiohttp_jinja2.context_processors_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         'foo: {{ foo }}, bar: {{ bar }}, path: {{ request.path }}'}))

    async def processor(request):
        return {'foo': 1,
                'bar': 'should be overwriten'}

    app['aiohttp_jinja2_context_processors'] = (
        aiohttp_jinja2.request_processor,
        processor,
    )

    app.router.add_get('/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt


async def test_nested_context_processors(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'bar': 2}

    subapp = web.Application(middlewares=[
            aiohttp_jinja2.context_processors_middleware])
    aiohttp_jinja2.setup(subapp, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         'foo: {{ foo }}, bar: {{ bar }}, '
         'baz: {{ baz }}, path: {{ request.path }}'}))

    async def subprocessor(request):
        return {'foo': 1,
                'bar': 'should be overwriten'}

    subapp['aiohttp_jinja2_context_processors'] = (
        aiohttp_jinja2.request_processor,
        subprocessor,
    )

    subapp.router.add_get('/', func)

    app = web.Application(middlewares=[
            aiohttp_jinja2.context_processors_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({}))

    async def processor(request):
        return {'baz': 5}

    app['aiohttp_jinja2_context_processors'] = (
        aiohttp_jinja2.request_processor,
        processor,
    )

    app.add_subapp('/sub/', subapp)

    client = await aiohttp_client(app)

    resp = await client.get('/sub/')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'foo: 1, bar: 2, baz: 5, path: /sub/' == txt


async def test_context_is_response(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        raise web.HTTPForbidden()

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': "template"}))

    app.router.add_route('GET', '/', func)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 403 == resp.status


async def test_context_processors_new_setup_style(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'bar': 2}

    async def processor(request):
        return {'foo': 1,
                'bar': 'should be overwriten'}

    app = web.Application()
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader(
            {'tmpl.jinja2':
             'foo: {{ foo }}, bar: {{ bar }}, '
             'path: {{ request.path }}'}),
        context_processors=(aiohttp_jinja2.request_processor,
                            processor)
    )

    app.router.add_route('GET', '/', func)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt


async def test_context_not_tainted(aiohttp_client):

    global_context = {'version': 1}

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return global_context

    async def processor(request):
        return {'foo': 1}

    app = web.Application()
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({'tmpl.jinja2': 'foo: {{ foo }}'}),
        context_processors=[processor])

    app.router.add_get('/', func)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'foo: 1' == txt

    assert 'foo' not in global_context
