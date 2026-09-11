FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
ENV FLAG=flag{phantom_sqli_bypass_missing}
EXPOSE 80
CMD ["python", "app.py"]
