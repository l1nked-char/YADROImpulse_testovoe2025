import psycopg2
from fastapi.exceptions import RequestValidationError

from api.queries import call_func, add_graph_query, is_graph_acyclic
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from api.validators import GraphData
from starlette.requests import Request


app = FastAPI(debug=True)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    error_mapping = {
        "missing": "Поле обязательно для заполнения",
        "string_too_short": "Имя узла не может быть пустым",
        "too_short": "Граф должен содержать минимум 1 узел",
        "int_parsing": "Вводимое значение должно быть целым числом"
    }

    formatted_errors = []
    for error in exc.errors():
        error_type = error["type"].split(".")[-1]
        msg = error.get("msg", "")

        if "Узел '" in msg:
            custom_msg = msg
        else:
            custom_msg = error_mapping.get(error_type, msg)

        formatted_errors.append({
            "loc": error["loc"],
            "msg": custom_msg,
            "type": error_type
        })

    return JSONResponse(
        status_code=422,
        content={"detail": formatted_errors}
    )


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
        graph_id = await add_graph_query(nodes, edges)
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
async def read_graph(graph_id: int):
    try:
        response_json: dict = await call_func('get_graph', graph_id)
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
async def read_graph_adjacency_list(graph_id: int):
    try:
        response_json = await call_func('get_adjacency_list', graph_id)
        return JSONResponse(
            status_code=200,
            content={"adjacency_list": response_json}
        )
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=404,
            content={"message": str(e)}
        )


@app.get("/api/graph/{graph_id}/reverse_adjacency_list")
async def api_graph_reverse_adjacency_list(graph_id: int):
    try:
        response_json = await call_func('get_transposed_adjacency_list', graph_id)
        return JSONResponse(
            status_code=200,
            content={"adjacency_list": response_json}
        )
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=404,
            content={"message": str(e)}
        )


@app.delete("/api/graph/{graph_id}/node/{node_name}", status_code=204)
async def api_graph(graph_id: int, node_name: str):
    try:
        await call_func('delete_node', graph_id, node_name)
        return "Узел успешно удалён"
    except psycopg2.Error as e:
        return JSONResponse(
            status_code=404,
            content={"message": str(e)}
        )
