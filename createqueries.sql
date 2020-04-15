
CREATE TABLE hashtags (
	hashtag VARCHAR(50) NOT NULL, 
	frequency INTEGER, 
	PRIMARY KEY (hashtag)
)



CREATE TABLE places (
	place_id VARCHAR(20) NOT NULL, 
	name VARCHAR(50), 
	latitude FLOAT, 
	longitude FLOAT, 
	country_code VARCHAR(5), 
	PRIMARY KEY (place_id), 
	FOREIGN KEY(country_code) REFERENCES countries (country_code)
)


CREATE TABLE users (
	id BIGSERIAL NOT NULL, 
	id_str VARCHAR(20), 
	name VARCHAR(60), 
	screen_name VARCHAR(60), 
	followers_count INTEGER, 
	verified BOOLEAN, 
	profile_image_url_https VARCHAR(512), 
	favourites_count INTEGER, 
	PRIMARY KEY (id)
)



CREATE TABLE base_tweets (
	tweet_id BIGSERIAL NOT NULL, 
	tweet_id_str VARCHAR(20), 
	tweet_text TEXT, 
	source VARCHAR(512), 
	favorited BOOLEAN, 
	retweeted BOOLEAN, 
	favorite_count INTEGER, 
	retweet_count INTEGER, 
	result_type VARCHAR(20), 
	created_at TIMESTAMP WITHOUT TIME ZONE, 
	lang VARCHAR(10), 
	possibly_sensitive BOOLEAN, 
	place_id VARCHAR(20), 
	PRIMARY KEY (tweet_id), 
	FOREIGN KEY(place_id) REFERENCES places (place_id)
)



CREATE TABLE tweet_users (
	user_id BIGINT NOT NULL, 
	tweet_id BIGINT NOT NULL, 
	PRIMARY KEY (user_id, tweet_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(tweet_id) REFERENCES base_tweets (tweet_id)
)



CREATE TABLE retweeted_users (
	user_id BIGINT NOT NULL, 
	tweet_id BIGINT NOT NULL, 
	PRIMARY KEY (user_id, tweet_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(tweet_id) REFERENCES base_tweets (tweet_id)
)



CREATE TABLE mentioned_users (
	user_id BIGINT NOT NULL, 
	tweet_id BIGINT NOT NULL, 
	PRIMARY KEY (user_id, tweet_id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	FOREIGN KEY(tweet_id) REFERENCES base_tweets (tweet_id)
)



CREATE TABLE tweet_hashtag (
	tweet_id BIGINT NOT NULL, 
	hashtag VARCHAR(50) NOT NULL, 
	PRIMARY KEY (tweet_id, hashtag), 
	FOREIGN KEY(tweet_id) REFERENCES base_tweets (tweet_id), 
	FOREIGN KEY(hashtag) REFERENCES hashtags (hashtag)
)



CREATE TABLE countries (
	country_code VARCHAR(5) NOT NULL, 
	country VARCHAR(50), 
	PRIMARY KEY (country_code)
)



CREATE TABLE intensity (
	latitude FLOAT NOT NULL, 
	longitude FLOAT NOT NULL, 
	intensity FLOAT, 
	PRIMARY KEY (latitude, longitude)
)

