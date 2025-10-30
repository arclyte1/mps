import os, sys
import time

required_env_vars = ("OSU_API_CLIENT_ID", "OSU_API_CLIENT_SECRET", "POSTGRES_URL")
missing_env_vars = [var for var in required_env_vars if not os.environ[var]]
if missing_env_vars:
    print(f"Please set env vars: {', '.join(missing_env_vars)}")
    sys.exit()


from database import get_missing_beatmap_ids, insert_missing_data, get_missing_player_ids
from osu_api import instance as api
from pprint import pprint

LOAD_LIMIT = 50

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def add_beatmap_data():
    print("getting missing beatmaps")
    beatmap_ids = get_missing_beatmap_ids()
    print(f"got missing beatmaps: {len(beatmap_ids)}")
    chunk_i = 1
    chunks_count = len(beatmap_ids) // LOAD_LIMIT + 1
    for ids in chunks(beatmap_ids, LOAD_LIMIT):
        is_loaded = False
        while not is_loaded:
            try:
                print(f"load beatmaps {chunk_i}/{chunks_count} | {ids[0]} - {ids[-1]}")
                beatmaps_data = api.get_beatmaps(ids)
                while "error" in beatmaps_data:
                    time.sleep(10)
                    beatmaps_data = api.get_beatmaps(ids)
                data = {
                    "beatmaps_data": beatmaps_data["beatmaps"]
                }
                insert_missing_data(data)
                chunk_i+= 1
                is_loaded = True
            except Exception as e:
                print(f"Exception while loading players {e}")
                print("Retry")
                time.sleep(10)


def add_player_data():
    print("getting missing players")
    player_ids = get_missing_player_ids()
    print(f"got missing players: {len(player_ids)}")
    chunk_i = 1
    chunks_count = len(player_ids) // LOAD_LIMIT + 1
    for ids in chunks(player_ids, LOAD_LIMIT):
        is_loaded = False
        while not is_loaded:
            try:
                print(f"load players {chunk_i}/{chunks_count} | {ids[0]} - {ids[-1]}")
                users_data = api.get_users(ids)
                while "error" in users_data:
                    time.sleep(10)
                    users_data = api.get_users(ids)
                data = {
                    "players": users_data["users"]
                }
                insert_missing_data(data)
                chunk_i+= 1
                is_loaded = True
            except Exception as e:
                print(f"Exception while loading players {e}")
                print("Retry")
                time.sleep(10)

if __name__ == "__main__":
    add_beatmap_data()
    add_player_data()
