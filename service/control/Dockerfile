FROM python:3.9-alpine

ARG CONTROL_PORT
ENV CONTROL_PORT $CONTROL_PORT

WORKDIR /app

COPY src/requirements.txt .
RUN pip3 install -r requirements.txt

COPY src .

COPY data /

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
