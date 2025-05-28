import requests
import disnake
from disnake.ext import commands
import datetime
import math
from paginator import PaginatorView
from config import API_HOST, MP_LIST_PAGE_SIZE, BOT_TOKEN


bot = commands.InteractionBot()

def get_mp_list(name, players, beatmaps, page):
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
    
    embed_dict = {
        "title": "",
        "fields": list(map(format_mp_field, r['matches'])),
        "footer": {"text": f"LOBBIES COUNT: {count} СТРАНИЦА {page+1} ИЗ {math.ceil(count/MP_LIST_PAGE_SIZE)}"}
    }
    embed = disnake.Embed.from_dict(embed_dict)
    return {"embed": embed, "count": count}

@bot.slash_command(name="mp-list")
async def mp_list(
    inter: disnake.ApplicationCommandInteraction, 
    name: str | None = commands.Param(default=None, name="name", description="Filter for lobby name. You can use regex by surrounding value with ``"), 
    players: str | None = commands.Param(default=None, name="players", description="Player ids separated with comma"),
    beatmaps: str | None = commands.Param(default=None, name="beatmaps", description="Beatmap ids separated with comma")
):
    await inter.response.defer()
    first_page = get_mp_list(name, players, beatmaps, 0)
    count = first_page["count"]
    if count > 0:
        view = PaginatorView(get_page=lambda x: get_mp_list(name, players, beatmaps, x), page_size=MP_LIST_PAGE_SIZE, count=count)
        await inter.edit_original_message(embed=first_page["embed"], view=view)
    else:
        await inter.edit_original_message("МУЛЬТИПЛЕЕР ЛОББИ НЕ НАЙДЕ НО")

            
if __name__ == '__main__':
    bot.run(BOT_TOKEN)