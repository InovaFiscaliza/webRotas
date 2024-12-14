# syntax=docker/dockerfile:1.4

# Condigo antigo instalação do python
# FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

FROM python:3.10 AS builder


WORKDIR /code
COPY requirements.txt /code
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY . .

################################################################################
# RUN echo "deb http://security.ubuntu.com/ubuntu bionic-security main" >> /etc/apt/sources.list
# RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
# RUN apt-get update
# RUN apt-get install -y firefox
################################################################################

################################################################################
# Instalando cron e certbot 
RUN apt-get update
RUN apt-get install -y cron && apt-get install -y vim
RUN pip install gunicorn
RUN apt-get install dos2unix

COPY crontab /etc/crontab
RUN dos2unix /etc/crontab
RUN chmod 0644 /etc/crontab

# RUN service cron start

# CMD ["cron", "-f"]

################################################################################


ENV FLASK_APP webdir/Site.py
ENV FLASK_ENV development
ENV FLASK_RUN_PORT 8000
ENV FLASK_RUN_HOST 0.0.0.0

EXPOSE 8000

# CMD ["flask", "run"]

COPY gunicorn.sh /code/gunicorn.sh
RUN chmod +x   /code/gunicorn.sh
RUN dos2unix /code/gunicorn.sh
CMD ["/code/gunicorn.sh"]
################################################################################
