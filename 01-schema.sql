-- DROP SCHEMA public;

COMMENT ON SCHEMA public IS 'standard public schema';

-- DROP SEQUENCE public.edges_edge_id_seq;

-- Drop table

-- DROP TABLE public.graph;

CREATE TABLE public.graph (
	graph_id serial4 NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT graph_pk PRIMARY KEY (graph_id)
);


-- public.nodes определение

-- Drop table

-- DROP TABLE public.nodes;

CREATE TABLE public.nodes (
	node_id serial4 NOT NULL,
	"name" varchar NOT NULL,
	graph_id int4 NOT NULL,
	CONSTRAINT nodes_pk PRIMARY KEY (node_id),
	CONSTRAINT nodes_graph_fk FOREIGN KEY (graph_id) REFERENCES public.graph(graph_id)
);
CREATE INDEX idx_nodes_graph ON public.nodes USING btree (graph_id);


-- public.edges определение

-- Drop table

-- DROP TABLE public.edges;

CREATE TABLE public.edges (
	edge_id serial4 NOT NULL,
	"source" int4 NOT NULL,
	target int4 NOT NULL,
	CONSTRAINT edges_pk PRIMARY KEY (edge_id),
	CONSTRAINT edges_nodes_fk FOREIGN KEY ("source") REFERENCES public.nodes(node_id) ON DELETE CASCADE,
	CONSTRAINT edges_nodes_fk1 FOREIGN KEY (target) REFERENCES public.nodes(node_id) ON DELETE CASCADE
);



-- DROP FUNCTION public.add_graph(json, json);

CREATE OR REPLACE FUNCTION public.add_graph(nodes_json json, edges_json json)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    new_graph_id INT;
    node_map JSONB = '{}'::JSONB;
BEGIN
    INSERT INTO graph ("name")
    VALUES ('graph')
    RETURNING graph_id INTO new_graph_id;


    WITH inserted_nodes AS (
        INSERT INTO nodes (name, graph_id)
        SELECT
            (n->>'name')::VARCHAR,
            new_graph_id
        FROM json_array_elements(nodes_json) AS n
        RETURNING node_id, name
    )
    SELECT jsonb_object_agg(name, node_id)
    INTO node_map
    FROM inserted_nodes;


    INSERT INTO edges ("source", target)
    SELECT
        (node_map->>(e->>'source'))::int4,
        (node_map->>(e->>'target'))::int4
    FROM json_array_elements(edges_json) AS e;

    RETURN new_graph_id;


EXCEPTION
    WHEN others THEN
        RAISE EXCEPTION 'Ошибка создания графа: %', SQLERRM;
END;
$function$
;

-- DROP FUNCTION public.delete_node(int4, varchar);

CREATE OR REPLACE FUNCTION public.delete_node(graph_id_in integer, node_name character varying)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
	IF NOT EXISTS (SELECT 1 FROM graph g WHERE g.graph_id = graph_id_in) THEN
        RAISE EXCEPTION 'Не найден граф с id %', graph_id_in;
    END IF;

	PERFORM n.node_id FROM nodes n WHERE n.graph_id = graph_id_in AND n."name" = node_name;

	IF NOT FOUND THEN
        RAISE EXCEPTION 'Для графа % не найден узел по имени %', graph_id_in, node_name;
    END IF;

	IF (SELECT COUNT(n.node_id) FROM nodes n WHERE n.graph_id = graph_id_in) > 1 THEN
		DELETE FROM nodes n WHERE n.graph_id = graph_id_in AND n."name" = node_name;
	ELSE
		RAISE EXCEPTION 'У графа должно быть не менее одного узла';
	END IF;

	-- RETURN json_build_object('message', 'Узел успешно удалён');
	EXCEPTION
	    WHEN others THEN
	        RAISE EXCEPTION 'Ошибка удаления узла: %', SQLERRM;
END;
$function$
;

-- DROP PROCEDURE public.drop_tables();

CREATE OR REPLACE PROCEDURE public.drop_tables()
 LANGUAGE sql
AS $function$
	TRUNCATE graph, edges, nodes RESTART IDENTITY CASCADE;
$function$
;


-- DROP FUNCTION public.get_adjacency_list(int4);

CREATE OR REPLACE FUNCTION public.get_adjacency_list(graph_id_in integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
    result_out JSON;
BEGIN
	IF NOT EXISTS (SELECT 1 FROM graph WHERE graph_id = graph_id_in) THEN
        RAISE EXCEPTION 'Не найден граф с id %', id_in;
    END IF;

    SELECT jsonb_object_agg(
        source_name,
        COALESCE(target_names, '[]'::JSONB)
    ) INTO result_out
    FROM (
        SELECT
            src."name" AS source_name,
            COALESCE(jsonb_agg(DISTINCT trg."name" ORDER BY trg."name") FILTER (WHERE trg."name" IS NOT NULL), '[]'::JSONB) AS target_names
        FROM nodes src
        LEFT JOIN edges e
            ON src.node_id = e."source"
        LEFT JOIN nodes trg
            ON e.target = trg.node_id
        WHERE src.graph_id = graph_id_in
        GROUP BY src."name"
    ) AS subq;

    RETURN result_out;

EXCEPTION
    WHEN others THEN
        RAISE EXCEPTION 'Ошибка получения списка смежности: %', SQLERRM;
END;
$function$
;

-- DROP FUNCTION public.get_graph(int4);

CREATE OR REPLACE FUNCTION public.get_graph(id_in integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
    nodes_json JSON;
    edges_json JSON;
BEGIN
    IF NOT EXISTS (SELECT 1 FROM graph WHERE graph_id = id_in) THEN
        RAISE EXCEPTION 'Не найден граф с id %', id_in;
    END IF;

    SELECT json_agg(json_build_object('name', name))
    INTO nodes_json
    FROM nodes
    WHERE graph_id = id_in;

    SELECT json_agg(json_build_object(
        'source', (SELECT name FROM nodes WHERE node_id = e.source),
        'target', (SELECT name FROM nodes WHERE node_id = e.target)
    ))
    INTO edges_json
    FROM edges e
	JOIN nodes n ON e."source" = n.node_id
    WHERE n.graph_id = id_in;

    RETURN json_build_object(
        'nodes', COALESCE(nodes_json, '[]'::JSON),
        'edges', COALESCE(edges_json, '[]'::JSON)
    );
END;
$function$
;

-- DROP FUNCTION public.get_transposed_adjacency_list(int4);

CREATE OR REPLACE FUNCTION public.get_transposed_adjacency_list(graph_id_in integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
    result_out JSON;
BEGIN
    -- Проверка существования графа
    IF NOT EXISTS (SELECT 1 FROM graph WHERE graph_id = graph_id_in) THEN
        RAISE EXCEPTION 'Граф с ID % не найден', graph_id_in;
    END IF;

    -- Формирование транспонированного списка смежности
    SELECT jsonb_object_agg(
        target_name,
        COALESCE(source_names, '[]'::JSONB)
    ) INTO result_out
    FROM (
        SELECT
            trg."name" AS target_name,
            COALESCE(
                jsonb_agg(DISTINCT src."name" ORDER BY src."name") FILTER (WHERE src."name" IS NOT NULL),
                '[]'::JSONB
            ) AS source_names
        FROM nodes trg
        LEFT JOIN edges e
            ON trg.node_id = e.target
        LEFT JOIN nodes src
            ON e."source" = src.node_id
        WHERE trg.graph_id = graph_id_in
        GROUP BY trg."name"
    ) AS subq;

    RETURN result_out;

EXCEPTION
    WHEN others THEN
        RAISE EXCEPTION 'Ошибка получения транспонированного списка смежности: %', SQLERRM;
END;
$function$
;


CREATE ROLE "user" WITH
	NOSUPERUSER
	NOCREATEDB
	NOCREATEROLE
	NOINHERIT
	LOGIN
	NOREPLICATION
	NOBYPASSRLS
    PASSWORD '1357920_user'
	CONNECTION LIMIT -1;

GRANT EXECUTE ON FUNCTION add_graph(json, json) TO "user";
GRANT EXECUTE ON FUNCTION delete_node(int4, varchar) TO "user";
GRANT SELECT, INSERT, REFERENCES, DELETE ON TABLE edges TO "user";
GRANT USAGE ON SEQUENCE edges_edge_id_seq TO "user";
GRANT EXECUTE ON FUNCTION get_adjacency_list(int4) TO "user";
GRANT EXECUTE ON FUNCTION get_graph(int4) TO "user";
GRANT EXECUTE ON FUNCTION get_transposed_adjacency_list(int4) TO "user";
GRANT SELECT, INSERT ON TABLE graph TO "user";
GRANT USAGE ON SEQUENCE graph_graph_id_seq TO "user";
GRANT SELECT, INSERT, REFERENCES, DELETE ON TABLE nodes TO "user";
GRANT USAGE ON SEQUENCE nodes_node_id_seq TO "user";
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT USAGE ON SEQUENCES TO "user";

