CREATE OR REPLACE FUNCTION data.update_json_key_with_version(
    p_schema TEXT,
    p_table TEXT,
    p_id_column TEXT,
    p_id_value INTEGER,
    p_json_column TEXT,
    p_json_key TEXT,
    p_json_value JSONB,
    p_mode TEXT
)
RETURNS VOID AS $$
DECLARE
    qualified_table TEXT;
    current_json JSONB;
    current_array JSONB;
    max_version INT;
    updated_array JSONB;
    new_entry JSONB;
    entry JSONB;
BEGIN
    qualified_table := format('%I.%I', p_schema, p_table);

    -- Get the current JSONB object from the column
    EXECUTE format(
        'SELECT %I FROM %s WHERE %I = $1',
        p_json_column, qualified_table, p_id_column
    )
    INTO current_json
    USING p_id_value;

    -- Extract array under the given key
    current_array := current_json -> p_json_key;

    IF p_mode = 'add' THEN
        IF jsonb_typeof(current_array) = 'array' THEN
            SELECT COALESCE(MAX((e->>'version')::INT), 0) + 1
            INTO max_version
            FROM jsonb_array_elements(current_array) AS e;
        ELSE
            max_version := 1;
        END IF;

        new_entry := p_json_value || jsonb_build_object('version', max_version);

        IF jsonb_typeof(current_array) = 'array' THEN
            updated_array := current_array || new_entry;
        ELSE
            updated_array := jsonb_build_array(new_entry);
        END IF;

    ELSIF p_mode = 'replace' THEN
        IF jsonb_typeof(current_array) IS DISTINCT FROM 'array' THEN
            -- Treat like add
            max_version := 1;
            new_entry := p_json_value || jsonb_build_object('version', max_version);
            updated_array := jsonb_build_array(new_entry);
        ELSE
            -- Replace most recent version
            SELECT COALESCE(MAX((e->>'version')::INT), 1)
            INTO max_version
            FROM jsonb_array_elements(current_array) AS e;

            new_entry := p_json_value || jsonb_build_object('version', max_version);
            updated_array := '[]'::jsonb;

            FOR entry IN SELECT * FROM jsonb_array_elements(current_array)
            LOOP
                IF (entry->>'version')::INT = max_version THEN
                    updated_array := updated_array || new_entry;
                ELSE
                    updated_array := updated_array || entry;
                END IF;
            END LOOP;
        END IF;

    ELSE
        RAISE EXCEPTION 'Invalid mode: %, must be "add" or "replace"', p_mode;
    END IF;

    -- Final update using jsonb_set
    EXECUTE format(
        'UPDATE %s SET %I = jsonb_set(COALESCE(%I, ''{}''), ARRAY[$1], $2, true) WHERE %I = $3',
        qualified_table, p_json_column, p_json_column, p_id_column
    )
    USING p_json_key, updated_array, p_id_value;

END;
$$ LANGUAGE plpgsql;
