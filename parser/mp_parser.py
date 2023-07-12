from OsuApi import OsuApi
from time import sleep
import psycopg2
from datetime import datetime
import os

START_MP = 109144236
LIMIT = 5000
MODS = {
    "NM" : 0,
    "NF" : 1,
    "EZ" : 2, 
    "TD" : 4, 
    "HD" : 8, 
    "HR" : 16, 
    "SD" : 32, 
    "DT" : 64, 
    "RX" : 128, 
    "HT" : 256, 
    "NC" : 512,
    "FL" : 1024, 
    "Autoplay" : 2048,
    "SO" : 4096, 
    "AP" : 8192,
    "PF" : 16384,
    "4K" : 32768, 
    "5K" : 65536,
    "6K" : 131072, 
    "7K" : 262144, 
    "8K" : 524288, 
    "FI" : 1048576, 
    "RD" : 2097152, 
    "LastMod" : 4194304,
    "9K" : 16777216, 
    "10K" : 33554432, 
    "1K" : 67108864, 
    "3K" : 134217728, 
    "2K" : 268435456, 
    "ScoreV2" : 536870912, 
    "MR" : 1073741824
}


def build_match_query(match):
    name = match['name'].replace('\'', '\'\'')
    return f"INSERT INTO match VALUES ({match['id']}, \'{name}\', \'{match['start_time']}\', \'{match['end_time']}\');"


def build_event_query(match_id: int, event_id: int, last_event_time: datetime, event):
    deltatime = int((datetime.fromisoformat(event['timestamp']) - last_event_time).total_seconds())
    user_id = event['user_id'] if event['user_id'] else 'null'
    return f"INSERT INTO event VALUES ({match_id}, {event_id}, \'{event['detail']['type']}\', {user_id}, {deltatime});"


def build_game_query(match_id: int, game_id: int, last_event_time: datetime, event):
    start_delta = int((datetime.fromisoformat(event['timestamp']) - last_event_time).total_seconds())
    end_delta = 'null'
    if event['game']['end_time']:
        end_delta = int((datetime.fromisoformat(event['game']['end_time']) - last_event_time).total_seconds()) - start_delta
    mods = sum(map(MODS.get, event['game']['mods']))
    return f"INSERT INTO game VALUES ({match_id}, {game_id}, {start_delta}, {end_delta}, {mods}, \'{event['game']['mode']}\', {event['game']['beatmap_id']}, \'{event['game']['scoring_type']}\', \'{event['game']['team_type']}\');"


def build_score_query(match_id, game_id, score_id, score):
    return f"INSERT INTO score VALUES ({match_id}, {game_id}, {score_id}, {score['user_id']}, {score['score']}, {score['max_combo']}, {score['statistics']['count_100']}, {score['statistics']['count_300']}, {score['statistics']['count_50']}, {score['statistics']['count_geki']}, {score['statistics']['count_katu']}, {score['statistics']['count_miss']}, {score['passed']});"


def build_mp_queries(mp):
    queries = []
    queries.append(build_match_query(mp['match']))
    
    match_id = mp['match']['id']
    event_id = 0
    game_id = 0
    match_start = datetime.fromisoformat(mp['match']['start_time'])
    last_event_time = match_start
    last_game_time = match_start
    
    for event in mp['events']:
        if event['detail']['type'] != 'other':
            queries.append(build_event_query(match_id, event_id, last_event_time, event))
            event_id += 1
            last_event_time = datetime.fromisoformat(event['timestamp'])
        else:
            score_id = 0
            queries.append(build_game_query(match_id, game_id, last_game_time, event))
            for score in event['game']['scores']:
                queries.append(build_score_query(match_id, game_id, score_id, score))
                score_id += 1
            game_id += 1
            last_game_time = datetime.fromisoformat(event['timestamp'])
    
    return queries


def write_mp(mp, cursor):
    try:
        for query in build_mp_queries(mp):
            cursor.execute(query)
    except Exception as e:
        print(mp['match']['id'])
        print(e)


def download_mps(start: int, limit: int, api: OsuApi, connection):
    with connection.cursor() as cursor:
        for mp_id in range(start, start+limit, 20):
            mps = api.get_mps(list(range(mp_id, mp_id+20)))
            for mp in mps:
                write_mp(mp, cursor)
                connection.commit()
            sleep(1)


if __name__ == "__main__":
    try:
        connection = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/postgres")
        client_id = os.environ['OSU_API_CLIENT_ID']
        client_secret = os.environ['OSU_API_CLIENT_SECRET']
        api = OsuApi(client_id, client_secret)
        download_mps(START_MP, LIMIT, api, connection)
    except Exception as e:
        print(e)
    finally:
        if connection:
            connection.close()
