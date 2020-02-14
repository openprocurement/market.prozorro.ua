FROM python:3.7.6 AS compile-image
WORKDIR /code

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --disable-pip-version-check -r requirements.txt

FROM python:3.7.6-slim AS build-image
WORKDIR /code

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y -q libpq5 \
    && rm -vrf /var/lib/apt/lists/*

RUN useradd -r -l market_prozorro_ua
COPY --from=compile-image /opt/venv /opt/venv
COPY --chown=market_prozorro_ua application ./application
COPY --chown=market_prozorro_ua criteria ./criteria
COPY --chown=market_prozorro_ua profiles ./profiles
COPY --chown=market_prozorro_ua standarts ./standarts
COPY --chown=market_prozorro_ua auth.htpasswd manage.py ./
COPY docker-entrypoint.sh /usr/local/bin/

USER market_prozorro_ua
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED="1" \
    WORKER_CONNECTIONS="1000" \
    WORKERS="9"
EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
