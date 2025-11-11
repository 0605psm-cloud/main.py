# ------------------------------------------------------------
# FastAPI Cloud Run Dockerfile (수정본)
# ------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
ENV PORT=8080

# FastAPI 실행 명령 — 반드시 reload 끄고, workers=1 지정
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
