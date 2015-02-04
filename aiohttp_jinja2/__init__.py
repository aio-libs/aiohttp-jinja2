__version__ = '0.0.1'

import asyncio
import functools
import jinja2
from aiohttp import web


__all__ = ('setup', 'get_env', 'render_template', 'template')


APP_KEY = 'aiohttp_jinja2_environment'


def setup(app, *args, **kwargs):
    env = jinja2.Environment(*args, **kwargs)
    app[APP_KEY] = env
    return env


def get_env(app):
    return app.get(APP_KEY)


def _render_template(template_name, request, response, context, *,
                     encoding='utf-8'):
    env = request.app.get(APP_KEY)
    if env is None:
        raise web.HTTPInternalServerError(
            text=("Template engine is not initialized, "
                  "call aiohttp_jinja2.setup() first"))
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound:
        raise web.HTTPInternalServerError(
            text="Template {} not found".format(template_name))
    text = template.render(context)
    response.content_type = 'text/html'
    response.charset = encoding
    response.text = text
    return response


def render_template(template_name, request, context, *,
                    encoding='utf-8'):
    response = web.Response()
    return _render_template(template_name, request, response, context,
                            encoding=encoding)


def template(template_name, encoding='utf-8'):

    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            coro = asyncio.coroutine(func)
            response = web.Response()
            context = yield from coro(*args)
            request = args[-1]
            return _render_template(template_name, request, response, context,
                                    encoding=encoding)
        return wrapped

    return wrapper
