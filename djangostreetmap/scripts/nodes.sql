CREATE OR REPLACE FUNCTION overpass_import_nodes (new record)
    RETURNS void
    AS $$
BEGIN
    INSERT INTO djangostreetmap_osmnode AS node (id, lat, lon)
    SELECT DISTINCT ON (node_id)
        node_id,
        lon,
        lat
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//osm/node' passing data columns "node_id" bigint path '@id', "lon" float path '@lat', "lat" float path '@lat')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT ON CONSTRAINT djangostreetmap_osmnode_pkey
        DO UPDATE SET
            lat = excluded.lat,
            lon = excluded.lon
        WHERE
            node.id = excluded.id;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION overpass_import_ways (new record)
    RETURNS void
    AS $$
BEGIN
    INSERT INTO djangostreetmap_osmway AS way (id)
    SELECT DISTINCT
        (xmltable.id)
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//way' passing data columns "id" int path '@id')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT
        DO NOTHING;
END;
$$
LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION overpass_import_relations (new record)
    RETURNS void
    AS $$
BEGIN
    INSERT INTO djangostreetmap_osmrelation AS relation (id)
    SELECT DISTINCT
        (xmltable.id)
    FROM
        djangostreetmap_osmxmlimport,
        xmltable('//relation' passing data columns "id" int path '@id')
    WHERE
        djangostreetmap_osmxmlimport.id = NEW.id
    ON CONFLICT
        DO NOTHING;
END;
$$
LANGUAGE 'plpgsql';
