import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs"
songplay_table_drop = "DROP TABLE IF EXISTS songplay"
user_table_drop = "DROP TABLE IF EXISTS users"
song_table_drop = "DROP TABLE IF EXISTS songs"
artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES

staging_events_table_create= (""" CREATE TABLE IF NOT EXISTS 
                                staging_events 
                                        (
                                        artist varchar,
                                        auth varchar, 
                                        firstName varchar,
                                        gender varchar,
                                        itemInSession int,
                                        lastName varchar,
                                        length float,
                                        level varchar,
                                        location varchar,
                                        method varchar, 
                                        page varchar, 
                                        registration bigint,
                                        sessionId int,
                                        song varchar,
                                        status int,
                                        ts bigint,
                                        userAgent varchar,
                                        userId int                                      
                                        );
""")

staging_songs_table_create = (""" CREATE TABLE IF NOT EXISTS 
                                staging_songs
                                    (
                                    num_songs int,
                                    artist_id varchar,
                                    artist_lattitude varchar,
                                    artist_longitude varchar,
                                    artist_location varchar,
                                    artist_name varchar,
                                    song_id varchar,
                                    title varchar,
                                    duration float,
                                    year int
                                    );
""")

songplay_table_create = (""" CREATE TABLE IF NOT EXISTS
                                songplay
                                (
                                songplay_id int IDENTITY(0,1),
                                start_time datetime,
                                user_id int,
                                level varchar,
                                song_id varchar distkey,
                                artist_id varchar,
                                session_id int sortkey,
                                location varchar,
                                user_agent varchar
                                );
                        """)

user_table_create = (""" CREATE TABLE IF NOT EXISTS 
                            users 
                            (
                            user_id int sortkey,
                            first_name varchar,
                            last_name varchar,
                            gender varchar,
                            level varchar                        
                            )
                            diststyle ALL;
                        """)

song_table_create = (""" CREATE TABLE IF NOT EXISTS 
                            songs 
                            (
                            song_id varchar NOT NULL sortkey distkey,
                            title varchar NOT NULL,
                            artist_id varchar NOT NULL,
                            year int,
                            duration float NOT NULL                            
                            );
                    """)

artist_table_create = (""" CREATE TABLE IF NOT EXISTS 
                            artists
                            (
                            artist_id varchar NOT NULL sortkey,
                            artist_name varchar,
                            location varchar,
                            lattitude varchar,
                            longitude varchar
                            )
                            diststyle ALL;
                        """)

time_table_create = (""" CREATE TABLE IF NOT EXISTS
                            time
                            (
                            start_time datetime NOT NULL distkey sortkey,
                            hour int NOT NULL,
                            day int NOT NULL,
                            week int NOT NULL, 
                            month int NOT NULL,
                            year int NOT NULL, 
                            weekday int NOT NULL
                            );
                    """)

# STAGING TABLES
#credentials 'aws_iam_role={}'
staging_events_copy = ("""COPY staging_events
                          FROM {}
                          iam_role '{}'                          
                          JSON {}
                          region 'us-west-2';
                       """).format(config.get("S3","LOG_DATA"),\
                                   config.get("IAM_ROLE", "ARN"),\
                                   config.get("S3", "LOG_JSONPATH")\
                                  )

staging_songs_copy = (""" COPY staging_songs
                          FROM {}
                          iam_role '{}'
                          JSON 'auto'
                          region 'us-west-2';
                    """).format(config.get('S3','SONG_DATA'),\
                                config.get('IAM_ROLE','ARN')\
                               )

# FINAL TABLES

songplay_table_insert = (""" INSERT INTO songplay 
                                (
                                 start_time,
                                 user_id,
                                 level,
                                 song_id,
                                 artist_id,
                                 session_id,
                                 location,
                                 user_agent
                                ) 
                             SELECT DISTINCT (TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 Second') as start_time, 
                                     se.userId as user_id, 
                                     se.level,
                                     ss.song_id,
                                     ss.artist_id,
                                     se.sessionId as session_id,
                                     se.location,
                                     se.userAgent as user_agent
                             FROM staging_events se
                             JOIN staging_songs ss 
                             ON (se.song=ss.title) AND (se.artist=ss.artist_name) AND (se.length=ss.duration) 
                             WHERE (se.page='NextSong');
                                
""")

user_table_insert = (""" INSERT INTO users
                            (
                            user_id, 
                            first_name,
                            last_name, 
                            gender,
                            level
                            ) 
                          SELECT DISTINCT userID as user_id,
                                 firstName as first_name,
                                 lastName as last_name,
                                 gender,
                                 level
                          FROM staging_events
                          WHERE user_id NOT IN (SELECT DISTINCT user_id FROM users)
""")

song_table_insert = (""" INSERT INTO songs
                            (
                            song_id,
                            title,
                            artist_id,
                            year,
                            duration
                            )
                            SELECT DISTINCT song_id,
                                   title,
                                   artist_id,
                                   year,
                                   duration
                            FROM staging_songs
""")

artist_table_insert = (""" INSERT INTO artists
                            (
                            artist_id,
                            artist_name, 
                            location,
                            lattitude,
                            longitude
                            )
                            SELECT DISTINCT artist_id, 
                                   artist_name as artist_name,
                                   artist_location as location,
                                   artist_lattitude as lattitude,
                                   artist_longitude as longitude
                            FROM staging_songs
""")

time_table_insert = (""" INSERT INTO time 
                            (
                            start_time,
                            hour,
                            day,
                            week,
                            month,
                            year,
                            weekday
                            )
                            SELECT DISTINCT new_ts as start_time, 
                                    EXTRACT (HOUR FROM new_ts) as hour,
                                    EXTRACT (DAY FROM new_ts) as day,
                                    EXTRACT (WEEK FROM new_ts) as week,
                                    EXTRACT (MONTH FROM new_ts) as month,
                                    EXTRACT (YEAR FROM new_ts) as year,
                                    DATEPART (WEEKDAY, new_ts) as weekday
                            FROM ( 
                                SELECT (TIMESTAMP 'epoch' + ts/1000 * INTERVAL '1 Second') as new_ts
                                FROM staging_events
                                )
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]
