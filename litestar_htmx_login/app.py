from litestar import Litestar, get

from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar import get, post, Litestar, Request, Response
from litestar.response import Template

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_200_OK
from litestar.datastructures import Cookie
from dataclasses import dataclass

from typing import Annotated

from litestar import Litestar, post
from litestar.enums import RequestEncodingType
from litestar.params import Body

from pathlib import Path
import pprint
from attrs import define, field

import logging
LOGGER = logging.getLogger(__name__)

@get("/ping")
async def ping() -> dict[str, str]:
    return {"msg": "pong"}


@get("/login")
async def get_login() -> Template:
    return HTMXTemplate(template_name="login.html", push_url="/form")

def checkbox_converter(x: str) -> bool:
    LOGGER.info(f"got to checkbox_converter: {x}")
    return x == 'on'

@define
class LoginPayload:
    username: str
    password: str
    remember: bool = field(default=False, converter=checkbox_converter)


@post("/login")
async def login(data: Annotated[LoginPayload, Body(media_type=RequestEncodingType.MULTI_PART)]) -> str:
    LOGGER.info(data)
    return "ok"


AUTHENTICATION_TOKEN = '1234'

@post("/api/users/token")
async def get_token(data: dict[str, str], request: Request)-> Response:
    username = data["username"]
    password = data["password"]

    if username == 'viett' and password == 'password':
        h = request.headers
        c = request.cookies
        LOGGER.info(c)
        d = {
            "data": {
                "authentication_token" : AUTHENTICATION_TOKEN,
                "status" : "success"
            }
        }
        r = Response(d, status_code=HTTP_201_CREATED, cookies=[Cookie(key="auth", value=AUTHENTICATION_TOKEN,httponly=True)])
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
    route_handlers=[ping, get_login, login, get_token, get_me],
    debug=True,
    request_class=HTMXRequest,
    template_config=TemplateConfig(
        directory=Path("litestar_htmx_login/templates"),
        engine=JinjaTemplateEngine,
    ),
)