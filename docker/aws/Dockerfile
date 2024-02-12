ARG PYTHON_VERSION=3.12.0
FROM r-docker-docker-hub.artifactory.klarna.net/python:${PYTHON_VERSION}
ARG AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY \
    SERVICENAME \
    ENVIRONMENT \
    AWS_CLI=1.29.17

RUN pip --no-cache-dir install "awscli==$AWS_CLI"

WORKDIR /data
COPY . /data

RUN chmod 755 provision-localstack.sh

ENTRYPOINT [ "./provision-localstack.sh" ]
