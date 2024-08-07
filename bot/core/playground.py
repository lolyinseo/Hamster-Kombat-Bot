import aiohttp
import asyncio
import random
import requests
import time
import uuid

from Cryptodome.Hash import MD5
from bot.config import settings
from dataclasses import dataclass
from enum import Enum, StrEnum

class Api(StrEnum):
    LOGIN_CLIENT = "https://api.gamepromo.io/promo/login-client"
    CREATE_CODE ="https://api.gamepromo.io/promo/create-code"
    REGISTER_EVENT ="https://api.gamepromo.io/promo/register-event"

@dataclass
class Promo:
    promoId: str
    blocked: bool
    prefix: str
    eventsCount: int
    codesPerDay: int
    keysPerDay: int
    keysPerCode: int
    registerEvent: bool

    def __init__(self, data: dict):
        self.promoId = data["promoId"]
        self.blocked = data["blocked"]
        self.prefix = data["prefix"]
        self.eventsCount = data["eventsCount"]
        self.keysPerDay = data["keysPerDay"]
        self.codesPerDay = data["codesPerDay"]
        self.keysPerCode = data["keysPerCode"]
        self.registerEvent = False

class App():
    token: str
    blocked: bool
    clientToken: str|None
    promos: list[Promo]|None
    registerEventTimeoutSec: int
    http_client: requests.Session|None = None

    def __init__(self, data: dict):
        self.token = data["token"]
        self.blocked = data["blocked"]
        self.clientToken = data.get("clientToken", None)
        self.registerEventTimeoutSec = data.get("registerEventTimeoutSec", 120)
        self.promos = list(map(lambda d: Promo(data=d), data["promos"])) if data["promos"] else None
        #self.http_client = self.initSession()

    def random_deviceid(self):
        return f"{round(time.time()*1000)}-{random.randint(1000000000000000000, 9999999999999999999)}"
    
    def initSession(self, proxy: str = None):
        headers =  {
            'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 12.0; Lenovo Z2122 Build/NRD91M)',
        }  
        
        session = requests.Session()
        session.headers.update(headers)
        session.proxies.update({'https': proxy if proxy else self.getRandomFromFile()})

        #session.cert = settings.CERT_FILE

        return session
    
    def setProxy(self, proxy):
        if self.http_client:
            self.http_client.proxies.update({'https': proxy})

    def is_clientToken_expired(self, timeout: int):        
        if not self.clientToken:
            return True
        
        created_at = int(self.clientToken.split(':')[-1])
        
        # if time.time()*1000 - created_at > timeout:
        #     return True
        
        #set aexpired to 6 hours
        if time.time()*1000 - created_at > 21600000:
            return True
        
        return False

    async def registerClient(self, proxy: str = None):

        self.http_client = self.initSession(proxy)

        try:
            response = self.http_client.post(url=Api.LOGIN_CLIENT,
                                    json ={"appToken":self.token,"clientId":self.random_deviceid(),"clientOrigin":"deviceid"})
            response.raise_for_status()
            authtoken = response.json().get('clientToken', None)
            
            self.http_client.headers.update({'Authorization':f'Bearer {authtoken}'})

        except Exception as error:
            authtoken = None

        self.clientToken = authtoken

        return authtoken


    async def createCode(self, promo: Promo):

        response = self.http_client.post(url=Api.CREATE_CODE,
                                json ={"promoId": promo.promoId})
        
        response.raise_for_status()
        code = response.json().get('promoCode', None)

        return code if code else None

    async def registerEvent(self, promo: Promo, timeout=20, retries = 10):
        await asyncio.sleep(self.registerEventTimeoutSec)

        try:
            response = self.http_client.post(url=Api.REGISTER_EVENT,
                                    json ={"promoId":promo.promoId,"eventId":str(uuid.uuid4()),"eventOrigin": "undefined"})
            
            response.raise_for_status()            
            hashCode = response.json().get('hasCode', None)
        except Exception as error:
            hashCode = None

        return hashCode if hashCode or retries == 0  else await self.registerEvent(promo, timeout, retries-1)

    def getRandomFromFile(self) -> str:    
        return random.choice(open(settings.USE_PROXY_FROM_FILE).readlines()) if settings.USE_PROXY_FROM_FILE else None

@dataclass
class Playground():
    loginAttemptTimeoutSec: int
    loginSameIpLimitSec: int
    loginSameIpLimitCount: int
    loginSessionTimeoutSec: int
    registerEventTimeoutSec: int
    apps: list[App]|None

    def __init__(self, data: dict):
        self.loginAttemptTimeoutSec = data["loginAttemptTimeoutSec"]
        self.loginSameIpLimitSec = data["loginSameIpLimitSec"]
        self.loginSameIpLimitCount = data["loginSameIpLimitCount"]
        self.loginSessionTimeoutSec = data["loginSessionTimeoutSec"]
        self.registerEventTimeoutSec = data["registerEventTimeoutSec"]
        self.apps = list(map(lambda d: App(data=d), data["apps"])) if data["apps"] else None
    
    @staticmethod
    def getConfigJson():
        headers =  {
            'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 12.0; Lenovo Z2122 Build/NRD91M)',
        }  
        response = requests.get(url=settings.GAMES_JSON_URL, headers=headers)

        return Playground(data=response.json().get("promos", None))
