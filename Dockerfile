FROM python:3.10-slim

WORKDIR /app
EXPOSE 8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "finara_agent.main:app", "--host", "0.0.0.0", "--port", "8080"]