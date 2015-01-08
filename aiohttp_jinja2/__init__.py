__version__ = '0.1.0a'

import asyncio
import functools
import inspect
import jinja2
from aiohttp import web


__all__ = ('setup', 'get_env', 'render_template', 'template')


APP_KEY = 'aiohttp_jinja2_environment'


def setup(app, *args, app_key=APP_KEY, **kwargs):
    env = jinja2.Environment(*args, **kwargs)
    app[app_key] = env
    return env


def get_env(app, app_key=APP_KEY):
    return app.get(app_key)


def render_template(template_name, request, context, *,
                    app_key=APP_KEY, response=None, encoding='utf-8'):
    env = request.app.get(app_key)
    if env is None:
        raise web.HTTPInternalServerError(
            text=("Template engine is not initialized, "
                  "call aiohttp_jinja2.setup(app_key={}) first"
                  "".format(app_key)))
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound:
        raise web.HTTPInternalServerError(
            text="Template {} not found".format(template_name))
    text = template.render(context)
    if response is None:
        response = web.HTTPOk()
    response.content_type = 'text/html'
    response.charset = encoding
    response.text = text
    return response


def template(template_name, encoding='utf-8', app_key=APP_KEY):

    def wrapper(func):
        if not asyncio.iscoroutinefunction(func):
            func = asyncio.coroutine(func)
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
            context = yield from func(self, request, response)
            return render_template(template_name, request, context,
                                   app_key=app_key, response=response,
                                   encoding=encoding)
        return wrapped

    def make_func_wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(request):
            response = web.HTTPOk()
            context = yield from func(request, response)
            return render_template(template_name, request, context,
                                   app_key=app_key, response=response,
                                   encoding=encoding)
        return wrapped

    return wrapper
