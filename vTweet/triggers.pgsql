-- CREATE OR REPLACE FUNCTION increment_hashtag_frequency()
--     RETURNS TRIGGER
--     AS $BODY$
-- DECLARE
--     hashtag_temp hashtags.hashtag%type;
--     frequency_temp
-- BEGIN
--     SELECT hashtag INTO hashtag_temp FROM hashtags WHERE hashtag = NEW.hashtag;
--     IF hashtag_temp IS NOT NULL THEN
--     END IF;
-- END;
-- $BODY$

CREATE OR REPLACE FUNCTION log_tweets ()
    RETURNS TRIGGER
    AS $$
BEGIN
    INSERT INTO log
        VALUES (now(), Format('Tweet %s inserted', NEW.tweet_id_str));
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_log_tweets
    AFTER INSERT ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE log_tweets ();

CREATE OR REPLACE FUNCTION is_possibly_sensitive ()
    RETURNS TRIGGER
    AS $$
DECLARE
    c_bad_words CURSOR FOR
        SELECT
            *
        FROM
            bad_words;
    r_bad_words RECORD;
    flag boolean := FALSE;
BEGIN
    FOR r_bad_words IN c_bad_words LOOP
        IF POSITION(r_bad_words.bad_word IN NEW.tweet_text) <> 0 THEN
            NEW.possibly_sensitive := TRUE;
        END IF;
    END LOOP;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_is_possibly_sensitive
    AFTER INSERT ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE is_possibly_sensitive ();

CREATE OR REPLACE FUNCTION delete_hashtags ()
    RETURNS TRIGGER
    AS $$
DECLARE
    c_tweet_hashtag CURSOR (t_id base_tweets.tweet_id % TYPE)
    FOR
        SELECT
            tweet_id,
            hashtag
        FROM
            tweet_hashtag
        WHERE
            tweet_id = t_id;
    freq_temp integer;
    hashtag_temp hashtags.hashtag % TYPE;
BEGIN
    --Hashtags
    FOR r_tweet_hashtag IN c_tweet_hashtag (OLD.tweet_id)
    LOOP
        SELECT
            frequency INTO freq_temp
        FROM
            hashtags
        WHERE
            hashtag = r_tweet_hashtag.hashtag;
        hashtag_temp := r_tweet_hashtag.hashtag;
        DELETE FROM tweet_hashtag
        WHERE CURRENT OF c_tweet_hashtag;
        IF freq_temp > 1 THEN
            UPDATE
                hashtags
            SET
                frequency = frequency - 1
            WHERE
                hashtag = hashtag_temp;
        ELSE
            DELETE FROM hashtags
            WHERE hashtags.hashtag = hashtag_temp;
        END IF;
    END LOOP;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_delete_hashtags
    BEFORE DELETE ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE delete_hashtags ();

CREATE OR REPLACE FUNCTION delete_users ()
    RETURNS TRIGGER
    AS $$
DECLARE
    c_tweet_users CURSOR (t_id base_tweets.tweet_id % TYPE)
    FOR
        SELECT
            tweet_id
        FROM
            tweet_users
        WHERE
            tweet_id = t_id;
    c_retweeted_users CURSOR (t_id base_tweets.tweet_id % TYPE)
    FOR
        SELECT
            tweet_id
        FROM
            retweeted_users
        WHERE
            tweet_id = t_id;
    c_mentioned_users CURSOR (t_id base_tweets.tweet_id % TYPE)
    FOR
        SELECT
            tweet_id
        FROM
            mentioned_users
        WHERE
            tweet_id = t_id;
BEGIN
    --Users
    FOR r_tweet_users IN c_tweet_users (OLD.tweet_id)
    LOOP
        DELETE FROM tweet_users
        WHERE CURRENT OF c_tweet_users;
    END LOOP;
    FOR r_retweeted_users IN c_retweeted_users (OLD.tweet_id)
    LOOP
        DELETE FROM retweeted_users
        WHERE CURRENT OF c_retweeted_users;
    END LOOP;
    FOR r_mentioned_users IN c_mentioned_users (OLD.tweet_id)
    LOOP
        DELETE FROM mentioned_users
        WHERE CURRENT OF c_mentioned_users;
    END LOOP;
    DELETE FROM users
    WHERE id NOT IN ((
            SELECT
                user_id FROM tweet_users)
    UNION (
        SELECT
            user_id FROM retweeted_users)
UNION (
    SELECT
        user_id FROM mentioned_users));
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_delete_users
    BEFORE DELETE ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE delete_users ();

CREATE OR REPLACE FUNCTION delete_places_countries ()
    RETURNS TRIGGER
    AS $$
BEGIN
    DELETE FROM place
    WHERE place_id NOT IN (
            SELECT
                place_id
            FROM
                base_tweets);
    DELETE FROM countries
    WHERE country_code NOT IN (
            SELECT
                country_code
            FROM
                places);
    RETURN NULL;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_delete_places_countries
    AFTER DELETE ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE delete_places_countries ();

CREATE OR REPLACE FUNCTION delete_word_sentiment ()
    RETURNS TRIGGER
    AS $$
BEGIN
    DELETE FROM tweet_word_sentiment
    WHERE tweet_id = OLD.tweet_id;
    DELETE FROM tweet_word
    WHERE tweet_id = OLD.tweet_id;
    RETURN OLD;
END;
$$
LANGUAGE plpgsql;

CREATE TRIGGER tr_delete_word_sentiment
    BEFORE DELETE ON base_tweets
    FOR EACH ROW
    EXECUTE PROCEDURE delete_word_sentiment ();

