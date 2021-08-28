FROM python:3.9.6

# You can pass PIP_ENV=development to install development dependencies
ARG PIP_ENV=production

# Root directory
WORKDIR /usr/src

# Application user
RUN set -eux \
    && groupadd app \
    && useradd -d /usr/src -g app app

# Data directory
RUN set -eux \
    && mkdir /data
VOLUME /data

# Prevents Python from writing *.pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Build dependencies
RUN set -eux \
    && apt-get update \
    && apt-get install -y \
        cmake \
        ffmpeg

# Copy application
COPY . /usr/src/

# Install application dependencies
RUN set -eux \
    && pip install -r /usr/src/requirements/${PIP_ENV}.txt \
    && rm -rf /root/.cache/pip

# Expose application port
EXPOSE 8000

# Start the application
CMD /usr/src/docker-entrypoint.sh
