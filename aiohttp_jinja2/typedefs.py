from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    Mapping,
    Tuple,
    TypedDict,
    Union,
)

import jinja2
from aiohttp import web

ContextProcessor = Callable[[web.Request[Any]], Awaitable[Dict[str, Any]]]
Filter = Callable[..., str]
Filters = Union[Iterable[Tuple[str, Filter]], Mapping[str, Filter]]


class AppState(TypedDict, total=False):
    """App config used by aiohttp-jinja2."""

    _aiohttp_jinja2_context_processors: Iterable[ContextProcessor]
    _aiohttp_jinja2_environment: jinja2.Environment
    static_root_url: str
