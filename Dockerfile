FROM python:3.11-alpine3.16

WORKDIR /core
COPY requirements.txt /temp/requirements.txt
RUN pip install -r /temp/requirements.txt

COPY /core /core

EXPOSE 8000
