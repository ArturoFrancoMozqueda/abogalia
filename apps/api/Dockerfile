FROM python:3.12.15-slim-bookworm@sha256:34386ef0cb081344d7ec1c103ba398e6e9f64e9ab3a1509accc92a4e24a07258

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --require-hashes --only-binary=:all: -r requirements.txt \
    && groupadd --gid 10001 legalia \
    && useradd --uid 10001 --gid 10001 --no-create-home --shell /usr/sbin/nologin legalia

COPY src/ ./src/
COPY certificates/supabase-prod-ca-2021.crt ./certificates/supabase-prod-ca-2021.crt
USER 10001:10001
EXPOSE 8080
CMD ["python", "-m", "abogalia_api.production"]
