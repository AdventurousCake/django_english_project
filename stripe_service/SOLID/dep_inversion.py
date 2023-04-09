"""Зависимость на Абстракциях. Нет зависимости на что-то конкретное"""


class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def execute_query(self, query):
        # execute the query using the connection string
        pass


class Logger:
    def __init__(self, log_file):
        self.log_file = log_file

    def log(self, message):
        # write the message to the log file
        pass


class UserRepository:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger

    def create_user(self, user):
        try:
            # insert the user into the database
            self.database.execute_query("INSERT INTO users (name, email) VALUES (%s, %s)", (user.name, user.email))
            self.logger.log("User created: {}".format(user.name))
        except Exception as e:
            self.logger.log("Error creating user: {}".format(str(e)))


class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email
