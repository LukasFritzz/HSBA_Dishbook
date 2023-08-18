import mysql.connector

host        = "XXX.XXX.XXX.XXX"
user        = "XXXXXXXXXXXXXXX"
password    = "XXXXXXXXXXXXXXX"
database    = "XXXXXXXXXXXXXXX"

def execute_sql_query(statement, values=None, fetch=True):
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = connection.cursor()
        
        if values:
            if isinstance(values[0], (list, tuple)):
                cursor.executemany(statement, values)
            else:
                cursor.execute(statement, values)
        else:
            cursor.execute(statement)

        if fetch:
            results = cursor.fetchall()
        else:
            results = None

        if not fetch:
            connection.commit()

        cursor.close()
        connection.close()

        return results

    except mysql.connector.Error as err:
        print("Error:", err)
        return None