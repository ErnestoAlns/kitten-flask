from ..models.cat_model import Cat
from mysql.connector import Error

class CatRepo:

    def get_all(self, connection):
        cursor = connection.cursor(dictionary=True)
        sql = 'SELECT * FROM cat'
        cursor.execute(sql)
        sql_data_rows = cursor.fetchall()
        cursor.close() # Cierra el cursor
        return sql_data_rows

    def get_by_id(self, connection, cat_id: int):
        cursor = connection.cursor(dictionary=True)
        sql = 'SELECT id, name, color, color_eye FROM cat WHERE id = %s'
        value = [cat_id]
        cursor.execute(sql, value)
        sql_data_row = cursor.fetchone()
        if sql_data_row is None:
            return None
        CATS = Cat.model_validate(sql_data_row)
        cursor.close()
        return CATS

    def insert_cat(self, connection, data):
        cursor = connection.cursor(dictionary=True)
        sql = 'INSERT INTO cat (name, color, color_eye) values (%(name)s, %(color)s, %(color_eye)s)'
        try:
            cursor.execute(sql, data.model_dump())
            connection.commit()
        finally:
            cursor.close()

    def update_cat(self, connection, data):
        sql = 'UPDATE cat SET name = %(name)s, color = %(color)s, color_eye = %(color_eye)s WHERE id = %(id)s'
        with connection.cursor(dictionary=True) as cursor:
            try: 
                cursor.execute(sql, data)
                connection.commit()
                return cursor.rowcount
            except Error as e:
                print(f"Error Updating cat: {e}")
                connection.rollback()
                raise

    def delete_cat(self, connection, id):
        cursor = connection.cursor(dictionary=True)
        sql = 'DELETE FROM cat WHERE id = %s'
        with connection.cursor() as cursor:
            try:
                cursor.execute(sql, [int(id)]) 
                connection.commit()
                return cursor.rowcount 

            except Error as e: 
                print(f"Error al ejecutar DELETE: {e}")
                connection.rollback()
                raise






