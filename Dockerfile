FROM alpine

COPY requirements.txt /home/requirements.txt

RUN apk update && \
    apk add --no-cache python3 py3-pip \
    pip install -r /home/requirements.txt \
    adduser -D -s /bin/ash runner

COPY /src/ /home/publications-service/src/

RUN chown -R runner:runner /home/publications-service/

EXPOSE 9990

USER runner

WORKDIR /home/publications-service/

ENTRYPOINT ["bash", "run.sh"]