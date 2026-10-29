import pytest

from draft.autobuild import prepare_candidate


BASE = (
    "FROM python:3.13-slim\n"
    "WORKDIR /work\n"
    "COPY main.c Makefile ./\n"
    "RUN make\n"
    'CMD ["./hello"]\n'
)
PINNED = "FROM python:3.13-slim@sha256:" + "a" * 64
CANDIDATE = BASE.replace("FROM python:3.13-slim", PINNED).replace(
    "RUN make", "RUN apt-get install -y build-essential\nRUN make"
)


def test_candidate_cannot_add_a_second_build_stage():
    candidate = CANDIDATE + "FROM scratch AS extra-stage\n"

    with pytest.raises(ValueError, match="Only single-stage candidates are supported"):
        prepare_candidate(BASE, candidate)
