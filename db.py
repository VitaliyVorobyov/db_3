import psycopg2 as pg


class Connector:
    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database

    def connect(self):
        conn = pg.connect(
            user=f"{self.user}",
            password=f"{self.password}",
            host=f"{self.host}",
            port=f"{self.port}",
            database=f"{self.database}"
        )
        return conn


class Request(Connector):
    def __init__(self, user: str, password: str, host: str, port: str, database: str) -> None:
        super().__init__(user, password, host, port, database)

    def create_table(self):
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY ,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE
            );""")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS phones (
            id SERIAL PRIMARY KEY ,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            phone VARCHAR(255) UNIQUE NOT NULL
            );""")
            conn.commit()
        conn.close()

    def add_user(self, first_name: str, last_name: str, email: str) -> any:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO users (first_name, last_name, email) 
            VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING
            RETURNING id;""",
                        (first_name, last_name, email)
                        )
            conn.commit()
            try:
                return cur.fetchone()
            finally:
                conn.close()

    def add_phone(self, user_id: int, phone: str) -> any:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO phones (user_id, phone) 
            VALUES (%s, %s) 
            ON CONFLICT (phone) DO UPDATE SET user_id = EXCLUDED.user_id
            RETURNING id;""",
                        (user_id, phone)
                        )
            conn.commit()
            try:
                return cur.fetchone()
            finally:
                conn.close()

    def get_user(self, email: str = None, phone: str = None,
                 first_name: str = None, last_name: str = None) -> list:
        conn = self.connect()
        with conn.cursor() as cur:
            query = """
                    SELECT users.id, first_name, last_name, email, phone, phones.id
                    FROM users
                    LEFT JOIN phones on users.id = phones.user_id
                    WHERE TRUE
                    """
            params = []

            if email:
                query += " AND email = %s"
                params.append(email)
            if first_name:
                query += " AND first_name = %s"
                params.append(first_name)
            if last_name:
                query += " AND last_name = %s"
                params.append(last_name)
            if phone:
                query += " AND phone = %s"
                params.append(phone)

            cur.execute(query, params)
            try:
                return cur.fetchall()
            finally:
                conn.close()

    def edit_user(self, user_id: int, first_name: str or None = None, last_name: str or None = None,
                  email: str or None = None) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            query = """UPDATE users SET"""
            params = []

            if email:
                query += " email = %s,"
                params.append(email)
            if first_name:
                query += " first_name = %s,"
                params.append(first_name)
            if last_name:
                query += " last_name = %s,"
                params.append(last_name)
            params.append(user_id)
            query = query.rstrip(',')
            query += " WHERE id = %s;"
            cur.execute(query, params)
            conn.commit()
            conn.close()

    def delete_user(self, user_id: int) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"""
            DELETE FROM users
            WHERE id = %s;""",
                        (user_id,)
                        )
            conn.commit()
            conn.close()

    def delete_phone(self, user_id: int) -> None:
        conn = self.connect()
        with conn.cursor() as cur:
            cur.execute(f"""
            DELETE FROM phones
            WHERE user_id = %s;""",
                        (user_id,)
                        )
            conn.commit()
            conn.close()
