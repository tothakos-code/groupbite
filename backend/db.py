import psycopg2
from collections import Counter
import logging
import datetime
import time

def db_connection():
    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(
    host="database",
    database="falusi",
    user="falusi",
    password="falusi")
    return conn

def get_row_count(sql_to_run, tuple=None):
    conn = None
    try:
        conn = db_connection()
        logging.info('Database connection opened.')

        cur = conn.cursor()

        if tuple == None:
            cur.execute(sql_to_run)
        else:
            cur.execute(sql_to_run, tuple)
        conn.commit()

        result = cur.rowcount
        # close the communication with the PostgreSQL
        cur.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
            logging.error('Database transaction error: ' + str(error))
    finally:
        if conn is not None:
            conn.close()
            logging.info('Database connection closed.')

def run_sql(sql_to_run, tuple=None, fetch='all'):
    conn = None
    try:
        conn = db_connection()
        logging.info('Database connection opened.')

        cur = conn.cursor()

        if tuple == None:
            cur.execute(sql_to_run)
        else:
            cur.execute(sql_to_run, tuple)
        conn.commit()

        result = None

        if fetch == 'one':
            result = cur.fetchone()
        elif fetch == 'all':
            result = cur.fetchall()
        else:
            result = cur.fetchall()

        # close the communication with the PostgreSQL
        cur.close()
        return result
    except (Exception, psycopg2.DatabaseError) as error:
            logging.error('Database transaction error: ' + str(error))
    finally:
        if conn is not None:
            conn.close()
            logging.info('Database connection closed.')


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
