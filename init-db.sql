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
    id smallint not null,
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
    id smallint not null,
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
    game_id smallint not null,
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

CREATE TABLE match_parser_queue(
    match_id integer not null,
    last_checked timestamp not null,
    primary key (match_id),
    foreign key (match_id) references match(id)
);