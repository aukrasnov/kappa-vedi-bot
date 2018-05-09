import psycopg2
from datetime import datetime


class DBConnector:
    def __init__(self, db_url, initial_queries=None):
        self.db_url = db_url
        self.conn = None
        self.initial_queries = initial_queries or []
        
    def add_initial_query(self, query):
        self.initial_queries.append(query)

    def get_connection(self, force_update=False):
        if self.conn is None or self.conn.closed or force_update:
            try:
                self.conn = psycopg2.connect(self.db_url)
                cur = self.conn.cursor()
                for query in self.initial_queries:
                    cur.execute(query)
                self.conn.commit()
            except Exception:
                self.conn = None
        return self.conn

    def sql_get(self, query):
        conn = self.get_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute(query)
            result = cur.fetchall()
            return result
        return None

    def sql_set(self, query):
        conn = self.get_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()

    def sql_set_get(self, query):
        conn = self.get_connection()
        if conn is not None:
            cur = conn.cursor()
            cur.execute(query)
            conn.commit()
            result = cur.fetchall()
            return result
        return None


class DBLogger:
    def __init__(self, connector):
        self.connector = connector
        self.connector.add_initial_query("CREATE TABLE IF NOT EXISTS dialog(chat_id varchar, user_name varchar, query varchar, response varchar, actualtime timestamp)")
    
    def log_message(self, message, response=None):
        query = "INSERT INTO dialog VALUES('{}', '{}', '{}', '{}', TIMESTAMP '{}')".format(
            message.chat.id,
            message.chat.username,
            message.text,
            response,
            datetime.now()
        )
        self.connector.sql_set(query)


class GroupManager:
    def __init__(self, connector):
        self.connector = connector
        self.users = []
        self.admins = []
        self.update_groups()
    
    def update_groups(self):
        # todo: connect to database or Google Sheets
        self.users = ["cointegrated", "helmeton", "Stepan_Ivanov"]
        self.admins = ["cointegrated", "helmeton", "Stepan_Ivanov"]

    def get_chat_id_for_users(self, usernames):
        query = "SELECT DISTINCT user_name, chat_id FROM dialog"
        results = self.connector.sql_get(query)
        if results is None:
            results = []
        results = dict(results)
        return [results.get(username) for username in usernames]


class EventManager:
    def __init__(self, connector):
        self.connector = connector
        self.connector.add_initial_query(
            "CREATE TABLE IF NOT EXISTS club_event (event_id SERIAL PRIMARY KEY, place VARCHAR , planned_time TIMESTAMP , program VARCHAR , cost VARCHAR )")
        self.update_events()

    def update_events(self):
        pass

    def add_event(self, event):
        query = "INSERT INTO club_event(place, planned_time, program, cost) VALUES('{}', '{}', '{}', '{}') RETURNING event_id".format(
            event['place'],
            event['time'],
            event['program'],
            event['cost'],
        )
        results = self.connector.sql_set_get(query)
        if results:
            return results[0][0]
        return None
