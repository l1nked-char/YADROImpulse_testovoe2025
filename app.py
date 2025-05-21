from fastapi import FastAPI, HTTPException
from queries import call_func, add_graph_query


app = FastAPI(debug=True)


@app.post("/api/graph/")
def add_graph(data: dict):
    list_of_nodes = data["nodes"]
    if list_of_nodes is None or len(list_of_nodes) == 0:
        return HTTPException(status_code=404, detail="No nodes found")
    list_of_edges = data["edges"]

    graph_id: int = add_graph_query(list_of_nodes, list_of_edges)
    return {"id": graph_id}


@app.get("/api/graph/{graph_id}/")
def read_graph(graph_id: int):
    response_json = call_func('get_graph', graph_id)
    if response_json is None:
        raise HTTPException(status_code=404, detail="Graph not found")
    return response_json


@app.get("/api/graph/{graph_id}/adjacency_list")
def read_graph_adjacency_list(graph_id: int, name: str = None):
    return {"graph_id": graph_id, "name": name, "messege": "adjacency_list"}


@app.get("/api/graph/{graph_id}/reverse_adjacency_list")
def api_graph_reverse_adjacency_list(graph_id: int, name: str = None):
    return {"graph_id": graph_id, "name": name, "messege": "reverse_adjacency_list"}


@app.delete("/api/graph/{graph_id}/node/{node_name}")
def api_graph(graph_id: int, node_name: str):
    call_func('delete_node', graph_id, node_name)
    return {"graph_id": graph_id, "node_name": node_name, "messege": "delete_node"}
