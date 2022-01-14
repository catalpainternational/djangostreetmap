CREATE OR REPLACE FUNCTION overpass_import_osmnodeway (new record)
    RETURNS void
    AS $$
BEGIN
    DELETE FROM djangostreetmap_osmnodeway
    WHERE way_id IN (
            SELECT
                xmltable.id
            FROM
                djangostreetmap_osmxmlimport,
                xmltable('//way' passing data columns "id" bigint path '@id')
            WHERE
                djangostreetmap_osmxmlimport.id = NEW.id);
    --ensure that referenced nodes ('nd' tags) exist in the nodes table
    INSERT INTO djangostreetmap_osmnode (id)
    SELECT
        node_id
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//way/nd' passing data columns node_id bigint path '@ref')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT
        DO NOTHING;
    INSERT INTO djangostreetmap_osmnodeway (way_id, node_id, ORDINALITY)
    SELECT
        xmltable.id,
        node_id,
        ord
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//way/nd' passing data columns "id" bigint path '../@id', node_id bigint path '@ref', ord FOR ORDINALITY)
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION overpass_import_osmrelationmembers (new record)
    RETURNS void
    AS $$
BEGIN
    DELETE FROM djangostreetmap_osmrelationmember
    WHERE relation_id IN (
            SELECT
                relation_id
            FROM
                djangostreetmap_osmxmlimport,
                xmltable('//osm/relation' passing data columns "relation_id" bigint path '@id')
            WHERE
                djangostreetmap_osmxmlimport.id = NEW.id);
    --ensure that referenced nodes and ways in 'member' tags exist in the nodes table
    INSERT INTO djangostreetmap_osmnode (id)
    SELECT
        node_id
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//osm/relation/member[@type="node"]' passing data columns node_id bigint path '@ref')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT
        DO NOTHING;
    INSERT INTO djangostreetmap_osmway (id)
    SELECT
        way_id
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//osm/relation/member[@type="way"]' passing data columns way_id bigint path '@ref')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT
        DO NOTHING;
    WITH instances AS (
        SELECT
            xmltable.*
        FROM
            djangostreetmap_osmxmlimport,
            xmltable('//osm/relation/member' passing data columns "relation_id" bigint path '../@id', "type" text path '@type', "ref" bigint path '@ref', ROLE text path '@role', ORDINALITY FOR ORDINALITY)
        WHERE
            djangostreetmap_osmxmlimport.id = NEW.id)
    INSERT INTO djangostreetmap_osmrelationmember (node_id, way_id, ROLE, relation_id, ORDINALITY)
    SELECT
        CASE WHEN TYPE = 'node' THEN
            ref
        ELSE
            NULL
        END AS node_id,
        CASE WHEN TYPE = 'way' THEN
            ref
        ELSE
            NULL
        END AS way_id,
        ROLE,
        relation_id,
        ORDINALITY
    FROM
        instances;
END;
$$
LANGUAGE 'plpgsql';
