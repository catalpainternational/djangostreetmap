CREATE OR REPLACE FUNCTION overpass_import_node_tags (new record)
    RETURNS void
    AS $$
BEGIN
    UPDATE
        djangostreetmap_osmnode
    SET
        tags = tags_query.tags
    FROM (
        SELECT
            xmltable.id,
            jsonb_object_agg(k, v) AS tags
        FROM
            djangostreetmap_osmxmlimport,
            xmltable('//osm/node/tag' passing data columns "id" bigint path '../@id', "k" text path '@k', "v" text path '@v')
        WHERE
            djangostreetmap_osmxmlimport.id = NEW.id
        GROUP BY
            xmltable.id) tags_query
WHERE
    tags_query.id = djangostreetmap_osmnode.id;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION overpass_import_way_tags (new record)
    RETURNS void
    AS $$
BEGIN
    UPDATE
        djangostreetmap_osmway
    SET
        tags = tags_query.tags
    FROM (
        SELECT
            xmltable.id,
            jsonb_object_agg(k, v) AS tags
        FROM
            djangostreetmap_osmxmlimport,
            xmltable('//osm/way/tag' passing data columns "id" bigint path '../@id', "k" text path '@k', "v" text path '@v')
        WHERE
            djangostreetmap_osmxmlimport.id = NEW.id
        GROUP BY
            xmltable.id) tags_query
WHERE
    tags_query.id = djangostreetmap_osmway.id;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION overpass_import_relation_tags (new record)
    RETURNS void
    AS $$
BEGIN
    UPDATE
        djangostreetmap_osmrelation
    SET
        tags = tags_query.tags
    FROM (
        SELECT
            xmltable.id,
            jsonb_object_agg(k, v) AS tags
        FROM
            djangostreetmap_osmxmlimport,
            xmltable('//osm/relation/tag' passing data columns "id" bigint path '../@id', "k" text path '@k', "v" text path '@v')
        WHERE
            djangostreetmap_osmxmlimport.id = NEW.id
        GROUP BY
            xmltable.id) tags_query
WHERE
    tags_query.id = djangostreetmap_osmrelation.id;
END;
$$
LANGUAGE 'plpgsql';
