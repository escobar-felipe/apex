FROM python:3.10-slim-bullseye

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV BASE_URL /

RUN /opt/venv/bin/python3 -m pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/

RUN . /opt/venv/bin/activate && pip install --no-cache-dir -r requirements.txt

RUN python3 -m nltk.downloader punkt -d /usr/share/nltk_data

COPY ./src /app/src/
COPY wsgi.py /app/
COPY ./assets /app/assets