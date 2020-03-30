-- Test function
CREATE OR REPLACE FUNCTION test_function() RETURNS INTEGER AS $$
DECLARE
BEGIN
    RETURN 433;
END;
$$ LANGUAGE plpgsql;


-- Return the most popular user (tweeted/retweeted)
CREATE OR REPLACE FUNCTION most_popular_user() RETURNS users AS $$
DECLARE
    f_count_tweeted INTEGER;
    f_count_retweeted INTEGER;
BEGIN
    SELECT MAX(followers_count) INTO f_count_tweeted FROM users, tweet_users WHERE users.id = tweet_users.user_id;
    SELECT MAX(followers_count) INTO f_count_retweeted FROM users, retweeted_users WHERE users.id = retweeted_users.user_id;
    RETURN (SELECT * FROM users WHERE users.followers_count = f_count_tweeted LIMIT 1);
END;
$$ LANGUAGE plpgsql;