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

