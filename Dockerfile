FROM python:3.8

ENV PYTHONBUFFERED=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=1

WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry \
      && poetry config virtualenvs.create false \
      && poetry install --no-dev --no-interaction --no-ansi \
      && pip uninstall --yes poetry

ADD . .
RUN useradd -m user
USER user

CMD ["uwsgi", "--master", "--die-on-term", "--module", "karaokeserver.app:app", "--http-socket", ":5000"]
