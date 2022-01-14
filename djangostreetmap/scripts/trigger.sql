CREATE OR REPLACE FUNCTION overpass_import_func ()
    RETURNS TRIGGER
    AS $$
BEGIN
    PERFORM
        overpass_import_nodes (new);
    PERFORM
        overpass_import_node_tags (new);
    PERFORM
        overpass_import_ways (new);
    PERFORM
        overpass_import_way_tags (new);
    PERFORM
        overpass_import_relations (new);
    PERFORM
        overpass_import_relation_tags (new);
    PERFORM
        overpass_import_osmnodeway (new);
    PERFORM
        overpass_import_relations (new);
    PERFORM
        overpass_import_osmrelationmembers (new);
    RETURN new;
END
$$
LANGUAGE 'plpgsql';

DROP TRIGGER IF EXISTS overpass_import ON djangostreetmap_osmxmlimport;

CREATE TRIGGER overpass_import
    AFTER INSERT ON djangostreetmap_osmxmlimport
    FOR EACH ROW
    EXECUTE FUNCTION overpass_import_func ();
