from litestar import Litestar, get

from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar import get, post, Litestar, Request, Response
from litestar.response import Template

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK, HTTP_302_FOUND
from litestar.datastructures import Cookie, Header
from dataclasses import dataclass
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler

from typing import Annotated

from litestar import Litestar, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.types import ASGIApp, Scope, Receive, Send
from litestar.response import Redirect
from litestar import Request
from litestar.middleware.base import MiddlewareProtocol
from litestar.middleware.session.client_side import CookieBackendConfig
from os import urandom
from litestar.response.redirect import ASGIRedirectResponse

# we initialize to config with a 16 byte key, i.e. 128 a bit key.
# in real world usage we should inject the secret from the environment
session_config = CookieBackendConfig(secret=urandom(16))  # type: ignore[arg-type]



from litestar.middleware import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar.connection import ASGIConnection


from pathlib import Path
import pprint
from attrs import define, field

import logging
LOGGER = logging.getLogger(__name__)


class RedirectMiddleware(MiddlewareProtocol):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        c = Request(scope).cookies
        if "auth" not in c or c["auth"] != AUTHENTICATION_TOKEN:
            response = ASGIRedirectResponse(path="/login")
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

@get("/", middleware=[RedirectMiddleware])
async def get_home() -> Template:
    return HTMXTemplate(template_name="home.html", push_url="/form")

@get("/ping")
async def ping() -> dict[str, str]:
    return {"msg": "pong"}


@get("/login")
async def get_login() -> Template:
    return HTMXTemplate(template_name="login.html", push_url="/form")

@define
class LoginPayload:
    username: str
    password: str
    remember: bool = field(default=False)


@post("/login")
async def login(data: Annotated[LoginPayload, Body(media_type=RequestEncodingType.MULTI_PART)], request: Request) -> str:
    c = request.cookies
    h = request.headers
    
    if "auth" in c and c["auth"] == AUTHENTICATION_TOKEN:
        return Response("ok", cookies=[Cookie(key="auth", value=AUTHENTICATION_TOKEN,httponly=True)], headers={"HX-Redirect" : "/"})

    token = await get_token_based_on_login(data.username, data.password)

    if token:
        return Response("ok", cookies=[Cookie(key="auth", value=token,httponly=True)], headers={"HX-Redirect" : "/"})
    
    return Response("Invalid Username or Password")


AUTHENTICATION_TOKEN = '1234'

async def get_token_based_on_login(username: str, password: str) -> str | None:
    if username == 'viett' and password == 'password':
        return AUTHENTICATION_TOKEN
    else:
        return None

@post("/api/users/token")
async def get_token(data: dict[str, str], request: Request)-> Response:
    username = data["username"]
    password = data["password"]

    token = await get_token_based_on_login(username, password)

    if token:
        d = {
            "data": {
                "authentication_token" : token,
                "status" : "success"
            }
        }
        r = Response(d, status_code=HTTP_201_CREATED, cookies=[Cookie(key="auth", value=token,httponly=True)])
        return r
    else:
        raise HTTPException(detail="Invalid username or password", status_code=HTTP_403_FORBIDDEN)

@get("/api/users/me")
async def get_me(request: Request) -> Response:
    h = request.headers
    c = request.cookies
    LOGGER.info(c)
    if "auth" in c and c["auth"] == AUTHENTICATION_TOKEN:
        d = {"data" : {"name" : "Viet Than"}}
        r = Response(d, status_code=HTTP_200_OK)
        return r
    else:
        raise HTTPException("Not Authorized")

app = Litestar(
    route_handlers=[get_home, ping, get_login, login, get_token, get_me],
    debug=True,
    request_class=HTMXRequest,
    template_config=TemplateConfig(
        directory=Path("litestar_htmx_login/templates"),
        engine=JinjaTemplateEngine,
    ),
    middleware=[
        # session_config.middleware
    ]
)