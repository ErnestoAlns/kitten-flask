import mysql.connector
from flask import g
from .config import get_db_config

def get_db_connection():
    if 'db_connection' not in g:
        config = get_db_config()
        try:
            g.db_connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            raise RuntimeError(f"Database connection failed: {err}")
    return g.db_connection

def close_db_connection(e=None):
    db = g.pop('db_connection', None)
    if db is not None:
        db.close()

# Nota: El cursor ya no se necesita aquí. Se crea en el Repositorio, 
# usando g.db_connection.cursor(dictionary=True)
