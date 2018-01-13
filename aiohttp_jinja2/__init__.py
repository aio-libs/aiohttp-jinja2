import asyncio
import functools
import jinja2
from collections import Mapping
from aiohttp import web
from aiohttp.abc import AbstractView
from .helpers import GLOBAL_HELPERS


__version__ = '0.15.0a0'

__all__ = ('setup', 'get_env', 'render_template', 'template')


APP_CONTEXT_PROCESSORS_KEY = 'aiohttp_jinja2_context_processors'
APP_KEY = 'aiohttp_jinja2_environment'
REQUEST_CONTEXT_KEY = 'aiohttp_jinja2_context'


def setup(app, *args, app_key=APP_KEY, context_processors=(),
          filters=None, default_helpers=True, **kwargs):
    kwargs.setdefault('autoescape', True)
    env = jinja2.Environment(*args, **kwargs)
    if default_helpers:
        env.globals.update(GLOBAL_HELPERS)
    if filters is not None:
        env.filters.update(filters)
    app[app_key] = env
    if context_processors:
        app[APP_CONTEXT_PROCESSORS_KEY] = context_processors
        app.middlewares.append(context_processors_middleware)

    env.globals['app'] = app

    return env


def get_env(app, *, app_key=APP_KEY):
    return app.get(app_key)


def render_string(template_name, request, context, *, app_key=APP_KEY):
    env = request.app.get(app_key)
    if env is None:
        text = ("Template engine is not initialized, "
                "call aiohttp_jinja2.setup(..., app_key={}) first"
                "".format(app_key))
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound as e:
        text = "Template '{}' not found".format(template_name)
        raise web.HTTPInternalServerError(reason=text, text=text) from e
    if not isinstance(context, Mapping):
        text = "context should be mapping, not {}".format(type(context))
        # same reason as above
        raise web.HTTPInternalServerError(reason=text, text=text)
    if request.get(REQUEST_CONTEXT_KEY):
        context = dict(request[REQUEST_CONTEXT_KEY], **context)
    text = template.render(context)
    return text


def render_template(template_name, request, context, *,
                    app_key=APP_KEY, encoding='utf-8', status=200):
    response = web.Response(status=status)
    if context is None:
        context = {}
    text = render_string(template_name, request, context, app_key=app_key)
    response.content_type = 'text/html'
    response.charset = encoding
    response.text = text
    return response


def template(template_name, *, app_key=APP_KEY, encoding='utf-8', status=200):

    def wrapper(func):
        @asyncio.coroutine
        @functools.wraps(func)
        def wrapped(*args):
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                coro = asyncio.coroutine(func)
            context = yield from coro(*args)
            if isinstance(context, web.StreamResponse):
                return context

            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]

            response = render_template(template_name, request, context,
                                       app_key=app_key, encoding=encoding)
            response.set_status(status)
            return response
        return wrapped
    return wrapper


@asyncio.coroutine
def context_processors_middleware(app, handler):
    @asyncio.coroutine
    def middleware(request):
        request[REQUEST_CONTEXT_KEY] = {}
        for processor in app[APP_CONTEXT_PROCESSORS_KEY]:
            request[REQUEST_CONTEXT_KEY].update(
                (yield from processor(request)))
        return (yield from handler(request))
    return middleware


@asyncio.coroutine
def request_processor(request):
    return {'request': request}
