import argparse
import asyncio

from itertools import cycle

from better_proxy import Proxy

from bot.config import settings
from bot.core.registrator import add_client
from bot.core.tapper import run_tapper
from bot.core.helpers import attach_wallet_to_client, add_referral, register_wallet, pack_data, detach_wallet
from bot.utils.profile import Profile
from bot.utils.logger import logger

start_text = """

▒█ ▒█ █▀▀█ █▀▄▀█ █▀▀ ▀▀█▀▀ █▀▀ █▀▀█ ▒█ ▄▀ █▀▀█ █▀▄▀█ █▀▀▄ █▀▀█ ▀▀█▀▀ ▒█▀▀█ █▀▀█ ▀▀█▀▀ 
▒█▀▀█ █▄▄█ █ ▀ █ ▀▀█   █   █▀▀ █▄▄▀ ▒█▀▄  █  █ █ ▀ █ █▀▀▄ █▄▄█   █   ▒█▀▀▄ █  █   █   
▒█ ▒█ ▀  ▀ ▀   ▀ ▀▀▀   ▀   ▀▀▀ ▀ ▀▀ ▒█ ▒█ ▀▀▀▀ ▀   ▀ ▀▀▀  ▀  ▀   ▀   ▒█▄▄█ ▀▀▀▀   ▀  

Select an action:

    0. Exit
    1. Add client
    2. Run clicker
    3. Attach wallet to clients
    4. Add referral
    5. Detach wallet
"""


def get_profile_files() -> list[str]:
    profile_files = settings.PROFILE_DIR.glob('*.json')

    return list(profile_files)


def get_proxies() -> list[Proxy]:
    
    if settings.USE_PROXY_FROM_FILE:
        with settings.USE_PROXY_FROM_FILE.open() as file:
            proxies = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_profiles() -> list[Profile]:
    profile_files = get_profile_files()

    if not profile_files:
        raise FileNotFoundError("Not found profile files")

    profiles = []
    for profile_file in profile_files:
        data = settings.PROFILE_DIR.joinpath(profile_file).read_text()
        profile = Profile.model_validate_json(json_data = data, context = {'rewrite': False})

        profiles.append(profile)

    return profiles

async def attach_wallet() -> None:
    profile_name = input('\nEnter the profile name (press Enter to exit): ')

    if not profile_name:
        return None
    
    wallet = input('\nEnter the wallet address(press Enter for register new one): ')

    if not wallet:
        mnemonic, wallet = await register_wallet()

    profile = Profile.load(name = profile_name)

    try:
        await attach_wallet_to_client(profile, wallet)

        profile.wallet = wallet
        profile.mnemonic = await pack_data(mnemonic, settings.ENCRYPT_KEY) if mnemonic else None
    except Exception as error:
        print("An exception occurred:", error)

async def remove_wallet() -> None:
    profile_name = input('\nEnter the profile name (press Enter to exit): ')

    if not profile_name:
        return None
    
    profile = Profile.load(name = profile_name)

    await detach_wallet(profile)

async def add_ref() -> None:
    profile_name = input('\nEnter the profile name (press Enter to exit): ')

    if not profile_name:
        return None
    
    referrer = input('\nEnter Referrer id (press Enter to exit): ')

    if not referrer or not referrer.isdigit():
        return None

    profile = Profile.load(name = profile_name)

    await add_referral(profile, referrer)


async def process() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    action = parser.parse_args().action

    if not action:
        print(start_text)

        while True:
            action = input("> ")

            if not action.isdigit():
                logger.warning("Action must be number")
            elif action not in ['0', '1', '2', '3', '4', '5']:
                logger.warning("Action must be 1-5")
            else:
                action = int(action)
                break

    if action == 1:
        await add_client()
    elif action == 2:        
        profiles = await get_profiles()

        await run_tasks(profiles=profiles)
    elif action == 3:
        await attach_wallet()
    elif action == 4:
        await add_ref()
    elif action == 5:
        await remove_wallet()
    elif action == 0:
        exit()   

#RUN all tasks
async def run_tasks(profiles: list[Profile]):
    logger.info(f"Detected {len(get_profile_files())} clients | {len(get_proxies())} proxies")

    proxies = get_proxies()
    proxies_cycle = cycle(proxies) if proxies else None
    tasks = [asyncio.create_task(run_tapper(profile=profile, proxy=profile.proxy if profile.proxy else next(proxies_cycle) if proxies_cycle else None))
             for profile in profiles]

    await asyncio.gather(*tasks)
