from os import environ
from celery import Celery
from datetime import datetime, timedelta
from osu_api import instance as api
import database as db
from queue import Empty
from functools import wraps
from pprint import pprint
from itertools import chain


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


@app.task(bind=True, name='load_new_mps', queue='osu_api', max_retries=None)
@osu_api_rate_limit()
def load_new_mps(self):
    try:
        last_match_id = api.get_matches_list()['matches'][0]['id']
        last_checked_mp = max(
            db.get_max_match_id(),
            int(environ['MP_PARSER_START_ID'])
        )
        start_mp = last_checked_mp

        inspect = app.control.inspect()
        all_tasks = list(chain(*chain(*(inspect.reserved().values(), inspect.active().values(), inspect.scheduled().values()))))
        osu_api_tasks_count = len(filter(lambda x: x['delivery_info']['routing_key'] == 'osu_api', all_tasks))
        

        mps_in_waiting: int = 1
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
def load_mp(self, mp_id):
    try:
        mp = api.get_mp(mp_id)
        print("Got mp " + str(mp_id))
        if mp:  # None means mp has private history
            if db.get_match(mp_id):
                db.upsert_mp(mp)
                if mp['match']['end_time']:
                    db.delete_match_from_queue(mp_id)
                else:
                    db.upsert_match_to_queue(mp_id, datetime.now())
            elif not mp['match']['end_time']:
                db.upsert_mp(mp)
                db.upsert_match_to_queue(mp_id, datetime.now())
            else:
                db.upsert_mp(mp)
        else:
            db.delete_match(mp_id)
            db.delete_match_from_queue(mp_id)
    except Exception as e:
        print(f"Exception while loading mp {mp_id}: {e}")
        db.upsert_mp({
            'match': {
                'id': mp_id,
                'name': None,
                'start_time': None,
                'end_time': None,
            },
            'events': list()
        })
        db.upsert_match_to_queue(mp_id, datetime.now())
