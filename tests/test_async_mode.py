import asyncio

import jinja2
import aiohttp_jinja2
from aiohttp import web


@asyncio.coroutine
def test_async_mode_disabled(test_client, loop):
    """
    Test that running in blocking manner will also work.
    """
    @aiohttp_jinja2.template('tmpl.jinja2')
    @asyncio.coroutine
    def func(request):
        return {'foo': 42}

    app = web.Application(loop=loop)
    template = "foo: {{foo}}"
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.DictLoader({
            'tmpl.jinja2': template,
        }),
        enable_async=False,
    )

    app.router.add_get('/', func)

    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'foo: 42' == txt
