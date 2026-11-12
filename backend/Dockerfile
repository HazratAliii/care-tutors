FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

# Seed the database, then start the API.
CMD ["sh", "-c", "python seed.py && FLASK_HOST=0.0.0.0 python app.py"]
