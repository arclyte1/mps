from os import environ
from celery import Celery
from datetime import datetime, timedelta
from osu_api import instance
import database as db


environ.setdefault('CELERY_CONFIG_MODULE', 'celery_config')

app = Celery(
    'tasks',
    backend=environ['BACKEND_URL'],
    broker=environ['BROKER_URL']
)
app.config_from_envvar('CELERY_CONFIG_MODULE')

app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'load_new_mps',
        'schedule': 10.0,
        'args': ()
    },
}

current_mp_id = max(
    db.get_max_match_id(),
    int(environ['MP_PARSER_START_ID'])
)


@app.task(name='token')
def token():
    return 1


@app.task(name='load_new_mps')
def load_new_mps():
    print("hello")


@app.task(name='get_users', queue='osu_api', priority=7)
def get_users(user_ids):
    pass


@app.task(name='get_beatmaps', queue='osu_api', priority=7)
def get_beatmaps(beatmap_ids):
    pass


@app.task(name='load_mp', queue='osu_api', priority=5)
def load_mp(mp_id):
    try:
        mp = instance.get_mp(mp_id)
        if instance.get_mp(mp_id):  # None means mp has private history
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
