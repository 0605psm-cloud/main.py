# ------------------------------------------------------------
# ✅ FastAPI Cloud Run 완전 호환 Dockerfile
# ------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# 종속성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 복사
COPY . .

# Cloud Run은 내부적으로 PORT 환경 변수를 지정하므로 그대로 사용
EXPOSE 8080
ENV PORT=8080

# Uvicorn 실행 — 반드시 proxy-headers 포함
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --proxy-headers --forwarded-allow-ips="*"
