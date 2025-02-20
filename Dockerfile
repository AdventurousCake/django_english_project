# build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade setuptools \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefer-binary --user -r requirements.txt

# use build
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN python manage.py migrate --settings=prod_settings && python manage.py collectstatic --noinput
RUN python manage.py collectstatic --noinput
