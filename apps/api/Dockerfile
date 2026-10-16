FROM python:3.12.15-alpine3.24@sha256:1b668429b3511ab407d8e00648891631b0b1a4d7e15e3ca70f38ab5b91ad4ab4

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --require-hashes --only-binary=:all: -r requirements.txt \
    && addgroup -g 10001 -S legalia \
    && adduser -u 10001 -S -D -H -G legalia -s /sbin/nologin legalia

COPY src/ ./src/
COPY certificates/supabase-prod-ca-2021.crt ./certificates/supabase-prod-ca-2021.crt
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "abogalia_api.production"]
