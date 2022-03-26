FROM alpine

COPY requirements.txt /home/requirements.txt

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/main' >> /etc/apk/repositories && \
    echo 'http://dl-cdn.alpinelinux.org/alpine/v3.9/community' >> /etc/apk/repositories


RUN apk update

RUN apk add mongodb yaml-cpp=0.6.2-r2 && \
    apk add openrc --no-cache && \
    mkdir -p /data/db/

RUN rc-update add mongodb default

RUN apk update && \
    apk add --no-cache python3 py3-pip && \
    apk add build-base && \
    apk add python3-dev && \
    pip install -r /home/requirements.txt

COPY src /home/publications-service/src
COPY run.sh /home/publications-service/

EXPOSE 8080

WORKDIR /home/publications-service/

ENTRYPOINT ["sh", "run.sh"]