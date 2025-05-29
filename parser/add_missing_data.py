from database import get_unique_beatmap_ids, insert_missing_data, get_unique_player_ids
from osu_api import instance as api
from pprint import pprint

def add_beatmap_data():
    i = 0
    beatmap_ids = get_unique_beatmap_ids()
    ids_list = list()
    while i != len(beatmap_ids):
        while len(ids_list) != 50:
            if(i == len(beatmap_ids)):
                break
            ids_list.append(beatmap_ids[i][0])
            i += 1
        beatmaps_data = api.get_beatmaps(ids_list)
        data = {
            "beatmaps_data": [b for b in beatmaps_data if 'error' not in b]
        }
        insert_missing_data(data)
        ids_list.clear()
    
    
        

def add_player_data():
    i = 0
    player_ids = get_unique_player_ids()
    ids_list = list()
    while i != len(player_ids):
        while len(ids_list) != 50:
            if(i == len(player_ids)):
                break
            ids_list.append(player_ids[i][0])
            i += 1
        users_data = api.get_users(ids_list)
        data = {
            "players": [p for p in users_data if 'error' not in p]
        }
        insert_missing_data(data)
        ids_list.clear()
            

if __name__ == "__main__":
    add_beatmap_data()
    add_player_data()
            
            
