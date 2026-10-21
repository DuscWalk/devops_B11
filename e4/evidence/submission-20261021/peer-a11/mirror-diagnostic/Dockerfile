ARG BASE_IMAGE=python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
FROM ${BASE_IMAGE}

ARG PIP_INDEX_URL=https://pypi.org/simple

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN sed -i 's|http://deb.debian.org|https://mirrors.huaweicloud.com|g' /etc/apt/sources.list.d/debian.sources \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
      gcc make libc6-dev strace git \
 && rm -rf /var/lib/apt/lists/* \
 && dpkg-query -W -f='${Package}=${Version}\n' \
      gcc make libc6-dev strace git \
      > /opt/toolchain.lock

COPY requirements-dev.lock /tmp/requirements-dev.lock
RUN pip install \
      --index-url "${PIP_INDEX_URL}" \
      --require-hashes \
      -r /tmp/requirements-dev.lock \
 && rm -f /tmp/requirements-dev.lock

RUN useradd --uid 10001 app \
 && install -d -o app -g app /app \
 && install -d -o app -g app /app/work

COPY --chown=app:app services/buildchecker/ /app/
COPY --chown=app:app scripts/ /app/scripts/
COPY --chown=app:app fixtures/md-rd/ /app/fixtures/md-rd/

WORKDIR /app
USER app

CMD ["python", "-m", "buildchecker.cli", "version"]
