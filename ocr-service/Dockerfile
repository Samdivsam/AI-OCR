FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ARG PIP_TRUSTED_HOST=pypi.org files.pythonhosted.org pypi.python.org

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        libgl1 \
        libglib2.0-0 \
        libsm6 \
        libxext6 \
        libxrender1 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host pypi.python.org -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]


