import psycopg2


def connect_db():
    try:
        conn = psycopg2.connect(
            database="ethereum",
            user="postgres",
            password="postgres",
            host="127.0.0.1",
            port="5432",
        )
        cur = conn.cursor()

        return conn, cur
    except Exception as error:
        print(f"Error: {error}")


def close_db(conn, cur):
    cur.close()
    conn.close()


# 3. Define functions
def insert_data(fromAddress, toAddress, transferValue, timestamp):
    conn, cur = connect_db()

    sql = "INSERT INTO transactions (fromAddress, toAddress, transferValue, timestamp)"
    data = (fromAddress, toAddress, transferValue, timestamp)
    cur.execute(sql, data)

    cur.commit()
    close_db(conn, cur)
