# ------------------------------------------------------------
# FastAPI Cloud Run Dockerfile
# ------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
ENV PORT=8080

# 핵심 부분: FastAPI 엔트리포인트를 명시적으로 지정
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}
