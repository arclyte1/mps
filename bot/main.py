import requests
import disnake
from disnake.ext import commands
import datetime
import math
from paginator import PaginatorView
from enum import Enum
from config import API_HOST, MP_LIST_PAGE_SIZE, BOT_TOKEN
# from ..parser.database import OrderBy

class OrderBy(Enum):
    START_TIME = 'id'
    END_TIME = 'end_time'
    NAME = 'name'


bot = commands.InteractionBot()

MP_LIST_ORDER_BY_CHOISES = {
    "Start time": OrderBy.START_TIME.name,
    "End time": OrderBy.END_TIME.name,
    "Name": OrderBy.NAME.name
}

def get_mp_list(name, players, beatmaps, page, order_by, reverse_order):
    r = requests.post(f'{API_HOST}/mps', json={'name': name, 'page': page, 'limit': MP_LIST_PAGE_SIZE, 'users': players, 'beatmaps': beatmaps}).json()
    count = r['count']

    def format_mp_field(x):
        start_time = int(datetime.datetime.fromisoformat(x['start_time']).replace(tzinfo=datetime.timezone.utc).timestamp())
        time = f'<t:{start_time}:R>'
        maps_played = len(x['games'])
        user_ids = set()
        for game in x['games']:
            for score in game['scores']:
                user_ids.add(score['user_id'])
        for event in x['events']:
            if user_id := event['user_id']:
                user_ids.add(user_id)
        user_count = len(user_ids)
        return {
            "name": "",
            "value": f"[{x['name']}](https://osu.ppy.sh/mp/{x['id']}) ({x['id']})\n{time}\t{maps_played} maps played\t{user_count} players",
            "inline": "false"
        }   

    found_mps = f"{count:,d}".replace(",", " ")
    embed_dict = {
        "title": "",
        "fields": list(map(format_mp_field, r['matches'])),
        "footer": {"text": f"Found mps: {found_mps} | Page: {page+1}/{math.ceil(count/MP_LIST_PAGE_SIZE)}"}
    }
    embed = disnake.Embed.from_dict(embed_dict)
    return {"embed": embed, "count": count}

@bot.slash_command(name="mp-list", description="Get list of mps")
async def mp_list(
    inter: disnake.ApplicationCommandInteraction, 
    name: str | None = commands.Param(default=None, name="name", description="Filter for lobby name. You can use regex by surrounding value with ``"), 
    players: str | None = commands.Param(default=None, name="players", description="Player ids separated with comma"),
    beatmaps: str | None = commands.Param(default=None, name="beatmaps", description="Beatmap ids separated with comma"),
    order_by: str | None = commands.Param(default=OrderBy.START_TIME.name, name="order_by", description="Value to ordey by (start time by default)", choices=MP_LIST_ORDER_BY_CHOISES),
    reverse_order: bool | None = commands.Param(default=False, name="reverse_order", description="Output in reverse order")
):
    await inter.response.defer()
    first_page = get_mp_list(name, players, beatmaps, 0, order_by, reverse_order)
    count = first_page["count"]
    if count > 0:
        view = PaginatorView(get_page=lambda x: get_mp_list(name, players, beatmaps, x, order_by, reverse_order), page_size=MP_LIST_PAGE_SIZE, count=count)
        await inter.edit_original_message(embed=first_page["embed"], view=view)
    else:
        await inter.edit_original_message("МУЛЬТИПЛЕЕР ЛОББИ НЕ НАЙДЕ НО")


if __name__ == '__main__':
    bot.run(BOT_TOKEN)