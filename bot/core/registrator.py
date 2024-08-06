import asyncio
from urllib.parse import unquote

import requests
from pyrogram import Client as TgClient
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.functions.messages import RequestWebView

from bot.config import settings
from bot.utils import logger
from bot.utils.profile import Profile
from bot.core.helpers import getFingerprint
from bot.exceptions import InvalidSession
from bot.core.headers import Headers
from bot.core.api import Requests


async def add_client() -> None:
    profile_name = input('\nEnter the profile name (press Enter to exit): ')

    if not profile_name:
        return None
    
    proxy = input('\nEnter the proxy address(press Enter to skip): ')

    token = input('\nEnter the token (Leave empty to start TG Auth): ')

    fingerprint, useragent = await getFingerprint()

    if not token:       
        try:
            token,session,user = await register_client_by_tg_auth(profile_name, fingerprint, useragent, proxy)
        except Exception as error:
            logger.error(f"Failed to register client by Telegram Auth: {error}")
            raise
    
    Profile(name=profile_name, token=token, session=session, user_agent = fingerprint.useragent, id=user.id)

    logger.success(f'Profile `{profile_name}` added successfully')


async def register_client_by_tg_auth(profile_name, fingerprint, useragent, proxy) -> None:
    if not settings.API_ID or not settings.API_HASH:
        logger.error('API_ID or API_HASH is not set in the .env file')
        return None

    try:
        tg_client = TgClient(
            name=profile_name,
           #in_memory=True,
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            workdir=settings.ROOT_PATH.joinpath('sessions')
        )
        async with tg_client:
            me = await tg_client.get_me()
        
            access_token = await auth(tg_client=tg_client, fingerprint=fingerprint, useragent=useragent, proxy=proxy )
            session = await tg_client.export_session_string()
        
        if tg_client.is_connected:
            await tg_client.disconnect()    

        #await tg_client.disconnect()

        return access_token, session, me   

    except Exception as error:
        logger.error(f"Unknown error while getting Access Token: {error}")
        raise


async def auth(tg_client: TgClient, fingerprint: str, useragent: str, proxy: str) -> str | None:
    
    headers = Headers({'authorization': '', 'User-Agent': useragent, 'Content-Type': 'application/json'})

    tg_web_data = await get_tg_web_data(tg_client)

    response = requests.post(url=Requests.WEBAPP_AUTH, headers=headers,
                              data=f'{{"initDataRaw":"{requests.utils.quote(tg_web_data, safe='=&')}","fingerprint":{fingerprint}}}',
                              proxies = {'http': proxy} if proxy else None) 

    return response.json().get('authToken')


async def get_tg_web_data(tg_client: TgClient) -> str | None:
    try:
        if not tg_client.is_connected:
            try:
                await tg_client.connect()
            except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                raise InvalidSession("hamster_bot")

        dialogs = tg_client.get_dialogs()
        async for dialog in dialogs:
            if dialog.chat and dialog.chat.username and dialog.chat.username == 'hamster_kombat_bot':
                break

        while True:
            try:
                peer = await tg_client.resolve_peer('hamster_kombat_bot')
                break
            except FloodWait:
                return None

        web_view = await tg_client.invoke(RequestWebView(
            peer=peer,
            bot=peer,
            platform='android',
            from_bot_menu=False,
            url='https://hamsterkombatgame.io/'
        ))

        auth_url = web_view.url
        tg_web_data = unquote(
            string=unquote(
                string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0]))

        # if tg_client.is_connected:
        #     await tg_client.disconnect()

        return tg_web_data

    except InvalidSession as error:
        raise error

    except Exception as error:
        logger.error(f"Unknown error during Authorization: {error}")
        await asyncio.sleep(delay=3)
