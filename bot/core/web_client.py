import json as json_parser
from time import time

import aiohttp

from bot.core.entities import AirDropTask, Boost, Upgrade, User, Task, DailyCombo, AirDropTaskId, DailyCipher, MiniGame
from bot.core.api import Requests
from bot.utils.profile import Profile


class WebClient:
    profile: Profile
    http_client: aiohttp.ClientSession

    def __init__(self, http_client: aiohttp.ClientSession, profile: Profile):

        self.profile = profile
        self.http_client = http_client
        self.http_client.headers["User-Agent"] = profile.user_agent
        self.http_client.headers["Authorization"] = f"Bearer {profile.token}"

    async def get_user_data(self) -> User:
        response = await self.make_request(Requests.SYNC)
        user_data = response.get('clickerUser') or response.get('found', {}).get('clickerUser', {})
        return User(data=user_data)

    async def get_tasks(self) -> list[Task]:
        response = await self.make_request(Requests.LIST_TASKS)
        return list(map(lambda d: Task(data=d), response['tasks']))

    async def select_exchange(self, exchange_id: str) -> bool:
        await self.make_request(Requests.SELECT_EXCHANGE, json={'exchangeId': exchange_id})
        return True
    
    async def start_minigame(self) -> MiniGame:
        response = await self.make_request(Requests.START_MINIGAME)
        return MiniGame(data=response.get('dailyKeysMiniGame'))
    
    async def claim_minigame(self, code) -> MiniGame:
        response = await self.make_request(Requests.CLAIM_MINIGAME, json={'cipher': code})
        return MiniGame(data=response.get('dailyKeysMiniGame')) if "dailyKeysMiniGame" in response else None
    
    async def get_promos(self) -> list:
        response = await self.make_request(Requests.GET_PROMOS)
        return response.get('states', None)
    
    async def apply_promo(self, code) -> User:
        response = await self.make_request(Requests.APPLY_PROMO, json={'promoCode': code})
        
        user_data = response.get('clickerUser') or response.get('found', {}).get('clickerUser', {})
        return User(data=user_data)

    async def check_task(self, task_id: str) -> bool:
        response = await self.make_request(Requests.CHECK_TASK, json={'taskId': task_id})
        return response.get('task', {}).get('isCompleted', False)

    async def apply_boost(self, boost_id: str) -> User:
        response = await self.make_request(Requests.BUY_BOOST, json={'timestamp':round(time()*1000),'boostId':boost_id})
        user_data = response.get('clickerUser') or response.get('found', {}).get('clickerUser', {})

        return User(data=user_data)

    async def get_upgrades(self) -> tuple[list[Upgrade], DailyCombo]:
        response = await self.make_request(Requests.UPGRADES_FOR_BUY)
        return list(map(lambda x: Upgrade(data=x), response['upgradesForBuy'])), \
            DailyCombo(data=response.get('dailyCombo', {}))

    async def buy_upgrade(self, upgrade_id: str) -> tuple[User, list[Upgrade], DailyCombo]:
        response = await self.make_request(Requests.BUY_UPGRADE, json={'timestamp':round(time()*1000),'upgradeId':upgrade_id})
        if 'found' in response:
            response = response['found']
        user_data = response.get('clickerUser')
        return User(data=user_data), \
            list(map(lambda x: Upgrade(data=x), response.get('upgradesForBuy', []))), \
            DailyCombo(data=response.get('dailyCombo', {}))

    async def get_boosts(self) -> list[Boost]:
        response = await self.make_request(Requests.BOOSTS_FOR_BUY)
        return list(map(lambda x: Boost(data=x), response['boostsForBuy']))

    async def send_taps(self, available_energy: int, taps: int) -> User:
        response = await self.make_request(Requests.TAP,
                                           json={ 'count':taps,'availableTaps':available_energy,'timestamp':round(time()*1000)})
        user_data = response.get('clickerUser') or response.get('found', {}).get('clickerUser', {})

        return User(data=user_data)

    async def get_me_telegram(self) -> None:
        await self.make_request(Requests.ME_TELEGRAM)

    async def get_config(self) -> tuple[DailyCipher, MiniGame]:
        response = await self.make_request(Requests.CONFIG)

        return DailyCipher(data=response.get('dailyCipher')) if "dailyCipher" in response else None, \
            MiniGame(data=response.get('dailyKeysMiniGame')) if "dailyKeysMiniGame" in response else None

    async def claim_daily_cipher(self, cipher: str) -> User:
        response = await self.make_request(Requests.CLAIM_DAILY_CIPHER, json={'cipher': cipher})
        if 'found' in response:
            response = response['found']
        return User(data=response.get('clickerUser'))

    async def claim_daily_combo(self) -> User:
        response = await self.make_request(Requests.CLAIM_DAILY_COMBO)
        if 'found' in response:
            response = response['found']
        return User(data=response.get('clickerUser'))

    async def get_referrals_count(self) -> int:
        response = await self.make_request(Requests.REFERRAL_STAT, json={'offset': 0})
        if 'found' in response:
            response = response['found']
        return response.get('count', 0)
        
    async def add_referral(self, friendUserId: int) -> dict:
        response = await self.make_request(Requests.ADD_REFERAL,
                                           json={'friendUserId':int(friendUserId)})
        return response.get('friendFirstName', None)

    async def attach_wallet(self, wallet: str) -> bool:
        response = await self.make_request(Requests.CHECK_AIRDROP_TASK,
                                           json={'id':AirDropTaskId.CONNECT_TON_WALLET,'walletAddress':wallet})
        return response.get('airdropTask', {}).get('isCompleted', False)
    
    async def delete_wallet(self) -> bool:
        response = await self.make_request(Requests.DELETE_WALLET)
        
        return True
    
    async def get_airdrop_tasks(self) -> list[AirDropTask]:
        response = await self.make_request(Requests.LIST_AIRDROP_TASKS)
        return list(map(lambda d: AirDropTask(data=d), response['airdropTasks']))

    async def make_request(self, request: Requests, json: dict | None = None) -> dict:

        response = await self.http_client.post(url=request, json=json)        
        response_text = await response.text()

        if response.status != 422:
            response.raise_for_status()
        
        return json_parser.loads(response_text)
