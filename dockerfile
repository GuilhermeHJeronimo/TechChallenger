FROM python:3.13-slim-bullseye AS builder

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim-bullseye AS runtime

WORKDIR /app

ARG APP\_USER=appuser
RUN groupadd -r ${APP\_USER} && useradd --no-log-init -r -g ${APP\_USER} ${APP\_USER}

COPY --from=builder /opt/venv /opt/venv

COPY ./app /app/app

COPY ./templates /app/templates
COPY ./static /app/static

ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER ${APP\_USER}

EXPOSE 8000

CMD ["gunicorn", "-w", "2", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000"]