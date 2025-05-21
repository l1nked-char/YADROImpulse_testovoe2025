import psycopg2
from config import DB_CONFIG
import json


def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as _:
        print(f"Ошибка подключения к базе")
        return None


def call_func(func_name: str, *args):
    conn = None
    cursor = None
    try:
        conn = connect_db()
        if not conn:
            return None

        cursor = conn.cursor()
        query: str = f'SELECT * FROM {func_name}(' + ','.join(['%s' for _ in range(len(args))]) + ')'
        cursor.execute(query, args)
        result_set = cursor.fetchall()[0][0]
        conn.commit()
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Ошибка PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result_set


def add_graph_query(nodes_data, edges_data):
    conn = None
    cursor = None
    try:
        conn = connect_db()
        if conn is None:
            return None
        cursor = conn.cursor()

        nodes_json = json.dumps(nodes_data)
        edges_json = json.dumps(edges_data)

        cursor.execute(
            'SELECT * FROM public.add_graph(%s::JSON, %s::JSON)',
            (nodes_json, edges_json)
        )

        new_graph_id = cursor.fetchone()[0]
        conn.commit()

        return new_graph_id

    except psycopg2.Error as e:
        print(f"Ошибка PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
