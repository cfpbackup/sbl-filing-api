FROM ghcr.io/cfpb/regtech/sbl/python-alpine:3.12

WORKDIR /usr/app
RUN mkdir upload
RUN pip install poetry

COPY --chown=sbl:sbl poetry.lock pyproject.toml alembic.ini README.md ./

COPY --chown=sbl:sbl ./src ./src
COPY --chown=sbl:sbl ./db_revisions ./db_revisions

RUN poetry config virtualenvs.create false
RUN poetry install --only main

RUN chmod -R 447 /usr/app/upload

WORKDIR /usr/app/src

EXPOSE 8888

USER sbl

CMD ["python", "sbl_filing_api/main.py"]
