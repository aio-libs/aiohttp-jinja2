import asyncio

import jinja2
import aiohttp_jinja2
from aiohttp import web


@asyncio.coroutine
def test_func(loop, test_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({
            'tmpl.jinja2': template
        }),
    )

    app.router.add_route('*', '/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt
