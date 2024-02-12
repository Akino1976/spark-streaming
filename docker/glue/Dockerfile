FROM amazon/aws-glue-streaming-libs:glue_streaming_libs_4.0.0_image_01
ENV GLUE_WORKSPACE="/home/glue_user/workspace"
ENV PYTHONPATH=$PYTHONPATH:${GLUE_WORKSPACE}:/usr/local/lib/python3.10/site-packages:/home/glue_user/.local/bin/ \
    PATH=$PATH:/home/glue_user/.local/bin/ \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    POETRY_VERSION=1.7.0 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100\
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    ICEBERG_VERSION=1.3.1 \
    AWS_SDK_VERSION=2.20.18 \
    POSTGRESQL_VERSION=42.2.24 \
    CONFLUENT_VERSION=5.5.0

ENV M2_HOME=/opt/apache-maven-3.6.0
ENV PATH="${PATH}:${M2_HOME}/bin"

USER root
RUN yum -y update && \
    yum -y install \
    curl \
    make \
    bzip2-devel \
    libffi-devel \
    librdkafka \
    zip \
    yum clean all \
    && rm -rf /var/cache/yum

RUN printf "\n%s\n" "alias python=/usr/local/bin/python3.10" >>/home/glue_user/.bashrc
RUN printf "\n%s\n" "alias pip=pip3.10" >>/home/glue_user/.bashrc
RUN printf "\n%s\n" "export PYSPARK_PYTHON=/usr/local/bin/python3.10" >>/home/glue_user/.bashrc
RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN rm -f /usr/bin/python3 && ln -s /usr/local/bin/python3.10 /usr/bin/python3
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip && ./aws/install
RUN curl -SsL https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz \
    | tar -C /opt --warning=no-unknown-keyword -xzf -

USER glue_user
COPY ./.docker/pom.xml .
RUN pip install "poetry==$POETRY_VERSION"
RUN pip install pytest pytest-watch pytest_bdd pytest-cov pytest-xdist
RUN mvn -f pom.xml -DoutputDirectory=${SPARK_HOME}/jars dependency:copy-dependencies
RUN curl https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/${AWS_SDK_VERSION}/bundle-${AWS_SDK_VERSION}.jar -Lo bundle-${AWS_SDK_VERSION}.jar \
    && mv bundle-${AWS_SDK_VERSION}.jar ${SPARK_HOME}/jars

RUN mkdir -p /tmp/write_iceberg_table_version

ENTRYPOINT [ "bash" ]
