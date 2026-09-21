# Manually prepared baseline candidate, not an executed DRAFT output.
# Not built yet; base digest and package versions require later pinning.
FROM ubuntu:24.04
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/jhawthorn/fzy.git /workspace/fzy \
    && cd /workspace/fzy \
    && git checkout --detach 28195b3a709995354b6c33cec9bb7c9f81532eb6 \
    && test "$(git rev-parse HEAD)" = "28195b3a709995354b6c33cec9bb7c9f81532eb6"
WORKDIR /workspace/fzy
RUN make clean && make && make check && ./fzy --help
CMD ["sh"]
