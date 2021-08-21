import asyncio
import functools
import sys
import warnings
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

import jinja2
from aiohttp import web
from aiohttp.abc import AbstractView

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from .helpers import GLOBAL_HELPERS
from .typedefs import Filters

__version__ = "1.5"

__all__ = ("setup", "get_env", "render_template", "render_string", "template")


APP_CONTEXT_PROCESSORS_KEY = "aiohttp_jinja2_context_processors"
APP_KEY = "aiohttp_jinja2_environment"
REQUEST_CONTEXT_KEY = "aiohttp_jinja2_context"

_TemplateReturnType = Awaitable[Union[web.StreamResponse, Mapping[str, Any]]]
_SimpleTemplateHandler = Callable[[web.Request], _TemplateReturnType]
_ContextProcessor = Callable[[web.Request], Awaitable[Dict[str, Any]]]

_T = TypeVar("_T")
_AbstractView = TypeVar("_AbstractView", bound=AbstractView)


class _TemplateWrapper(Protocol):
    @overload
    def __call__(
        self, func: _SimpleTemplateHandler
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        ...

    @overload
    def __call__(
        self, func: Callable[[_AbstractView], _TemplateReturnType]
    ) -> Callable[[_AbstractView], Awaitable[web.StreamResponse]]:
        ...

    @overload
    def __call__(
        self, func: Callable[[_T, web.Request], _TemplateReturnType]
    ) -> Callable[[_T, web.Request], Awaitable[web.StreamResponse]]:
        ...


def setup(
    app: web.Application,
    *args: Any,
    app_key: str = APP_KEY,
    context_processors: Iterable[_ContextProcessor] = (),
    filters: Optional[Filters] = None,
    default_helpers: bool = True,
    **kwargs: Any,
) -> jinja2.Environment:
    kwargs.setdefault("autoescape", True)
    env = jinja2.Environment(*args, **kwargs)
    if default_helpers:
        env.globals.update(GLOBAL_HELPERS)
    if filters is not None:
        env.filters.update(filters)
    app[app_key] = env
    if context_processors:
        app[APP_CONTEXT_PROCESSORS_KEY] = context_processors
        app.middlewares.append(context_processors_middleware)

    env.globals["app"] = app

    return env


def get_env(app: web.Application, *, app_key: str = APP_KEY) -> jinja2.Environment:
    return cast(jinja2.Environment, app.get(app_key))


def _render_string(
    template_name: str,
    request: web.Request,
    context: Mapping[str, Any],
    app_key: str,
) -> Tuple[jinja2.Template, Mapping[str, Any]]:
    env = request.config_dict.get(app_key)
    if env is None:
        text = (
            "Template engine is not initialized, "
            "call aiohttp_jinja2.setup(..., app_key={}) first"
            "".format(app_key)
        )
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    try:
        template = env.get_template(template_name)
    except jinja2.TemplateNotFound as e:
        text = f"Template '{template_name}' not found"
        raise web.HTTPInternalServerError(reason=text, text=text) from e
    if not isinstance(context, Mapping):
        text = "context should be mapping, not {}".format(type(context))
        # same reason as above
        raise web.HTTPInternalServerError(reason=text, text=text)
    if request.get(REQUEST_CONTEXT_KEY):
        context = dict(request[REQUEST_CONTEXT_KEY], **context)
    return template, context


def render_string(
    template_name: str,
    request: web.Request,
    context: Mapping[str, Any],
    *,
    app_key: str = APP_KEY,
) -> str:
    template, context = _render_string(template_name, request, context, app_key)
    return template.render(context)


async def render_string_async(
    template_name: str,
    request: web.Request,
    context: Mapping[str, Any],
    *,
    app_key: str = APP_KEY,
) -> str:
    template, context = _render_string(template_name, request, context, app_key)
    return await template.render_async(context)


def _render_template(
    context: Optional[Mapping[str, Any]],
    encoding: str,
    status: int,
) -> Tuple[web.Response, Mapping[str, Any]]:
    response = web.Response(status=status)
    if context is None:
        context = {}
    response.content_type = "text/html"
    response.charset = encoding
    return response, context


def render_template(
    template_name: str,
    request: web.Request,
    context: Optional[Mapping[str, Any]],
    *,
    app_key: str = APP_KEY,
    encoding: str = "utf-8",
    status: int = 200,
) -> web.Response:
    response, context = _render_template(context, encoding, status)
    response.text = render_string(template_name, request, context, app_key=app_key)
    return response


async def render_template_async(
    template_name: str,
    request: web.Request,
    context: Optional[Mapping[str, Any]],
    *,
    app_key: str = APP_KEY,
    encoding: str = "utf-8",
    status: int = 200,
) -> web.Response:
    response, context = _render_template(context, encoding, status)
    response.text = await render_string_async(
        template_name, request, context, app_key=app_key
    )
    return response


def template(
    template_name: str,
    *,
    app_key: str = APP_KEY,
    encoding: str = "utf-8",
    status: int = 200,
) -> _TemplateWrapper:
    @overload
    def wrapper(
        func: _SimpleTemplateHandler,
    ) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        ...

    @overload
    def wrapper(
        func: Callable[[_AbstractView], _TemplateReturnType]
    ) -> Callable[[_AbstractView], Awaitable[web.StreamResponse]]:
        ...

    @overload
    def wrapper(
        func: Callable[[_T, web.Request], _TemplateReturnType]
    ) -> Callable[[_T, web.Request], Awaitable[web.StreamResponse]]:
        ...

    def wrapper(
        func: Callable[..., _TemplateReturnType]
    ) -> Callable[..., Awaitable[web.StreamResponse]]:
        @functools.wraps(func)
        async def wrapped(*args: Any) -> web.StreamResponse:  # type: ignore[misc]
            if asyncio.iscoroutinefunction(func):
                coro = func
            else:
                warnings.warn(
                    "Bare functions are deprecated, use async ones",
                    DeprecationWarning,
                )
                coro = asyncio.coroutine(func)
            context = await coro(*args)
            if isinstance(context, web.StreamResponse):
                return context

            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]

            env = request.config_dict.get(app_key)
            if env and env.is_async:
                response = await render_template_async(
                    template_name, request, context, app_key=app_key, encoding=encoding
                )
            else:
                response = render_template(
                    template_name, request, context, app_key=app_key, encoding=encoding
                )
            response.set_status(status)
            return response

        return wrapped

    return wrapper


@web.middleware
async def context_processors_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:

    if REQUEST_CONTEXT_KEY not in request:
        request[REQUEST_CONTEXT_KEY] = {}
    for processor in request.config_dict[APP_CONTEXT_PROCESSORS_KEY]:
        request[REQUEST_CONTEXT_KEY].update(await processor(request))
    return await handler(request)


async def request_processor(request: web.Request) -> Dict[str, web.Request]:
    return {"request": request}
