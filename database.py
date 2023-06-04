import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_table_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                id_user varchar(25) NOT NULL PRIMARY KEY,
                id_profile varchar(25) NOT NULL);"""
        )
    print("[INFO] Table USERS was created.")

def insert_data_users(id_user):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users (id_user) VALUES ('{id_user}');"""
        )

def insert_data_profiles(id_profile, offset):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users (id_profile) VALUES ('{id_profile}') OFFSET '{offset}';"""
        )

def select(offset):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT id_user, id_profile FROM users
            WHERE id_profile IS NULL
            OFFSET '{offset}';"""
        )
        return cursor.fetchone()

def drop_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS users CASCADE;"""
        )
        print('[INFO] Table USERS was deleted.')

def creating_database():
    create_table_users()
    drop_users()
