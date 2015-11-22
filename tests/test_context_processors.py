import aiohttp
import aiohttp_jinja2
import asyncio
import jinja2
import pytest


@pytest.mark.run_loop
def test_context_processors(create_server, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'bar': 2}

    app, url = yield from create_server(
        middlewares=[
            aiohttp_jinja2.context_processors_middleware])
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         'foo: {{ foo }}, bar: {{ bar }}, path: {{ request.path }}'}))

    app['aiohttp_jinja2_context_processors'] = (
        aiohttp_jinja2.request_processor,
        asyncio.coroutine(
            lambda request: {'foo': 1, 'bar': 'should be overwriten'}),
    )

    app.router.add_route('GET', '/', func)

    resp = yield from aiohttp.request('GET', url, loop=loop)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt


@pytest.mark.run_loop
def test_context_is_response(create_server, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    def func(request):
        return aiohttp.web_exceptions.HTTPForbidden()

    app, url = yield from create_server()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': "template"}))

    app.router.add_route('GET', '/', func)

    resp = yield from aiohttp.request('GET', url, loop=loop)
    assert 403 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_context_processors_new_setup_style(create_server, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'bar': 2}

    app, url = yield from create_server()
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

    resp = yield from aiohttp.request('GET', url, loop=loop)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 1, bar: 2, path: /' == txt
