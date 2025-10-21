FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install --with-deps  # Ensures browsers and deps
COPY . .
CMD ["python", "main.py"]