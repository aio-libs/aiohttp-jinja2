from aiohttp.web import Application, Request

from aiohttp_jinja2 import AppState

_App = Application[AppState]
_Request = Request[AppState]
