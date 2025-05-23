from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, field_validator
from typing import List

from fastapi.responses import JSONResponse
from starlette.requests import Request

import app


@app.app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_mapping = {
        "missing": "Поле обязательно для заполнения",
        "string_too_short": "Имя узла не может быть пустым",
        "too_short": "Граф должен содержать минимум 1 узел",
        "value_error": "Ошибка валидации",
        "int_parsing": "Вводимое значение должно быть целым числом"
    }

    formatted_errors = []
    for error in exc.errors():
        error_type = error["type"].split(".")[-1]
        msg = error.get("msg", "")

        # Извлекаем контекст для форматирования
        ctx = error.get("ctx", {})

        # Кастомные сообщения
        if "Имена узлов должны быть уникальными" in msg:
            custom_msg = "Имя узла графа должно быть уникальным"
        elif "Узел '" in msg:
            custom_msg = msg
        else:
            custom_msg = error_mapping.get(error_type, msg)

        # Форматирование с контекстом
        try:
            custom_msg = custom_msg.format(**ctx)
        except:
            pass

        formatted_errors.append({
            "loc": error["loc"],
            "msg": custom_msg,
            "type": error_type
        })

    return JSONResponse(
        status_code=422,
        content={"detail": formatted_errors}
    )


class Node(BaseModel):
    name: str = Field(..., min_length=1)


class Edge(BaseModel):
    source: str = Field(...)
    target: str = Field(...)


class GraphData(BaseModel):
    nodes: List[Node] = Field(..., min_length=1)
    edges: List[Edge] = Field(default_factory=list)

    @field_validator("nodes", mode='before')
    @classmethod
    def validate_nodes(cls, nodes: List[Node]) -> List[Node]:
        names = [node["name"] for node in nodes]
        if len(names) != len(set(names)):
            raise ValueError("Имена узлов должны быть уникальными")
        return nodes

    @field_validator("edges")
    @classmethod
    def validate_edges(cls, edges: List[Edge], values) -> List[Edge]:
        node_names = {node.name for node in values.data.get("nodes", [])}
        for edge in edges:
            if edge.source not in node_names:
                raise ValueError(f"Узел '{edge.source}' не существует")
            if edge.target not in node_names:
                raise ValueError(f"Узел '{edge.target}' не существует")
        return edges
