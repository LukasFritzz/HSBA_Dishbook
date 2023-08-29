import  mysql.connector
import  static.py.keys  as keys

def execute_sql_query(statement, values=None, fetch=True):
    try:
        connection = mysql.connector.connect(
            host        = keys.host
            ,user       = keys.dbUser
            ,password   = keys.dbPassword
            ,database   = keys.database
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