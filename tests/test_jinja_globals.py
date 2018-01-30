import asyncio
import logging

import jinja2
import pytest
from aiohttp import web

import aiohttp_jinja2


def test_get_env(loop):
    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': "tmpl"}))

    env = aiohttp_jinja2.get_env(app)
    assert isinstance(env, jinja2.Environment)
    assert env is aiohttp_jinja2.get_env(app)


@asyncio.coroutine
def test_url(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    @asyncio.coroutine
    def other(request):
        return

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         "{{ url('other', name='John_Doe')}}"}))

    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/user/{name}', other, name='other')
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '/user/John_Doe' == txt


@asyncio.coroutine
def test_url_with_query(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         "{{ url('index', query_={'foo': 'bar'})}}"}))

    app.router.add_get('/', index, name='index')
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '/?foo=bar' == txt


@asyncio.coroutine
def test_helpers_disabled(test_client, loop):

    @asyncio.coroutine
    def index(request):
        with pytest.raises(jinja2.UndefinedError,
                           match="'url' is undefined"):
            aiohttp_jinja2.render_template('tmpl.jinja2', request, {})
        return web.Response()

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(
        app,
        default_helpers=False,
        loader=jinja2.DictLoader(
            {'tmpl.jinja2': "{{ url('index')}}"})
    )

    app.router.add_route('GET', '/', index)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status


@asyncio.coroutine
def test_static(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         "{{ static('whatever.js') }}"}))

    app['static_root_url'] = '/static'
    app.router.add_route('GET', '/', index)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '/static/whatever.js' == txt


@asyncio.coroutine
def test_static_var_missing(test_client, loop, caplog):

    @asyncio.coroutine
    def index(request):
        with pytest.raises(RuntimeError, match='static_root_url') as ctx:
            aiohttp_jinja2.render_template('tmpl.jinja2', request, {})
        return web.Response()

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         "{{ static('whatever.js') }}"}))

    app.router.add_route('GET', '/', index)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status  # static_root_url is not set
