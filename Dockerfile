FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
RUN mkdir -p /code/media && mkdir -p /code/static

COPY . /code/
WORKDIR /code
RUN rm -rf public
RUN useradd market_prozorro_ua
RUN chown -R market_prozorro_ua /code
USER market_prozorro_ua

EXPOSE 8000
