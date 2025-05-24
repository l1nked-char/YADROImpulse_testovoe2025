import psycopg2
from config import DB_CONFIG
import json
from collections import defaultdict


def connect_db():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as _:
        raise psycopg2.Error("Ошибка подключения к базе!")


async def call_func(func_name: str, *args):
    conn = None
    cursor = None
    try:
        conn = connect_db()
        if not conn:
            return None

        cursor = conn.cursor()
        query: str = f'SELECT * FROM {func_name}(' + ','.join(['%s' for _ in range(len(args))]) + ')'
        cursor.execute(query, args)
        result_set: dict = cursor.fetchall()[0][0]
        conn.commit()
        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        raise psycopg2.Error(f"{e.pgerror.splitlines()[0]}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return result_set


async def add_graph_query(nodes_data: list[dict], edges_data: list[dict]) -> int:  # запрос на добавление графа
    conn = None
    cursor = None
    try:
        conn = connect_db()
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
        if conn:
            conn.rollback()
        raise psycopg2.Error(f"{e.pgerror.splitlines()[0]}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def is_graph_acyclic(nodes: list[dict], edges: list[dict]) -> bool:
    adj_list = defaultdict(list)
    for i in edges:
        adj_list[i["source"]].append(i["target"])
    # 0 - не проверен, 1 - проверяется сейчас, 2 - проверен
    visited = {node["name"]: 0 for node in nodes}

    def dfs(node):
        if visited[node] == 1:
            return False  # цикл
        if visited[node] == 2:
            return True  # проверенный узел

        visited[node] = 1  # проверяем сейчас
        for neighbor in adj_list[node]:
            if not dfs(neighbor):
                return False
        visited[node] = 2  # проверили
        return True

    # Проверяем все узлы
    for node in nodes:
        if visited[node["name"]] == 0:
            if not dfs(node["name"]):
                return False
    return True
