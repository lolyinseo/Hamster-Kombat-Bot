import aiohttp
import asyncio
import random

from pytoniq import BaseWallet, LiteBalancer, Address
from Cryptodome.Cipher import AES
from Cryptodome.Hash import MD5
from Cryptodome.Util import Padding
from base64 import b64encode, b64decode

from bot.core.entities import AirDropTaskId
from bot.core.headers import Headers
from bot.core.web_client import WebClient
from bot.utils import logger
from bot.utils.profile import Profile
from bot.config import settings
 

#pack string or dict to compressed string
async def pack_data(data: list|str, password: str ):
    if type(data) is list:
        data = ' '.join(data)

    passhash=MD5.new(password.encode('utf-8')).digest()

    cipher = AES.new(passhash, AES.MODE_ECB)
    encrypted = cipher.encrypt(Padding.pad(data.encode('utf-8'), 16))

    return b64encode(encrypted).decode("utf-8")

async def unpack_data(data: str, password): 
    passhash=MD5.new(password.encode('utf-8')).digest()

    cipher = AES.new(passhash, AES.MODE_ECB)
    decrypted = Padding.unpad(cipher.decrypt(b64decode(data)), 16)

    return decrypted.decode("utf-8")

async def attach_wallets(profiles: Profile):
    wallet = input('\nEnter the wallet address: ')

    if not wallet:
        return None

    unpacked_wallet = await unpack_wallet(wallet)

    for profile in profiles:
        await attach_wallet_to_client(profile=profile, wallet=unpacked_wallet)   


async def register_wallet():
    provider = LiteBalancer.from_mainnet_config(trust_level=1)
    await provider.start_up()

    mnemonic, wallet = await BaseWallet.create(provider=provider, version='v4r2')

    
    nonbounceable = Address(wallet.address).to_str(
        is_user_friendly=True, is_bounceable=False, is_url_safe=True
    )

    return mnemonic, nonbounceable


async def attach_wallet_to_client(profile: Profile, wallet: str):
    unpacked_wallet = await unpack_wallet(wallet)

    if unpacked_wallet is None:
        logger.error("Wallet not found")
        return None

    headers = Headers()
    try:
        async with aiohttp.ClientSession(headers=headers) as http_client:
            web_client = WebClient(http_client=http_client, profile=profile)
            tasks = await web_client.get_airdrop_tasks()
            connect_ton_task = next(t for t in tasks if t.id == AirDropTaskId.CONNECT_TON_WALLET)
            if connect_ton_task.is_completed:
                logger.info(f"[{profile.name}] Wallet already attached")
            else:
                await web_client.attach_wallet(wallet=unpacked_wallet)
                logger.success(f"[{profile.name}] Wallet attached")
    except aiohttp.ClientConnectorError as error:
        logger.error(f"Error while attaching wallet: {error}")
        raise

async def detach_wallet(profile: Profile):
    headers = Headers()
    try:
        async with aiohttp.ClientSession(headers=headers) as http_client:
            web_client = WebClient(http_client=http_client, profile=profile)
            tasks = await web_client.delete_wallet()

    except aiohttp.ClientConnectorError as error:
        logger.error(f"Error while detaching wallet: {error}")

async def unpack_wallet(wallet: str) -> str | None:
    try:
        async with aiohttp.ClientSession() as http_client:
            response = await http_client.get(url=f'https://toncenter.com/api/v2/unpackAddress?address={wallet}')
            json = await response.json()
            return json.get('result')
    except aiohttp.ClientConnectorError as error:
        logger.error(f"Error while unpacking wallet: {error}")
        return None

async def add_referral(profile: Profile,  referrer: int):

    try:
        async with aiohttp.ClientSession(headers=Headers()) as http_client:
            web_client = WebClient(http_client=http_client, profile=profile)
            result = await web_client.add_referral(referrer)

            if result:
                logger.info(f"Referral {profile.name} successfully added to {result}")

            return result
    except aiohttp.ClientConnectorError as error:
        logger.error(f"Error while add referral: {error}")


# async def get_minigame_cipher(start: int):

#     headers =  {
#         'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Accept': 'application/json',
#         'Content-Type': 'application/json; charset=utf-8',
#         'Authorization': "Bearer RUoK!pusp6ThEdURUtRenOwUhAsWUCLheBazl!uJLPlS8EbreWLdrupIwabRAsiBu"
#     }
    
#     try:
#         async with aiohttp.ClientSession(headers=headers) as session:                
#             async with session.post(url = settings.MINIGAME_CIPHER_URL, json={"start": start}) as response:
#                 response.raise_for_status()

#                 return await response.json()

#     except Exception as error:
#         raise error
    
async def get_minigame_cipher(start: str):

    GAME_SUCCES_FLAG = 0
    
    start_len = len(start)
    index = (float(start) % (start_len - 2)) + 1

    res = ""
    for i in range(1, start_len + 1):
        if i == index:
            res += str(GAME_SUCCES_FLAG)
        else:
            res += str(random.randint(0, 9))

    return res    
    
async def getFingerprint() -> tuple[str, str]:
    headers =  {
        'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Authorization': f"Bearer {settings.SERVER_SECRET}"
    }
    
    async def get(session: aiohttp.ClientSession, url):
        resp = await session.request('GET', headers=headers, url=url)
        data = await resp.text()
        
        return data
        
    async with aiohttp.ClientSession() as session:

        async with asyncio.TaskGroup() as group:
            fingerprint = group.create_task(get(session=session, url = settings.FINGERPRINT_URL))
            useragent = group.create_task(get(session=session, url = settings.USERAGENT_URL))

        try:
            return fingerprint.result(), useragent.result()
        except Exception as error:
            logger.error(f"Failed to get remoute fingerprint data: {error}")
            raise error
