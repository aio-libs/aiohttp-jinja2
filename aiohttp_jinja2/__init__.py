__version__ = '0.1.0a'

import asyncio
import functools
import inspect
import jinja2
from aiohttp import web


__all__ = ('setup', 'get_env', 'render')


APP_KEY = 'aiohttp_jinja2_environment'


def setup(app, *args, **kwargs):
    env = jinja2.Environment(*args, **kwargs)
    app[APP_KEY] = env
    return env


def get_env(app):
    return app.get(APP_KEY)


def render(template_name, encoding='utf-8'):

    def wrapper(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError("func should be coroutine")
        sig = inspect.signature(func)
        try:
            sig.bind(object(), object(), object())
            return make_method_wrapper(func)
        except TypeError:
            try:
                sig.bind(object(), object())
                return make_func_wrapper(func)
            except TypeError:
                raise TypeError("wrapped func should be either free function "
                                "or method that accepts "
                                "'request' and 'response' parameters")

    def make_method_wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(self, request):
            response = web.HTTPOk()
            ctx = yield from func(self, request, response)
            return do_render(ctx, request, response)
        return wrapped

    def make_func_wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(request):
            response = web.HTTPOk()
            ctx = yield from func(request, response)
            return do_render(ctx, request, response)
        return wrapped

    def do_render(ctx, request, response):
        env = request.app[APP_KEY]
        try:
            template = env.get_template(template_name)
        except jinja2.TemplateNotFound:
            raise web.HTTPInternalServerError(
                text="Template {} not found".format(template_name))
        text = template.render(ctx)
        response.content_type = 'text/html'
        response.charset = encoding
        response.text = text
        return response

    return wrapper
