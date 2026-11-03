FROM python:3.13-slim@sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74
RUN sed -i 's|http://deb.debian.org|https://mirrors.huaweicloud.com|g' /etc/apt/sources.list.d/debian.sources
ENV PIP_INDEX_URL=https://repo.huaweicloud.com/repository/pypi/simple
