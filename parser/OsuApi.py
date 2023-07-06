import asyncio
import aiohttp
import time
import json


class OsuApi:
    token: str
    token_time: int
    client_id: int
    client_secret: str

    # Create or read file with token
    def __init__(self, client_id: int, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            with open('osuApiToken.txt', 'r') as tokenFile:
                self.token = tokenFile.readline().replace('\n', '')
                self.token_time = int(tokenFile.readline().replace('\n', ''))
        except:
            async def refresh():
                async with aiohttp.ClientSession() as session:
                    await self.__refresh_token(session)

            asyncio.run(refresh())

    async def __refresh_token(self, session):
        async with session.post('https://osu.ppy.sh/oauth/token',
                                data={'grant_type': 'client_credentials',
                                      'client_id': self.client_id,
                                      'client_secret': self.client_secret,
                                      'scope': 'public'}
                                ) as resp:
            response = await resp.json()
            tokenFile = open('osuApiToken.txt', 'w')
            self.token = response['access_token']
            self.token_time = response['expires_in'] + int(time.time())
            print(f'{self.token}\n{self.token_time}', file=tokenFile)
            tokenFile.close()

    async def __get_request_async(self, session, request: str):
        body = 'https://osu.ppy.sh/api/v2'
        async with session.get(body + request,
                               headers={'Content-Type': 'application/json',
                                        'Accept': 'application/json',
                                        'Authorization': 'Bearer ' + self.token}) as resp:
            response = await resp.json()
            return response

    async def __get_requests_async(self, requests: list):
        async with aiohttp.ClientSession() as session:
            if self.token_time < int(time.time()):
                await self.__refresh_token(session)
            responses = []
            for request in requests:
                responses.append(asyncio.ensure_future(self.__get_request_async(session, request)))
            return await asyncio.gather(*responses)

    def get_requests(self, requests: list):
        return asyncio.run(self.__get_requests_async(requests))

    def get_request(self, request: str):
        return self.get_requests([request])[0]

    def get_user(self, username: str):
        return self.get_request(f'/users/{username}/osu')

    def get_users(self, usernames: list):
        return list(self.get_requests(list(map(lambda x: f'/users/{x}/osu', usernames))))

    def get_mp(self, id: int):
        mp = self.get_request(f'/matches/{id}')
        return mp if 'match' in mp else None

    def get_mps(self, ids: list):
        return filter(lambda x: 'match' in x, list(self.get_requests(list(map(lambda x: f'/matches/{x}', ids)))))
