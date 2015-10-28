import aiohttp
import aiohttp_jinja2
import asyncio
import jinja2
import pytest

from aiohttp import web


def test_get_env(loop):
    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': "tmpl"}))

    env = aiohttp_jinja2.get_env(app)
    assert isinstance(env, jinja2.Environment)
    assert env is aiohttp_jinja2.get_env(app)


@pytest.mark.run_loop
def test_url(create_server, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    @asyncio.coroutine
    def other(request):
        return

    app, url = yield from create_server()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2':
         "{{ url('other', parts={'name': 'John_Doe'})}}"}))

    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/user/{name}', other, name='other')

    resp = yield from aiohttp.request('GET', url, loop=loop)
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '/user/John_Doe' == txt
