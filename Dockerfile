FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install -r /code/requirements.txt
RUN pip install gunicorn
RUN mkdir -p /code/media && mkdir -p /code/static

COPY . /code/
WORKDIR /code
RUN rm -rf public
RUN useradd oscar_auction
RUN chown -R oscar_auction /code
USER oscar_auction

EXPOSE 8000
