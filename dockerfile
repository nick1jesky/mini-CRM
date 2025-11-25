FROM python:3.14.0

WORKDIR /lead_distribution

COPY ./lead_distribution/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /lead_distribution

CMD ["python", "main.py"]