FROM python:3.11-slim

LABEL vendor="AppCard"
LABEL maintainer="AppCard <devops@appcard.com>"

# RUN groupadd -g 1000 appcard \
#     && useradd -ms /bin/bash -u 1000 appcard -g appcard

ARG HOME="/usr/local"

COPY litestar_htmx_login /opt/appcard/litestar_htmx_login/litestar_htmx_login
COPY poetry.toml /opt/appcard/litestar_htmx_login/
COPY pyproject.toml /opt/appcard/litestar_htmx_login/
COPY README.md /opt/appcard/litestar_htmx_login/
WORKDIR /opt/appcard/litestar_htmx_login

# install pips
RUN python3 -m pip install --upgrade pip setuptools
RUN python3 -m pip install poetry
RUN python3 -m poetry install

# USER appcard

CMD ["python3", "-m", "poetry" ,"run", "uvicorn" ,"litestar_htmx_login.app:app", "--reload", "--host", "0.0.0.0", "--port", "5999"]

