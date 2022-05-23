FROM alpine

COPY requirements.txt /home/requirements.txt

RUN apk update && \
    apk add --no-cache python3 py3-pip && \
    apk add build-base && \
    apk add python3-dev && \
    pip install -r /home/requirements.txt && \
    adduser -D -s /bin/ash runner

COPY src /home/publications-service/src
COPY run.sh /home/publications-service/

RUN chown -R runner:runner /home/publications-service/

EXPOSE 8000

USER runner

WORKDIR /home/publications-service/

ENTRYPOINT ["sh", "run.sh"]