import jinja2
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

import aiohttp_jinja2


async def test_func(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_render_class_based_view(aiohttp_client):
    class MyView(web.View):
        @aiohttp_jinja2.template('tmpl.jinja2')
        async def get(self):
            return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', MyView)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_meth(aiohttp_client):

    class Handler:

        @aiohttp_jinja2.template('tmpl.jinja2')
        async def meth(self, request):
            return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    handler = Handler()

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', handler.meth)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_convert_func_to_coroutine(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_render_not_initialized():

    async def func(request):
        return aiohttp_jinja2.render_template('template', request, {})

    app = web.Application()

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)
    msg = "Template engine is not initialized, " \
          "call aiohttp_jinja2.setup(..., app_key={}" \
          ") first".format(aiohttp_jinja2.APP_KEY)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        await func(req)

    assert msg == ctx.value.text


async def test_set_status(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2', status=201)
    async def func(request):
        return {'head': 'HEAD', 'text': 'text'}

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    assert 201 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_render_template(aiohttp_client):

    async def func(request):
        return aiohttp_jinja2.render_template(
            'tmpl.jinja2', request,
            {'head': 'HEAD', 'text': 'text'})

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_render_template_custom_status(aiohttp_client):

    async def func(request):
        return aiohttp_jinja2.render_template(
            'tmpl.jinja2', request,
            {'head': 'HEAD', 'text': 'text'}, status=404)

    template = '<html><body><h1>{{head}}</h1>{{text}}</body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({
        'tmpl.jinja2': template
    }))

    app.router.add_route('*', '/', func)

    client = await aiohttp_client(app)

    resp = await client.get('/')

    assert 404 == resp.status
    txt = await resp.text()
    assert '<html><body><h1>HEAD</h1>text</body></html>' == txt


async def test_template_not_found():

    async def func(request):
        return aiohttp_jinja2.render_template('template', request, {})

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader({}))

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)

    with pytest.raises(web.HTTPInternalServerError) as ctx:
        await func(req)

    t = "Template 'template' not found"
    assert t == ctx.value.text
    assert t == ctx.value.reason


async def test_render_not_mapping():

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return 123

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': 'tmpl'}))

    app.router.add_route('GET', '/', func)

    req = make_mocked_request('GET', '/', app=app)
    msg = "context should be mapping, not <class 'int'>"
    with pytest.raises(web.HTTPInternalServerError) as ctx:
        await func(req)

    assert msg == ctx.value.text


async def test_render_without_context(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        pass

    template = '<html><body><p>{{text}}</p></body></html>'

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': template}))

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><body><p></p></body></html>' == txt


async def test_render_default_is_autoescaped(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'text': '<script>alert(1)</script>'}

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': '<html>{{text}}</html>'}))

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html>&lt;script&gt;alert(1)&lt;/script&gt;</html>' == txt


async def test_render_can_disable_autoescape(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return {'text': '<script>alert(1)</script>'}

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': '<html>{{text}}</html>'}), autoescape=False)

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert '<html><script>alert(1)</script></html>' == txt


async def test_render_bare_funcs_deprecated(aiohttp_client):

    def wrapper(func):
        async def wrapped(request):
            with pytest.warns(DeprecationWarning,
                              match='Bare functions are deprecated'):
                return await func(request)
        return wrapped

    @wrapper
    @aiohttp_jinja2.template('tmpl.jinja2')
    def func(request):
        return {'text': 'OK'}

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': '{{text}}'}))

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert 'OK' == txt


async def test_skip_render_for_response_from_handler(aiohttp_client):

    @aiohttp_jinja2.template('tmpl.jinja2')
    async def func(request):
        return web.Response(text='OK')

    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.DictLoader(
        {'tmpl.jinja2': '{{text}}'}))

    app.router.add_route('GET', '/', func)

    client = await aiohttp_client(app)
    resp = await client.get('/')

    assert 200 == resp.status
    txt = await resp.text()
    assert 'OK' == txt
