FROM python:3.10-alpine3.16
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.16/main' > /etc/apk/repositories
RUN apk add tzdata
RUN cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime
RUN echo "Europe/Moscow" > /etc/timezone
RUN date && apk del tzdata

ADD req.pip /tmp/req.pip
RUN pip install -r /tmp/req.pip

ADD . /app
WORKDIR /app

RUN crontab /app/conf/crontab
CMD crond && API_TOKEN=${API_TOKEN} /app/main.py
