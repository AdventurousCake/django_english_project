FROM python:3.11-alpine

RUN addgroup -S app_user && adduser -S app_user -G app_user
#RUN adduser -D app_user

# set work directory
ENV APP_HOME=/usr/src/app
RUN mkdir $APP_HOME && \
    mkdir $APP_HOME/static && \
    mkdir $APP_HOME/media

WORKDIR $APP_HOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

## install psycopg2 dependencies
#RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy project
COPY . .

RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# chown all the files to the app user
RUN chown -R app_user:app_user $APP_HOME
USER app_user

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
