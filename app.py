import json

import psycopg2

from queries import call_func, add_graph_query, is_graph_acyclic, parse_adjacency_list
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(debug=True)


from validators import GraphData


@app.post("/api/graph/")
async def create_graph(data: GraphData):
    nodes = [n.model_dump() for n in data.nodes]
    edges = [e.model_dump() for e in data.edges]

    if not is_graph_acyclic(nodes, edges):
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", "edges"],
                "msg": "Граф не должен быть циклическим!",
                "type": "graph_cycle_error"
            }]
        )

    try:
        graph_id = add_graph_query(nodes, edges)
        return JSONResponse(
            status_code=201,
            content={"id": graph_id}
        )
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=400,
            content={"message": str(e)}
        )


@app.get("/api/graph/{graph_id}/")
def read_graph(graph_id: int):
    try:
        response_json: dict = call_func('get_graph', graph_id)
        return JSONResponse(
            status_code=200,
            content={"id": graph_id, **response_json}
        )
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=404,
            content={"message": str(e)}
        )


@app.get("/api/graph/{graph_id}/adjacency_list")
def read_graph_adjacency_list(graph_id: int):
    try:
        response_json = call_func('get_graph', graph_id)
        nodes: list[dict] = response_json["nodes"]
        edges: list[dict] = response_json["edges"]
        return JSONResponse(
            status_code=200,
            content={"adjacency_list": parse_adjacency_list(nodes, edges)}
        )
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=404,
            content={"message": str(e)}
        )


@app.get("/api/graph/{graph_id}/reverse_adjacency_list")
def api_graph_reverse_adjacency_list(graph_id: int):
    return {"graph_id": graph_id, "messege": "reverse_adjacency_list"}


@app.delete("/api/graph/{graph_id}/node/{node_name}")
def api_graph(graph_id: int, node_name: str):
    call_func('delete_node', graph_id, node_name)
    return {"graph_id": graph_id, "node_name": node_name, "messege": "delete_node"}
