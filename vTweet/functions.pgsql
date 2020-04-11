-- Test function
CREATE OR REPLACE FUNCTION test_function ()
    RETURNS integer
    AS $$
DECLARE
BEGIN
    RETURN 433;
END;
$$
LANGUAGE plpgsql;

-- Return the most popular user (tweeted/retweeted)
CREATE OR REPLACE FUNCTION most_popular_users ()
    RETURNS TABLE (
        LIKE users
    )
    AS $$
DECLARE
    f_count_tweeted integer;
    f_count_retweeted integer;
    max_f_count integer;
BEGIN
    RETURN QUERY (
        SELECT
            users.* FROM users, tweet_users
        UNION
        SELECT
            users.* FROM users, retweeted_users)
ORDER BY
    followers_count DESC
LIMIT 5;
    -- SELECT
    --     MAX(followers_count) INTO f_count_tweeted
    -- FROM
    --     users,
    --     tweet_users
    -- WHERE
    --     users.id = tweet_users.user_id;
    -- SELECT
    --     MAX(followers_count) INTO f_count_retweeted
    -- FROM
    --     users,
    --     retweeted_users
    -- WHERE
    --     users.id = retweeted_users.user_id;
    -- max_f_count := GREATEST (f_count_tweeted, f_count_retweeted);
    -- RETURN QUERY
    -- SELECT
    --     *
    -- FROM
    --     users
    -- WHERE
    --     users.followers_count = max_f_count
    -- LIMIT 1;
END;
$$
LANGUAGE plpgsql;

-- Call the function
SELECT
    *
FROM
    most_popular_users ();

-- Increment Hashtag Frequency (Use this instead of directly inserting to Hashtag table)
CREATE OR REPLACE PROCEDURE increment_hashtag_frequency (hashtag_name varchar
)
    AS $$
DECLARE
    hashtag_freq integer;
BEGIN
    SELECT
        frequency INTO hashtag_freq
    FROM
        hashtags
    WHERE
        hashtag = hashtag_name;
    IF hashtag_freq IS NULL THEN
        INSERT INTO hashtags
            VALUES (hashtag_name, 1);
    ELSE
        UPDATE
            hashtags
        SET
            frequency = hashtag_freq + 1
        WHERE
            hashtag = hashtag_name;
    END IF;
END;
$$
LANGUAGE plpgsql;

-- Call the procedure
CALL increment_hashtag_frequency ('somehashtag');

-- Most popular hashtags
CREATE OR REPLACE FUNCTION most_popular_hashtags ()
    RETURNS TABLE (
        LIKE hashtags
    )
    AS $$
DECLARE
BEGIN
    --- If the query itself is a hashtag, remove it from the most popular hashtags
    -- IF query LIKE '#%' THEN
    --     query := SUBSTRING(query, 2, length(query) - 1);
    --     RETURN QUERY
    --     SELECT
    --         *
    --     FROM
    --         hashtags
    --     EXCEPT (
    --         SELECT
    --             *
    --         FROM
    --             hashtags
    --         WHERE
    --             hashtag = query)
    -- ORDER BY
    --     frequency DESC
    -- LIMIT 10;
    --     --- Otherwise, just return the most popular hashtags
    -- ELSE
    RETURN QUERY
    SELECT
        *
    FROM
        hashtags
    ORDER BY
        frequency DESC
    LIMIT 10;
    -- END IF;
END;
$$
LANGUAGE plpgsql;

-- Call the function
SELECT
    *
FROM
    most_popular_hashtags ('originalhashtag');

CREATE OR REPLACE FUNCTION heatmap_input ()
    RETURNS TABLE (
        LIKE intensity
    )
    AS $$
DECLARE
    cur_coordinates CURSOR FOR
        SELECT
            latitude,
            longitude,
            COUNT(tweet_id)
        FROM
            base_tweets,
            places
        WHERE
            places.place_id = base_tweets.place_id
        GROUP BY
            places.place_id;
    rec_coordinates RECORD;
BEGIN
    DELETE FROM intensity;
    OPEN cur_coordinates;
    LOOP
        FETCH cur_coordinates INTO rec_coordinates;
        EXIT
        WHEN NOT FOUND;
        INSERT INTO intensity
            VALUES (rec_coordinates.latitude, rec_coordinates.longitude, 1);
    END LOOP;
    RETURN QUERY (
        SELECT
            * FROM intensity);
END;
$$
LANGUAGE plpgsql;

SELECT
    coordinates.latitude,
    coordinates.longitude,
    COUNT(tweet_id)
FROM
    base_tweets,
    places,
    coordinates
WHERE
    places.country_code = coordinates.country_code
    AND places.place_id = base_tweets.place_id
GROUP BY
    coordinates.country_code;

CREATE OR REPLACE FUNCTION most_popular_users ()
    RETURNS TABLE (
        name varchar(60),
        screen_name varchar(60),
        followers_count integer,
        profile_image_url_https varchar(512)
    )
    AS $$
DECLARE
BEGIN
    RETURN QUERY (
        SELECT
            users.name, users.screen_name, users.followers_count, users.profile_image_url_https FROM users ORDER BY followers_count DESC LIMIT 10);
END;
$$
LANGUAGE plpgsql;

-- We have to remove characters, RT, hashtag, mentioned users and extract emojis. PENDING
CREATE OR REPLACE PROCEDURE remove_special_characters ()
    AS $$
DECLARE
    cur_tweets CURSOR FOR
        SELECT
            tweet_text
        FROM
            base_tweets;
    row_tweets RECORD;
    txt text;
BEGIN
    OPEN cur_tweets;
    LOOP
        FETCH cur_tweets INTO row_tweets;
        EXIT
        WHEN NOT FOUND;
        txt := regexp_replace(row_tweets.tweet_text, '[^\w]+', ' ', 'g');
        -- RAISE NOTICE '%', regexp_replace(row_tweets.tweet_text, '[^\w]+', ' ', 'g');
    END LOOP;
END;
$$
LANGUAGE plpgsql;

CALL remove_special_characters ();

-- One word popular words
WITH popular_words AS (
    SELECT
        word
    FROM
        ts_stat('select tweet_text::tsvector from test')
    WHERE
        nentry > 1 --> parameter
        AND NOT word IN ('to', 'the', 'at', 'in', 'a') --> parameter
)
SELECT
    *
FROM
    popular_words;

-- Two word popular words
WITH popular_words AS (
    SELECT
        word
    FROM
        ts_stat('select tweet_text::tsvector from test')
    WHERE
        nentry > 1 --> parameter
        AND NOT word IN ('to', 'the', 'at', 'in', 'a') --> parameter
)
SELECT
    concat_ws(' ', a1.word, a2.word) phrase,
    count(*)
FROM
    popular_words AS a1
    CROSS JOIN popular_words AS a2
    CROSS JOIN test
WHERE
    tweet_text ILIKE format('%%%s %s%%', a1.word, a2.word)
GROUP BY
    1
HAVING
    count(*) > 1 --> parameter
ORDER BY
    2 DESC;

