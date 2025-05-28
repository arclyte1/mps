CREATE TABLE match(
    id integer not null,
    name varchar,
    start_time timestamp,
    end_time timestamp,
    primary key(id)
);

CREATE TYPE eventtype AS ENUM (
    'match-created',
    'match-disbanded',
    'player-joined',
    'player-left',
    'host-changed',
    'player-kicked',
    'unknown'
);

CREATE TABLE event(
    match_id integer not null,
    id integer not null,
    type eventtype not null,
    user_id integer,
    deltatime integer not null,
    primary key(match_id, id),
    foreign key(match_id) references match(id)
);

CREATE TYPE gamemode AS ENUM (
    'osu',
    'fruits',
    'mania',
    'taiko'
);

CREATE TYPE scoringtype AS ENUM (
    'score',
    'combo',
    'accuracy',
    'scorev2'
);

CREATE TYPE teamtype AS ENUM (
    'head-to-head',
    'tag-coop',
    'team-vs',
    'tag-team-vs'
);

CREATE TABLE game(
    match_id integer not null,
    id integer not null,
    start_deltatime integer not null,
    end_deltatime smallint,
    mods integer not null,
    game_mode gamemode not null,
    beatmap_id integer not null,
    scoring_type scoringtype not null,
    team_type teamtype not null,
    primary key(match_id, id),
    foreign key(match_id) references match(id)
);

CREATE TABLE score(
    match_id integer not null,
    game_id integer not null,
    id smallint not null,
    user_id integer not null,
    score integer not null,
    max_combo smallint not null,
    count_100 smallint not null,
    count_300 smallint not null,
    count_50 smallint not null,
    count_geki smallint not null,
    count_katu smallint not null,
    count_miss smallint not null,
    passed boolean not null,
    primary key (match_id, game_id, id),
    foreign key (match_id, game_id) references game(match_id, id)
);

CREATE EXTENSION pg_trgm;

CREATE INDEX score_user_id ON score (user_id);

CREATE INDEX event_user_id ON event (user_id);

CREATE INDEX game_beatmap_id ON game (beatmap_id);

CREATE INDEX match_name ON match USING gin(name gin_trgm_ops);

CREATE TYPE match_parser_queue_status AS ENUM (
    'unchecked',
    'ongoing',
    'error'
);

CREATE TABLE match_parser_queue(
    match_id integer not null,
    last_checked timestamp not null,
    match_status match_parser_queue_status not null,
    last_parsed_event_id bigint not null,
    primary key (match_id)
);

CREATE TABLE player(
    id integer not null,
    username varchar,
    country_code varchar,
    avatar_url varchar,
    primary key(id)
);

CREATE TABLE beatmapset(
    id integer not null,
    artist varchar,
    artist_unicode varchar,
    title varchar,
    title_unicode varchar,
    primary key(id)
);

CREATE TABLE beatmap(
    id integer not null,
    beatmapset_id integer not null,
    status varchar,
    difficulty_rating real,
    version varchar,
    primary key(id),
    foreign key(beatmapset_id) references beatmapset(id)
);