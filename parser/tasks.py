from os import environ
from celery import Celery
from datetime import datetime, timedelta, timezone
from osu_api import instance as api, API_RATE_LIMIT_PER_MINUTE as rate_limit
import database as db
from queue import Empty
from functools import wraps
from pprint import pprint
from itertools import chain
import subprocess
import json


environ.setdefault('CELERY_CONFIG_MODULE', 'celery_config')

app = Celery()
app.config_from_envvar('CELERY_CONFIG_MODULE')

last_checked_mp = max(
    db.get_max_match_id(),
    int(environ['MP_PARSER_START_ID'])
)


def osu_api_rate_limit():
    def decorator_func(func):
        @wraps(func)
        def function(self, *args, **kwargs):
            with self.app.connection_for_read() as conn:
                with conn.SimpleQueue('osu_api_tokens', no_ack=True, queue_opts={'max_length':2}) as queue:
                    try:
                        queue.get(block=True, timeout=5)
                        return func(self, *args, **kwargs)
                    except Empty:
                        self.retry(countdown=1)
        return function
    return decorator_func


@app.task(name='token', queue='osu_api_tokens')
def token():
    return 1


@app.task(bind=True, name='load_new_mps', queue='default', max_retries=None)
# @osu_api_rate_limit()
def load_new_mps(self):
    try:
        # Get all osu api tasks
        all_osu_api_tasks = json.loads(str(subprocess.check_output(["python", "rabbitmqadmin", "get", "queue=osu_api", "count=-1", "--format=raw_json", "--host=rabbitmq"], encoding="utf-8")))

        # # This task must be unique
        # if len(list(filter(lambda x: x['name'] == 'load_new_mps', all_tasks))) > 1:
        #     return

        last_match_id = api.get_matches_list()['matches'][0]['id']
        last_checked_mp = max(
            db.get_max_match_id(),
            int(environ['MP_PARSER_START_ID'])
        )

        # osu_api_tasks_count = len(list(filter(lambda x: x['delivery_info']['routing_key'] == 'osu_api', all_tasks)))
        max_tasks_to_post = int(rate_limit - len(all_osu_api_tasks))  # Maximum mps to be queued for loading for this check

        mps_to_load = set()

        # Firstly try to load new mps
        if max_tasks_to_post > 0:
            last_new_mp_to_load = min(last_match_id, last_checked_mp + int(max_tasks_to_post * 0.6)) # TODO
            new_mps_to_load = set(map(lambda x: (x, 1), range(last_checked_mp + 1, last_new_mp_to_load + 1)))
            db.upsert_matches_to_queue(map(lambda x: {'match_id': x[0], 'last_checked': datetime.now(timezone.utc), 'status': 'unchecked', 'last_parsed_event_id': 1}, new_mps_to_load))
            mps_to_load |= new_mps_to_load
            max_tasks_to_post -= len(new_mps_to_load)

        # Secondly try to load mps that was not checked due to error
        if max_tasks_to_post > 0:
            old_mps_to_load = set(map(lambda x: (x[0], x[3]), db.get_queued_matches(limit=max_tasks_to_post)))
            mps_to_load |= old_mps_to_load
        
        # Prevent tasks duplication
        mps_in_queue = set(map(lambda x: int(x['properties']['headers']['argsrepr'][1:-2]), filter(lambda x: x['properties']['headers']['task'] == 'load_mp', all_osu_api_tasks)))
        mps_to_load = set(filter(lambda x: x[0] not in mps_in_queue, mps_to_load))

        print("MPS IN QUEUE: ", sorted(list(mps_in_queue)))
        print("MPS TO LOAD: ", sorted(mps_to_load))
        

        # Create tasks
        for mp_id, last_event_id in mps_to_load:
            load_mp.apply_async((mp_id, last_event_id), priority=7)
        
        print(f"Added {len(mps_to_load)} load_mp tasks")
    except Exception as e:
        print(f"Unexpected error while loading new mps: {e}")


@app.task(bind=True, name='get_users', queue='osu_api', max_retries=None)
@osu_api_rate_limit()
def get_users(self, user_ids):
    print("Got users " + str(user_ids))


@app.task(bind=True, name='get_beatmaps', queue='osu_api', max_retries=None)
@osu_api_rate_limit()
def get_beatmaps(self, beatmap_ids):
    print("Got maps " + str(beatmap_ids))


@app.task(bind=True, name='load_mp', queue='osu_api', max_retries=None)
@osu_api_rate_limit()
def load_mp(self, mp_id, last_event_id):
    try:
        mp = api.get_mp(mp_id, after=last_event_id-1)
        if mp:  # None means mp has private history
            events_ids = list(map(lambda x: x['id'], mp['events']))
            if not events_ids:
                print(mp)
            max_event_id = max(map(lambda x: x['id'], mp['events']))
            is_reached_end = mp['match']['end_time'] and mp['latest_event_id'] == max_event_id
            db.upsert_mp(mp)
            if is_reached_end:
                db.delete_match_from_queue(mp_id)
                print("Got completed mp " + str(mp_id))
            else:
                db.upsert_match_to_queue(mp_id, datetime.now(timezone.utc), "ongoing", max_event_id)
                print("Got ongoing mp " + str(mp_id))
        else:
            print("Got private mp " + str(mp_id))
            if not db.get_events(mp_id):
                db.delete_match(mp_id)
            db.delete_match_from_queue(mp_id)
    except Exception as e:
        print(f"Exception while loading mp {mp_id}: {e}")
        queued_match = db.get_queued_match(mp_id)
        last_parsed_event = int(queued_match[3]) if isinstance(queued_match, tuple) and len(queued_match) >= 4 else 1
        db.upsert_match_to_queue(mp_id, datetime.now(timezone.utc), "error", last_parsed_event)
