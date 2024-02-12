ARG PYTHON_VERSION=3.10.5
FROM python:${PYTHON_VERSION}-slim-bullseye as python-base

ENV PYTHONPATH=$PYTHONPATH:/usr/local:/runtime/lib/python3.10 \
    PATH="$PATH:/runtime/bin"\
    ICEBERG_VERSION=1.2.0 \
    AWS_SDK_VERSION=2.20.18

ARG FUNCTION_DIR=/usr/tmp \
    POETRY_VERSION=1.7.0 \
    DESTINATION_FOLDER=${FUNCTION_DIR}/glue_packer \
    JARS_FOLDER=${FUNCTION_DIR}/glue_packer/jars \
    FOLDER_NAME=glue_library \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100\
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN  apt-get update -y \
    && apt-get upgrade -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y zip unzip curl\
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./.docker/glue_integrater ${FUNCTION_DIR}
COPY ./jobs ${FUNCTION_DIR}
WORKDIR ${FUNCTION_DIR}
RUN pip install wheel "poetry==$POETRY_VERSION" \
    && poetry export --without=dev --without-hashes --no-interaction --no-ansi \
        -f requirements.txt \
        -o requirements.txt \
    && pip wheel -w ${FUNCTION_DIR}/wheelhouse -r requirements.txt

RUN pip install \
    --requirement requirements.txt \
    --target ${DESTINATION_FOLDER}/${FOLDER_NAME} \
    --no-index --find-links ${FUNCTION_DIR}/wheelhouse \
    && cp -R ./common ${DESTINATION_FOLDER}/${FOLDER_NAME} \
    && cp -R ./assets/*.yaml ./assets/consumer/*.yaml ./assets/producer/*.yaml *.py --parents -t ${DESTINATION_FOLDER}

RUN pip install click boto3
WORKDIR ${DESTINATION_FOLDER}
RUN cd ${FOLDER_NAME} \
    && zip -r ../${FOLDER_NAME}.zip . -x '*.*dist-info/*' \
    && cd - && rm -rf ${FOLDER_NAME} && rm run_upload.py config.py

FROM l-docker-fin-data-integration-staging.artifactory.klarna.net/fin-data-integration/bookkeeping-data-streaming-glue:v1
RUN mkdir -p ${GLUE_WORKSPACE}/glue_packer/jars
COPY --from=python-base /glue_packer ${GLUE_WORKSPACE}/glue_packer
COPY ./.docker/glue_integrater ${GLUE_WORKSPACE}
USER root
#copy jars needed for upload to S3
RUN cp ${SPARK_HOME}/jars/url-connection-client-${AWS_SDK_VERSION}.jar \
    ${SPARK_HOME}/jars/bundle-${AWS_SDK_VERSION}.jar \
    ${SPARK_HOME}/jars/iceberg-spark-runtime-3.3_2.12-${ICEBERG_VERSION}.jar \
    ${GLUE_WORKSPACE}/glue_packer/jars
USER glue_user
ENTRYPOINT [ "python3.10" ]
CMD [ "run_upload.py", "upload-handler" ]
