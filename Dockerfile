FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install-deps
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
RUN playwright install firefox
COPY . .
CMD ["python", "main.py"]