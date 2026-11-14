FROM python:3.11-slim
WORKDIR /srv/evidencelab
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 EVIDENCELAB_DB_PATH=/srv/evidencelab/data/evidencelab.sqlite3
COPY pyproject.toml README.md ./
COPY app ./app
RUN pip install --no-cache-dir .
RUN mkdir -p /srv/evidencelab/data
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
