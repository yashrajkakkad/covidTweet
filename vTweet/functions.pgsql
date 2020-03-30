-- Test function
CREATE OR REPLACE FUNCTION test_function ()
    RETURNS INTEGER
    AS $$
DECLARE
BEGIN
    RETURN 433;
END;
$$
LANGUAGE plpgsql;

-- Return the most popular user (tweeted/retweeted)
CREATE OR REPLACE FUNCTION most_popular_user ()
    RETURNS RECORD
    AS $$
DECLARE
    f_count_tweeted integer;
    f_count_retweeted integer;
    pop_user RECORD;
BEGIN
    SELECT
        MAX(followers_count) INTO f_count_tweeted
    FROM
        users,
        tweet_users
    WHERE
        users.id = tweet_users.user_id;
    SELECT
        MAX(followers_count) INTO f_count_retweeted
    FROM
        users,
        retweeted_users
    WHERE
        users.id = retweeted_users.user_id;
    SELECT
        * INTO pop_user
    FROM
        users
    WHERE
        users.followers_count = f_count_tweeted
    LIMIT 1;
    RETURN pop_user;
END;
$$
LANGUAGE plpgsql;

-- Call the function
SELECT
    most_popular_user ();

