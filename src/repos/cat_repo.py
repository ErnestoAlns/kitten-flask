from ..models.cat_model import Cat

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
        sql = 'INSERT INTO cat (name, color, color_eye) values (%s, %s, %s)'
        values = (data.name, data.color, data. color_eye)
        cursor.execute(sql, values)
        cursor.commit()



