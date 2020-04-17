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
-- CREATE OR REPLACE FUNCTION most_popular_users ()
--     RETURNS TABLE (
--         LIKE users
--     )
--     AS $$
-- DECLARE
--     f_count_tweeted integer;
--     f_count_retweeted integer;
--     max_f_count integer;
-- BEGIN
--     RETURN QUERY (
--         SELECT
--             users.* FROM users, tweet_users
--         UNION
--         SELECT
--             users.* FROM users, retweeted_users)
-- ORDER BY
--     followers_count DESC
-- LIMIT 5;
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
-- END;
-- $$
-- LANGUAGE plpgsql;
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
            COUNT(tweet_id) AS cnt
        FROM
            base_tweets,
            places
        WHERE
            places.place_id = base_tweets.place_id
        GROUP BY
            places.place_id;
    rec_coordinates RECORD;
    intensity_temp numeric(2, 1);
    BEGIN
        DELETE FROM intensity;
        OPEN cur_coordinates;
        LOOP
            FETCH cur_coordinates INTO rec_coordinates;
            EXIT
            WHEN NOT FOUND;
            IF rec_coordinates.cnt >= 3 THEN
                intensity_temp := 1;
            ELSIF rec_coordinates.cnt = 2 THEN
                intensity_temp := 0.8;
            ELSE
                intensity_temp := 0.6;
            END IF;
            INSERT INTO intensity
                VALUES (rec_coordinates.latitude, rec_coordinates.longitude, intensity_temp);
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
        followers_count varchar,
        profile_image_url_https varchar(512)
    )
    AS $$
DECLARE
BEGIN
    RETURN QUERY (
        SELECT
            users.name, users.screen_name, convert_to_human_readable (users.followers_count), users.profile_image_url_https FROM users ORDER BY users.followers_count DESC LIMIT 10);
END;
$$
LANGUAGE plpgsql;

-- Convert follower count to human readable
CREATE OR REPLACE FUNCTION convert_to_human_readable (n integer)
    RETURNS varchar
    AS $$
import math
from decimal import Decimal
millnames = ['', 'k', 'M', 'B', 'T', 'P', 'E', 'Z', 'Y']
x = float(n)
millidx = max(0, min(len(millnames) - 1, int(math.floor(0 if x == 0 else math.log10(abs(x)) / 3))))
result = '{:.{precision}f}'.format(x / 10**(3 * millidx), precision=1)
return '{0}{dx}'.format(result, dx=millnames[millidx])
$$
LANGUAGE plpython3u;

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
    LEFT JOIN word_sentiment ON tweet_word.word = word_sentiment.word;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION most_positive_tweets ()
    RETURNS TABLE (
        b_tweets base_tweets.tweet_id % TYPE,
        s_name users.screen_name % TYPE
    )
    AS $$
BEGIN
    RETURN QUERY (
        SELECT
            base_tweets.tweet_id, users.screen_name FROM base_tweets, tweet_users, users
        WHERE
            base_tweets.tweet_id = tweet_users.tweet_id
            AND tweet_users.user_id = users.id
            AND (base_tweets.tweet_id IN (
                    SELECT
                        tweet_word_sentiment.tweet_id FROM tweet_word_sentiment GROUP BY tweet_word_sentiment.tweet_id ORDER BY (sum(tweet_word_sentiment.score)) DESC LIMIT 5)));
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION most_negative_tweets ()
    RETURNS TABLE (
        b_tweets base_tweets.tweet_id % TYPE,
        s_name users.screen_name % TYPE
    )
    AS $$
BEGIN
    RETURN QUERY (
        SELECT
            base_tweets.tweet_id, users.screen_name FROM base_tweets, tweet_users, users
        WHERE
            base_tweets.tweet_id = tweet_users.tweet_id
            AND tweet_users.user_id = users.id
            AND (base_tweets.tweet_id IN (
                    SELECT
                        tweet_word_sentiment.tweet_id FROM tweet_word_sentiment GROUP BY tweet_word_sentiment.tweet_id ORDER BY (sum(tweet_word_sentiment.score))
            LIMIT 5)));
END;
$$
LANGUAGE plpgsql;

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

CREATE OR REPLACE FUNCTION tweets_by_time ()
    RETURNS integer ARRAY
    AS $$
DECLARE
    tweet_frequency integer ARRAY := array_fill(0, ARRAY[24]);
    freq_temp integer;
BEGIN
    -- FOR i IN 0..23 LOOP
    --     RAISE NOTICE '%', tweet_frequency[i+1];
    -- END LOOP;
    FOR i IN 0..23 LOOP
        SELECT
            Count(*) INTO freq_temp
        FROM
            base_tweets
        WHERE
            EXTRACT(hour FROM created_at) = i;
        tweet_frequency[i + 1] := freq_temp;
    END LOOP;
    RETURN tweet_frequency;
END;
$$
LANGUAGE plpgsql;

SELECT
    *
FROM
    tweets_by_time ();

CREATE OR REPLACE FUNCTION tweets_by_time_with_sentiment ()
    RETURNS TABLE (
        p_freq integer ARRAY,
        neg_feq integer ARRAY,
        neu_freq integer ARRAY
    )
    AS $$
DECLARE
    positive_frequency integer ARRAY := array_fill(0, ARRAY[24]);
    neutral_frequency integer ARRAY := array_fill(0, ARRAY[24]);
    negative_frequency integer ARRAY := array_fill(0, ARRAY[24]);
    freq_temp integer;
    -- t_id_temp base_tweets.tweet_id % TYPE;
    -- scr_temp integer;
BEGIN
    FOR i IN 0..23 LOOP
        SELECT
            COUNT(*) INTO freq_temp
        FROM (
            SELECT
                tweet_word_sentiment.tweet_id,
                sum(tweet_word_sentiment.score)
            FROM
                base_tweets,
                tweet_word_sentiment
            WHERE
                base_tweets.tweet_id = tweet_word_sentiment.tweet_id
                AND EXTRACT(hour FROM created_at) = i
            GROUP BY
                tweet_word_sentiment.tweet_id
            HAVING
                sum(tweet_word_sentiment.score) > 0) AS tempAlias;
        positive_frequency[i + 1] := freq_temp;
        SELECT
            COUNT(*) INTO freq_temp
        FROM (
            SELECT
                tweet_word_sentiment.tweet_id,
                sum(tweet_word_sentiment.score)
            FROM
                base_tweets,
                tweet_word_sentiment
            WHERE
                base_tweets.tweet_id = tweet_word_sentiment.tweet_id
                AND EXTRACT(hour FROM created_at) = i
            GROUP BY
                tweet_word_sentiment.tweet_id
            HAVING
                sum(tweet_word_sentiment.score) < 0) AS tempAlias;
        negative_frequency[i + 1] := freq_temp;
        SELECT
            COUNT(*) INTO freq_temp
        FROM (
            SELECT
                tweet_word_sentiment.tweet_id,
                sum(tweet_word_sentiment.score)
            FROM
                base_tweets,
                tweet_word_sentiment
            WHERE
                base_tweets.tweet_id = tweet_word_sentiment.tweet_id
                AND EXTRACT(hour FROM created_at) = i
            GROUP BY
                tweet_word_sentiment.tweet_id
            HAVING
                sum(tweet_word_sentiment.score) = 0) AS tempAlias;
        neutral_frequency[i + 1] := freq_temp;
        -- SELECT
        --     Count(*) INTO freq_temp
        -- FROM
        --     base_tweets,
        --     tweet_word_sentiment
        -- WHERE
        --     base_tweets.tweet_id = tweet_word_sentiment.tweet_id
        --     AND EXTRACT(hour FROM created_at) = i
        -- GROUP BY
        --     (sum(tweet_word_sentiment.score))
        -- HAVING
        --     sum(tweet_word_sentiment.score) < 0;
        -- negative_frequency[i + 1] := freq_temp;
        -- SELECT
        --     Count(*) INTO freq_temp
        -- FROM
        --     base_tweets,
        --     tweet_word_sentiment
        -- WHERE
        --     base_tweets.tweet_id = tweet_word_sentiment.tweet_id
        --     AND EXTRACT(hour FROM created_at) = i
        -- GROUP BY
        --     sum(tweet_word_sentiment.score)
        -- HAVING
        --     sum(tweet_word_sentiment.score) = 0;
        -- neutral_frequency[i + 1] := freq_temp;
    END LOOP;
    RETURN QUERY (
        SELECT
            positive_frequency, negative_frequency, neutral_frequency);
END;
$$
LANGUAGE plpgsql;

SELECT
    *
FROM
    tweets_by_time_with_sentiment ();

CREATE OR REPLACE FUNCTION generate_word_cloud (words text[], pos_words text[], neg_words text[])
    RETURNS varchar
    AS $$

import preprocessor as p
import re
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

word_str = ' '.join(words)
word_str = p.clean(word_str)
word_str = re.sub(r'[^\x00-\x7F]+', ' ', word_str)
word_str = word_str.replace('corona', '')
word_str = word_str.replace('covid', '')
word_cloud = WordCloud(stopwords=STOPWORDS,
					   background_color='white',
                       width=640,
                       height=480).generate(word_str)
word_cloud.to_file('cloud.png')

pos_word_str = ' '.join(pos_words)
pos_word_str = p.clean(pos_word_str)
pos_word_str = re.sub(r'[^\x00-\x7F]+', ' ', pos_word_str)
pos_word_str = pos_word_str.replace('corona', '')
pos_word_str = pos_word_str.replace('covid', '')
word_cloud = WordCloud(stopwords=STOPWORDS,
					   background_color='white',
                       width=640,
                       height=480).generate(pos_word_str)
word_cloud.to_file('pos_cloud.png')

neg_word_str = ' '.join(words)
neg_word_str = p.clean(neg_word_str)
neg_word_str = re.sub(r'[^\x00-\x7F]+', ' ', neg_word_str)
neg_word_str = neg_word_str.replace('corona', '')
neg_word_str = neg_word_str.replace('covid', '')
word_cloud = WordCloud(stopwords=STOPWORDS,
					   background_color='white',
                       width=640,
                       height=480).generate(neg_word_str)
word_cloud.to_file('neg_cloud.png')
$$
LANGUAGE plpython3u;

CREATE OR REPLACE FUNCTION most_active_time_per_location ()
    RETURNS TABLE (
        hr double precision,
        p_id character varying,
        p_name character varying,
        p_latitude double precision,
        p_longitude double precision)
    LANGUAGE 'plpgsql'
    AS $$
BEGIN
    RETURN QUERY ( SELECT DISTINCT ON (place_id)
        most_active_hour, placeid, places.name, places.latitude, places.longitude FROM (
            SELECT
                EXTRACT(hour FROM created_at) AS most_active_hour, places.place_id AS placeid, RANK() OVER (PARTITION BY places.place_id ORDER BY COUNT(EXTRACT(hour FROM created_at)) DESC) AS hour_rank FROM base_tweets, places
WHERE
    base_tweets.place_id = places.place_id GROUP BY EXTRACT(hour FROM created_at), places.place_id ORDER BY places.name) AS tbl
JOIN places ON places.place_id = placeid
WHERE
    hour_rank = 1);
END;
$$;

SELECT
    *
FROM
    most_active_time_per_location ();

SELECT
    MAX(cnt)
FROM (
    SELECT
        EXTRACT(hour FROM created_at),
        COUNT(EXTRACT(hour FROM created_at)) AS cnt,
        places.place_id
    FROM
        base_tweets,
        places
    WHERE
        base_tweets.place_id = places.place_id
    GROUP BY
        EXTRACT(hour FROM created_at),
        places.place_id) AS derivedTable;

