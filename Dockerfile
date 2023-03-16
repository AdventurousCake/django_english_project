# pull official base image
FROM python:3.11-alpine

# set work directory
ENV APP_HOME=/usr/src/app
WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## install psycopg2 dependencies
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
RUN mkdir $APP_HOME/staticfiles

RUN adduser -D app_user
USER app_user

# run entrypoint.sh
ENTRYPOINT ["$APP_HOME/entrypoint.sh"]
