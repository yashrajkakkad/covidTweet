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
    most_popular_user ();

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
CREATE OR REPLACE FUNCTION most_popular_hashtags (query varchar)
    RETURNS TABLE (
        LIKE hashtags
    )
    AS $$
DECLARE
BEGIN
    --- If the query itself is a hashtag, remove it from the most popular hashtags
    IF query LIKE '#%' THEN
        query := SUBSTRING(query, 2, length(query) - 1);
        RETURN QUERY
        SELECT
            *
        FROM
            hashtags
        EXCEPT (
            SELECT
                *
            FROM
                hashtags
            WHERE
                hashtag = query)
    ORDER BY
        frequency DESC
    LIMIT 5;
        --- Otherwise, just return the most popular hashtags
    ELSE
        RETURN QUERY
        SELECT
            *
        FROM
            hashtags
        ORDER BY
            frequency DESC
        LIMIT 5;
    END IF;
END;
$$
LANGUAGE plpgsql;

-- Call the function
SELECT
    *
FROM
    most_popular_hashtags ('originalhashtag');

