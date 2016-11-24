import asyncio

import jinja2
from aiohttp import web

import aiohttp_jinja2


@asyncio.coroutine
def test_jinja_filters(test_client, loop):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def index(request):
        return {}

    def add_2(value):
        return value + 2

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({'tmpl.jinja2': "{{ 5|add_2 }}"}),
        filters={'add_2': add_2}
    )

    app.router.add_route('GET', '/', index)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '7' == txt
