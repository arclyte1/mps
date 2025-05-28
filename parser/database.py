from pprint import pprint
from os import environ
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta, timezone
from typing import Callable, Any
from enum import Enum


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
            query.sql_template += ' ON CONFLICT (id) DO UPDATE SET (name, start_time, end_time) = (%(name)s, %(start_time)s, %(end_time)s)'
        return query


    def build_event_query(self, match_id: int, event_id: int, match_start: datetime, event, is_upsert):
        deltatime = int((datetime.fromisoformat(event['timestamp']) - match_start).total_seconds())
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
            query.sql_template += ' ON CONFLICT (match_id, id) DO UPDATE SET (type, user_id, deltatime) = (%(type)s, %(user_id)s, %(deltatime)s)'
        return query


    def build_game_query(self, match_id: int, game_id: int, match_start: datetime, event, is_upsert):
        start_delta = int((datetime.fromisoformat(event['timestamp']) - match_start).total_seconds())
        end_delta = None  # 'null'
        if event['game']['end_time']:
            end_delta = int((datetime.fromisoformat(event['game']['end_time']) - match_start).total_seconds()) - start_delta
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
            query.sql_template += ' ON CONFLICT (match_id, id) DO UPDATE SET (start_deltatime, end_deltatime, mods, game_mode, beatmap_id, scoring_type, team_type)'\
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
            query.sql_template += ' ON CONFLICT (match_id, game_id, id) DO UPDATE SET (user_id, score, max_combo, count_100, count_300, count_50, count_geki,'\
                ' count_katu, count_miss, passed) = (%(user_id)s, %(score)s, %(max_combo)s, %(count_100)s,'\
                ' %(count_300)s, %(count_50)s, %(count_geki)s, %(count_katu)s, %(count_miss)s, %(passed)s)'
        return query


    def build_mp_queries(self, data, is_upsert=False, max_game_id=-1, max_event_id=-1):
        queries = []
        queries.append(self.build_match_query(data['match'], is_upsert))

        if data['match']['start_time']:
            match_id = data['match']['id']
            event_id = max_event_id + 1
            game_id = max_game_id + 1
            match_start = datetime.fromisoformat(data['match']['start_time'])
            
            for event in data['events']:
                if event['detail']['type'] != 'other':
                    queries.append(self.build_event_query(match_id, event_id, match_start, event, is_upsert))
                    event_id += 1
                else:
                    score_id = 0
                    queries.append(self.build_game_query(match_id, game_id, match_start, event, is_upsert))
                    for score in event['game']['scores']:
                        queries.append(self.build_score_query(match_id, game_id, score_id, score, is_upsert))
                        score_id += 1
                    game_id += 1
        
        return queries


def get_max_match_id():
    def q(conn, cursor):
        cursor.execute('SELECT MAX(match_id) FROM (SELECT id AS match_id FROM match UNION SELECT match_id FROM match_parser_queue) foo')
        max_match_table_mp_id = cursor.fetchone()
        return max_match_table_mp_id[0] if max_match_table_mp_id[0] else -1
    
    return db_query(q)


def get_match(id):
    def q(conn, cursor):
        cursor.execute(f'SELECT * FROM match WHERE id={id}')
        return cursor.fetchone()
    
    return db_query(q)


def get_events(match_id):
    def q(conn, cursor):
        cursor.execute(f'SELECT * FROM event WHERE match_id = %s', (match_id,))
        return cursor.fetchall()
    
    return db_query(q)


def upsert_mp(data):
    def q(conn, cursor):
        cursor.execute("SELECT MAX(id) FROM game WHERE match_id = %s", (data['match']['id'],))
        game_id_result = cursor.fetchone()
        max_game_id = game_id_result[0] if game_id_result[0] else -1
        cursor.execute("SELECT MAX(id) FROM event WHERE match_id = %s", (data['match']['id'],))
        event_id_result = cursor.fetchone()
        max_event_id = event_id_result[0] if event_id_result[0] else -1
        __query_builder = __QueryBuilder()
        queries = __query_builder.build_mp_queries(data, True, max_game_id, max_event_id)
        for query in queries:
            cursor.execute(query.sql_template, query.data)
        conn.commit()
    
    return db_query(q)


def delete_match(id):
    def q(conn, cursor):
        cursor.execute('DELETE FROM match WHERE id=%s', (id,))
        conn.commit()
    
    return db_query(q)


def upsert_match_to_queue(match_id, last_checked, status, last_parsed_event_id):
    def q(conn, cursor):
        cursor.execute(
            'INSERT INTO match_parser_queue VALUES (%s, %s, %s, %s) ON CONFLICT (match_id) DO UPDATE SET (last_checked, match_status, last_parsed_event_id) = (%s, %s, %s)',
            (match_id, last_checked, status, last_parsed_event_id, last_checked, status, last_parsed_event_id)
        )
        conn.commit()
    
    return db_query(q)


def upsert_matches_to_queue(matches):
    def q(conn, cursor):
        for match in matches:
            cursor.execute(
                'INSERT INTO match_parser_queue VALUES (%(match_id)s, %(last_checked)s, %(status)s, %(last_parsed_event_id)s) ON CONFLICT (match_id) DO UPDATE SET (last_checked, match_status, last_parsed_event_id) = (%(last_checked)s, %(status)s, %(last_parsed_event_id)s)',
                match
            )
        conn.commit()

    return db_query(q)


def delete_match_from_queue(match_id):
    def q(conn, cursor):
        cursor.execute('DELETE FROM match_parser_queue WHERE match_id=%s', (match_id,))
        conn.commit()

    return db_query(q)


def get_queued_matches(limit):
    def q(conn, cursor):
        max_date = (datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat() # TODO
        cursor.execute('SELECT * FROM match_parser_queue WHERE last_checked < %s ORDER BY last_checked LIMIT %s', (max_date, limit))
        return cursor.fetchall()
    
    return db_query(q)


def get_queued_match(id: int):
    def q(conn, cursor):
        cursor.execute('SELECT * FROM match_parser_queue WHERE match_id = %s', (id,))
        return cursor.fetchone()
    
    return db_query(q)

def update_last_checked_match_queue(match_id, last_checked):
    def q(conn, cursor):
        cursor.execute()


class OrderBy(Enum):
    START_TIME = 'id'
    END_TIME = 'end_time'
    NAME = 'name'


def get_matches(limit: int, 
                offset: int, 
                users: list,
                beatmaps: list,
                name: str | None = None, 
                use_regex: bool = False, 
                case_sensitive: bool = False, 
                order_by: OrderBy = OrderBy.START_TIME, 
                is_asc: bool = False):
    def q(conn, cursor):
        args = {
            'limit': limit,
            'offset': offset
        }
        ids_in = list()
        name_filter = None

        # Users filter
        for i, user in enumerate(users):
            ids_in.append(f'((select match_id from score where user_id = %(u_{i})s) union (select match_id from event where user_id = %(u_{i})s))')
            args[f'u_{i}'] = user

        # Beatmaps filter
        for i, beatmap in enumerate(beatmaps):
            ids_in.append(f'(select match_id from game where beatmap_id = %(b_{i})s)')
            args[f'b_{i}'] = beatmap

        if name:
            if use_regex:
                args['name'] = name
                if case_sensitive:
                    name_filter = 'name ~ %(name)s'
                else:
                    name_filter = 'name ~* %(name)s'
            else:
                args['name'] = '%' + name.replace('%', '\%') + '%'
                if case_sensitive:
                    name_filter = 'name like %(name)s'
                else:
                    name_filter = 'name ilike %(name)s'

        # Add conditions
        conditions = list()

        if ids_in:
            conditions.append(f'id in ({" intersect ".join(ids_in)})')

        if name_filter:
            conditions.append(name_filter)

        # Final condition
        condition = ''
        if conditions:
            condition += f'WHERE {" AND ".join(conditions)} '
        
        cursor.execute('SELECT COUNT(*) FROM match ' + condition, args)
        count = cursor.fetchone()

        condition += f'ORDER BY {order_by.value} {"ASC" if is_asc else "DESC"}'
        condition += ' LIMIT %(limit)s OFFSET %(offset)s'

        print(f"Select sql: {'SELECT * FROM match ' + condition}")
        cursor.execute('SELECT * FROM match ' + condition, args)
        matches = cursor.fetchall()
        for match in matches:
            if match['start_time'] != None:
                cursor.execute('SELECT * FROM event WHERE match_id=%s', (match['id'],))
                match['events'] = cursor.fetchall()
                for i in range(len(match['events'])):
                    if i != 0:
                        match['events'][i]['datetime'] = (datetime.fromisoformat(match['events'][i-1]['datetime']) + timedelta(seconds=match['events'][i]['deltatime'])).isoformat()
                    else:
                        match['events'][i]['datetime'] = (datetime.fromisoformat(str(match['start_time'])) + timedelta(seconds=match['events'][i]['deltatime'])).isoformat()
                    match['events'][i].pop('deltatime')

                cursor.execute('SELECT * FROM game WHERE match_id=%s', (match['id'],))
                match['games'] = cursor.fetchall()
                for i in range(len(match['games'])):
                    start_time = None
                    if i != 0:
                        start_time = datetime.fromisoformat(match['games'][i-1]['start_time']) + timedelta(seconds=match['games'][i]['start_deltatime'])
                    else:
                        start_time = datetime.fromisoformat(str(match['start_time'])) + timedelta(seconds=match['games'][i]['start_deltatime'])
                    match['games'][i]['start_time'] = start_time.isoformat()
                    match['games'][i].pop('start_deltatime')
                    match['games'][i]['end_time'] = None if match['games'][i]['end_deltatime'] == None else (start_time + timedelta(seconds=match['games'][i]['end_deltatime'])).isoformat()
                    match['games'][i].pop('end_deltatime')

                cursor.execute('SELECT * FROM score WHERE match_id=%s', (match['id'],))
                scores = cursor.fetchall()
                for game in match['games']:
                    game['scores'] = list(filter(lambda x: x['game_id'] == game['id'], scores))
        return {
            'matches': matches,
            'count': count["count"],
        }

    return db_query(q, cursor_factory=psycopg2.extras.RealDictCursor)


def db_query(f: Callable[[Any, Any], Any], cursor_factory = None) -> Any:
    conn = psycopg2.connect(environ['POSTGRES_URL'])
    res = None
    with conn.cursor(cursor_factory=cursor_factory) as cursor:
        res = f(conn, cursor)
    conn.close()
    return res
