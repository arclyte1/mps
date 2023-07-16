from pprint import pprint
from os import environ
import psycopg2
from datetime import datetime


class __QueryBuilder:

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


    class Query:
        sql_template: str
        data: dict

        def __str__(self):
            return str({'sql_template': self.sql_template, 'data': self.data})


    def build_match_query(self, match, is_upsert):
        query = self.Query()
        query.data = {
            'id': match['id'],
            'name': match['name'],
            'start_time': match['start_time'],
            'end_time': match['end_time']
        }
        query.sql_template = 'INSERT INTO match VALUES (%(id)s, %(name)s, %(start_time)s, %(end_time)s)'
        if is_upsert:
            query.sql_template += 'ON CONFLICT (id) DO UPDATE SET (name, start_time, end_time) = (%(name)s, %(start_time)s, %(end_time)s)'
        return query


    def build_event_query(self, match_id: int, event_id: int, last_event_time: datetime, event, is_upsert):
        deltatime = int((datetime.fromisoformat(event['timestamp']) - last_event_time).total_seconds())
        query = self.Query()
        query.data = {
            'match_id': match_id,
            'event_id': event_id,
            'type': event['detail']['type'],
            'user_id': event['user_id'],
            'deltatime': deltatime
        }
        query.sql_template = 'INSERT INTO event VALUES (%(match_id)s, %(event_id)s, %(type)s, %(user_id)s, %(deltatime)s)'
        if is_upsert:
            query.sql_template += 'ON CONFLICT (match_id, id) DO UPDATE SET (type, user_id, deltatime) = (%(type)s, %(user_id)s, %(deltatime)s)'
        return query


    def build_game_query(self, match_id: int, game_id: int, last_event_time: datetime, event, is_upsert):
        start_delta = int((datetime.fromisoformat(event['timestamp']) - last_event_time).total_seconds())
        end_delta = None  # 'null'
        if event['game']['end_time']:
            end_delta = int((datetime.fromisoformat(event['game']['end_time']) - last_event_time).total_seconds()) - start_delta
        mods = sum(map(self.MODS.get, event['game']['mods']))
        query = self.Query()
        query.data = {
            'match_id': match_id,
            'game_id': game_id,
            'start_delta': start_delta,
            'end_delta': end_delta,
            'mods': mods,
            'mode': event['game']['mode'],
            'beatmap_id': event['game']['beatmap_id'],
            'scoring_type': event['game']['scoring_type'],
            'team_type': event['game']['team_type']
        }
        query.sql_template = 'INSERT INTO game VALUES (%(match_id)s, %(game_id)s, %(start_delta)s, %(end_delta)s, %(mods)s, %(mode)s, %(beatmap_id)s,'\
            ' %(scoring_type)s, %(team_type)s)'
        if is_upsert:
            query.sql_template += 'ON CONFLICT (match_id, id) DO UPDATE SET (start_deltatime, end_deltatime, mods, game_mode, beatmap_id, scoring_type, team_type)'\
                ' = (%(start_delta)s, %(end_delta)s, %(mods)s, %(mode)s, %(beatmap_id)s, %(scoring_type)s, %(team_type)s)'
        return query


    def build_score_query(self, match_id, game_id, score_id, score, is_upsert):
        query = self.Query()
        query.data = {
            'match_id': match_id,
            'game_id': game_id,
            'score_id': score_id,
            'user_id': score['user_id'],
            'score': score['score'],
            'max_combo': score['max_combo'],
            'count_100': score['statistics']['count_100'],
            'count_300': score['statistics']['count_300'],
            'count_50': score['statistics']['count_50'],
            'count_geki': score['statistics']['count_geki'],
            'count_katu': score['statistics']['count_katu'],
            'count_miss': score['statistics']['count_miss'],
            'passed': score['passed']
        }
        query.sql_template = 'INSERT INTO score VALUES (%(match_id)s, %(game_id)s, %(score_id)s, %(user_id)s, %(score)s, %(max_combo)s, %(count_100)s,'\
            ' %(count_300)s, %(count_50)s, %(count_geki)s, %(count_katu)s, %(count_miss)s, %(passed)s)'
        if is_upsert:
            query.sql_template += 'ON CONFLICT (match_id, game_id, id) DO UPDATE SET (user_id, score, max_combo, count_100, count_300, count_50, count_geki,'\
                ' count_katu, count_miss, passed) = (%(user_id)s, %(score)s, %(max_combo)s, %(count_100)s,'\
                ' %(count_300)s, %(count_50)s, %(count_geki)s, %(count_katu)s, %(count_miss)s, %(passed)s)'
        return query


    def build_mp_queries(self, data, is_upsert=False):
        queries = []
        queries.append(self.build_match_query(data['match'], is_upsert))

        if data['match']['start_time']:
            match_id = data['match']['id']
            event_id = 0
            game_id = 0
            match_start = datetime.fromisoformat(data['match']['start_time'])
            last_event_time = match_start
            last_game_time = match_start
            
            for event in data['events']:
                if event['detail']['type'] != 'other':
                    queries.append(self.build_event_query(match_id, event_id, last_event_time, event, is_upsert))
                    event_id += 1
                    last_event_time = datetime.fromisoformat(event['timestamp'])
                else:
                    score_id = 0
                    queries.append(self.build_game_query(match_id, game_id, last_game_time, event, is_upsert))
                    for score in event['game']['scores']:
                        queries.append(self.build_score_query(match_id, game_id, score_id, score, is_upsert))
                        score_id += 1
                    game_id += 1
                    last_game_time = datetime.fromisoformat(event['timestamp'])
        
        return queries


__connection = psycopg2.connect(environ['POSTGRES_URL'])
__cursor = __connection.cursor()
__query_builder = __QueryBuilder()


def get_max_match_id():
    __cursor.execute('select max(id) from match;')
    max_match_table_mp_id = __cursor.fetchone()
    return max_match_table_mp_id[0] if max_match_table_mp_id[0] else -1


def get_match(id):
    __cursor.execute(f"select * from match where id={id};")
    return __cursor.fetchone()


def upsert_mp(data):
    queries = __query_builder.build_mp_queries(data, True)
    for query in queries:
        __cursor.execute(query.sql_template, query.data)
    __connection.commit()


def upsert_match_to_queue(match_id, last_checked):
    __cursor.execute('INSERT INTO match_parser_queue VALUES (%s, %s) ON CONFLICT (match_id) DO UPDATE SET last_checked=%s', (match_id, last_checked, last_checked))
    __connection.commit()


def delete_match_from_queue(match_id):
    __cursor.execute('DELETE FROM match_parser_queue WHERE match_id=%s', (match_id,))
    __connection.commit()
