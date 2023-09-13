from litestar import Litestar, get

from litestar.contrib.htmx.request import HTMXRequest
from litestar.contrib.htmx.response import HTMXTemplate
from litestar import get, post, Litestar
from litestar.response import Template

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from pathlib import Path
import pprint

import logging
LOGGER = logging.getLogger(__name__)


@get("/ping")
async def ping() -> dict[str, str]:
    return {"msg": "pong"}


@get("/login")
async def get_login() -> Template:
    return HTMXTemplate(template_name="login.html", push_url="/form")

@post("/login")
async def login(request: HTMXRequest) -> str:
    d = {}
    for attr in dir(request):
        if attr == 'auth' or attr == 'session' or attr == 'user':
            continue
        d[attr] = getattr(request, attr, None)
    LOGGER.error(pprint.pformat(d, indent=4))
    return "ok"


app = Litestar(
    route_handlers=[ping, get_login, login],
    debug=True,
    request_class=HTMXRequest,
    template_config=TemplateConfig(
        directory=Path("litestar_htmx_login/templates"),
        engine=JinjaTemplateEngine,
    ),
)