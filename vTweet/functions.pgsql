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

CREATE OR REPLACE FUNCTION most_popular_tweets ()
    RETURNS TABLE (
        tweet_id base_tweets.tweet_id % TYPE,
        screen_name varchar(60)
    )
    AS $$
BEGIN
    RETURN QUERY (
        SELECT
            base_tweets.tweet_id, users.screen_name FROM base_tweets, users, tweet_users
        WHERE
            users.id = tweet_users.user_id
            AND base_tweets.tweet_id = tweet_users.tweet_id ORDER BY base_tweets.favorite_count DESC LIMIT 10);
END;
$$
LANGUAGE plpgsql;

-- Test the function
DROP FUNCTION most_popular_tweets;

SELECT
    *
FROM
    most_popular_tweets ();

-- We have to remove characters, RT, hashtag, mentioned users and extract emojis (PENDING).
CREATE OR REPLACE PROCEDURE remove_special_characters ()
    AS $$
DECLARE
    cur_tweets CURSOR FOR
        SELECT
            tweet_id,
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
        -- RT/FAV
        txt := regexp_replace(row_tweets.tweet_text, '^(RT|FAV)', '', 'gi');
        -- URL
        txt := regexp_replace(txt, '\m((https?://)(\w+)\.(\S+))', ' ', 'gi');
        -- User mentions
        txt := regexp_replace(txt, '@\w*', ' ', 'gi');
        -- Hashtags and other special characters (except apostrophe)
        txt := regexp_replace(txt, '[^\w''\s]', ' ', 'gi');
        -- Remove apostrophe and the next letter
        -- NOTE: REMOVE THE EXTRA SPACE IN REGEX PATTERN. FORMATTER DOES THIS BY DEFAULT
        txt := regexp_replace(txt, '' '\w', ' ', 'gi');
        -- Apparently, colons get left out
        txt := regexp_replace(txt, ':', ' ', 'gi');
        -- Remove extra spaces in the start and end
        txt := regexp_replace(txt, '^\s+', '', 'gi');
        txt := regexp_replace(txt, '\s+$', '', 'gi');
        EXECUTE 'INSERT INTO tweet_word select $1, unnest(tsvector_to_array(to_tsvector(''simple'', $2)))'
        USING row_tweets.tweet_id,
        txt;
    END LOOP;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE calculate_word_score ()
    AS $$
BEGIN
    INSERT INTO tweet_word_sentiment
    SELECT
        tweet_word.tweet_id,
        tweet_word.word,
        word_sentiment.score
    FROM
        tweet_word
    LEFT JOIN word_sentiment ON tweet_word.word = word_sentiment.word
END;
$$
LANGUAGE sql;

WITH most_positive_tweets AS (
    SELECT
        *
    FROM
        base_tweets
    WHERE
        base_tweets.tweet_id IN (
            SELECT
                tweet_word_sentiment.tweet_id
            FROM
                tweet_word_sentiment
            GROUP BY
                tweet_word_sentiment.tweet_id,
                word
            ORDER BY
                sum(score) DESC
            LIMIT 5))
SELECT
    tweet_id,
    tweet_text
FROM
    most_positive_tweets;

WITH most_negative_tweets AS (
    SELECT
        *
    FROM
        base_tweets
    WHERE
        base_tweets.tweet_id IN (
            SELECT
                tweet_word_sentiment.tweet_id
            FROM
                tweet_word_sentiment
            GROUP BY
                tweet_word_sentiment.tweet_id,
                word
            ORDER BY
                sum(score)
            LIMIT 5))
SELECT
    tweet_id,
    tweet_text
FROM
    most_negative_tweets;

WITH most_positive_tweets AS (
    SELECT
        *
    FROM
        base_tweets
    WHERE
        base_tweets.tweet_id = (
            SELECT
                tweet_id
            FROM
                tweet_word_sentiment
            ORDER BY
                sum(score) DESC
            LIMIT 5))
SELECT
    tweet_id,
    tweet_text
FROM
    most_positive_tweets;

-- One word popular words
WITH popular_words AS (
    SELECT
        word,
        nentry
    FROM
        ts_stat('select to_tsvector(''english'', tweet_text) from base_tweets') -- 'english' removes the stop words by default. Not sure about its coverage
    WHERE
        nentry > 1 --> parameter
        -- AND NOT word IN ('to', 'the', 'at', 'in', 'a') --> parameter
    ORDER BY
        nentry DESC
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
        ts_stat('select to_tsvector(''english'', tweet_text) from base_tweets')
    WHERE
        nentry > 1 --> parameter
        -- AND NOT word IN ('to', 'the', 'at', 'in', 'a') --> parameter
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

