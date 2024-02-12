ARG PYTHON_VERSION=3.10.5
FROM python:${PYTHON_VERSION}-slim-bullseye as python-base
WORKDIR /usr/tmp
ENV GLUE_WORKSPACE="/home/glue_user/workspace/jupyter_workspace"
ARG FUNCTION_DIR=/usr/tmp \
    PATH="$PATH:/runtime/bin" \
    FOLDER_NAME=glue_library \
    POETRY_VERSION=1.7.0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100\
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONPATH="$PYTHONPATH:/runtime/lib/python3.10/site-packages":/usr/tmp

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get dist-upgrade -y \
    && apt-get install -y zip unzip curl \
    && apt-get -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock ${FUNCTION_DIR}

RUN pip install \
    wheel \
    "poetry==$POETRY_VERSION" \
    && poetry export --with dev --without-hashes --no-interaction --no-ansi -f requirements.txt -o requirements.txt \
    && pip wheel -w ${FUNCTION_DIR}/wheelhouse -r requirements.txt

RUN pip install \
    --requirement requirements.txt \
    --target ${FOLDER_NAME} \
    --no-index --find-links /usr/tmp/wheelhouse
RUN find ${FOLDER_NAME} -maxdepth 1 -type d -name '*dist-info*' | xargs -I@ rm -rf @

FROM amazon/aws-glue-libs:glue_libs_4.0.0_image_01
ENV GLUE_WORKSPACE="/home/glue_user/workspace/jupyter_workspace"
ARG MOCK_AWS_HOST \
    DEFAULT_TIMEZONE \
    AWS_PROFILE \
    AWS_ACCESS_KEY_ID \
    AWS_SECRET_ACCESS_KEY \
    FUNCTION_DIR=/usr/tmp

COPY --from=python-base ${FUNCTION_DIR}/glue_library ${GLUE_WORKSPACE}/
COPY  ./infrastructure/athena_tables ${GLUE_WORKSPACE}/athena_tables/
COPY  ./jobs/assets/*.yaml \
      ./jobs/*.py ${GLUE_WORKSPACE}

COPY ./.docker/notebook/jupyter_workspace/*.ipynb ${GLUE_WORKSPACE}
COPY  ./jobs/common ${GLUE_WORKSPACE}/common/

ARG SPARK_HOME=/home/glue_user/spark
ENV PYTHONPATH=$PYTHONPATH:$GLUE_WORKSPACE:/home/glue_user/workspace/:$SPARK_HOME/python/:$SPARK_HOME/python/lib/py4j-0.10.9-src.zip
USER root
RUN chown -R glue_user ${GLUE_WORKSPACE}
USER glue_user
ENTRYPOINT [ "/bin/sh" ]
# source /home/glue_user/.bashrc && /home/glue_user/jupyter/jupyter_start.sh
