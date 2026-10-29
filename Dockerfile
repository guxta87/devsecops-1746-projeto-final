FROM python:3.11.14-slim-bookworm AS builder

WORKDIR /build

COPY requirements.txt .

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt


FROM python:3.11.14-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# A atualização da imagem base é exigida pelo exercício para aplicar correções
# de segurança publicadas após a geração da tag fixada.
# hadolint ignore=DL3005
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 nonroot \
    && useradd --uid 10001 --gid nonroot --create-home nonroot

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=nonroot:nonroot app ./app

# Ferramentas de empacotamento são necessárias apenas no estágio de build.
RUN rm -rf \
        /usr/local/lib/python3.11/site-packages/pip* \
        /usr/local/lib/python3.11/site-packages/setuptools* \
        /usr/local/lib/python3.11/site-packages/wheel* \
        /usr/local/lib/python3.11/site-packages/pkg_resources \
        /usr/local/lib/python3.11/site-packages/_distutils_hack \
        /opt/venv/lib/python3.11/site-packages/pip* \
        /opt/venv/lib/python3.11/site-packages/setuptools* \
        /opt/venv/lib/python3.11/site-packages/pkg_resources \
        /opt/venv/lib/python3.11/site-packages/_distutils_hack \
    && mkdir -p /app/instance \
    && chown -R nonroot:nonroot /app/instance

USER nonroot

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2)"]

ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
