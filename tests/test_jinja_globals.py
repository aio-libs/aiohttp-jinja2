import asyncio

import jinja2
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
         "{{ url('other', parts={'name': 'John_Doe'})}}"}))

    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/user/{name}', other, name='other')
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '/user/John_Doe' == txt
