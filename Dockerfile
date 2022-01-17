FROM alpine

COPY requirements.txt /home/requirements.txt

RUN apk update && \
    apk add --no-cache python3 py3-pip \
    pip install -r /home/requirements.txt \
    adduser -D -s /bin/ash runner

COPY /res/ /home/hero-management-µs/res/
COPY /src/ /home/hero-management-µs/src/

RUN chown -R runner:runner /home/hero-management-µs/

EXPOSE 9990

USER runner

WORKDIR /home/hero-management-µs

ENTRYPOINT ["python3", "-u", "src/main.py"]