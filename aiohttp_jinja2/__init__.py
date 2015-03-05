import asyncio
import functools
import jinja2
from aiohttp import web


__version__ = '0.2.1'

__all__ = ('setup', 'get_env', 'render_template', 'template')


APP_KEY = 'aiohttp_jinja2_environment'


def setup(app, *args, app_key=APP_KEY, **kwargs):
    env = jinja2.Environment(*args, **kwargs)
    app[app_key] = env
    return env


def get_env(app, app_key=APP_KEY):
    return app.get(app_key)


def pre_validate(request, app_key, template_name):
    template_instance = None

    env = request.app.get(app_key)
    if env is None:
        raise web.HTTPInternalServerError(
            text=("Template engine is not initialized, call aiohttp_jinja2.setup(app_key={}) first".format(app_key)))
    try:
        template_instance = env.get_template(template_name)
    except jinja2.TemplateNotFound:
        raise web.HTTPInternalServerError(
            text="Template {} not found".format(template_name))

    return template_instance


@asyncio.coroutine
def get_html_from_template(template_name, request, context, *, app_key=APP_KEY):
    template_instance = pre_validate(request, app_key, template_name)
    return template_instance.render(context)


def _render_template(template_name, request, response, context, *, app_key, encoding):
    template_instance = pre_validate(request, app_key, template_name)

    if template_instance:
        text = template_instance.render(context)
        response.content_type = 'text/html'
        response.charset = encoding
        response.text = text


def render_template(template_name, request, context, *, app_key=APP_KEY, encoding='utf-8', response_status_code=200):
    response = web.Response(status=response_status_code)
    _render_template(
        template_name=template_name,
        request=request,
        response=response,
        context=context,
        app_key=app_key,
        encoding=encoding
    )
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
            response = web.Response()
            context = yield from coro(*args)
            request = args[-1]
            _render_template(template_name, request, response, context, app_key=app_key, encoding=encoding)
            response.set_status(status)
            return response
        return wrapped
    return wrapper

