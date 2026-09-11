FROM python:3.11-alpine
WORKDIR /app
RUN pip install --no-cache-dir flask pillow
RUN mkdir -p /app/static
COPY generate.py app.py ./
ENV FLAG=flag{phantom_stego_recovered_missing}
RUN python generate.py
EXPOSE 80
CMD ["sh", "-c", "python generate.py && python app.py"]
