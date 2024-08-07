# pylint: disable=W0718

import asyncio
import traceback
from random import randint, choice, uniform
from time import time
from base64 import urlsafe_b64encode, b64decode
from datetime import datetime,timezone

import aiohttp
from aiohttp_proxy import ProxyConnector

from bot.config import settings
from bot.utils.combo import combo
from bot.core.entities import DailyCipher, Upgrade, User, Boost, Task, DailyCombo, Sleep, SleepReason, MiniGame
from bot.core.playground import Playground, App, Promo
from bot.core.web_client import WebClient
from bot.exceptions import InvalidSession
from bot.utils import logger
from bot.utils.profile import Profile
from .headers import Headers
from bot.core.helpers import get_minigame_cipher

class Tapper:
    def __init__(self, web_client: WebClient) -> None:
        self.web_client = web_client
        self.profile = web_client.profile
        self.user = User(data={})
        self.upgrades: list[Upgrade] = []
        self.boosts: list[Boost] = []
        self.tasks: list[Task] = []
        self.apps: list[App] = []
        self.daily_combo: DailyCombo | None = None
        self.daily_cipher: DailyCipher | None = None
        self.minigame: MiniGame | None = None        
        self.preferred_sleep: Sleep | None = None

    def update_preferred_sleep(self, delay: float, sleep_reason: SleepReason):
        if self.preferred_sleep is not None and delay >= self.preferred_sleep.delay:
            return
        self.preferred_sleep = Sleep(delay=min(delay, settings.MAX_SLEEP_TIME), sleep_reason=sleep_reason, created_time=time())

    def get_spending_balance(self, upgarde: Upgrade = None):
        if upgarde and upgarde.expires_at:
            now = datetime.now(timezone.utc)
            if (upgarde.expires_at-now).total_seconds() < 86400:
                return self.user.balance - self.profile.min_balance
        
        return self.user.balance - self.user.earn_per_hour*self.profile.balance_strategy

    def upgrade_calculate_significance(self, upgarde: Upgrade) -> float:
        if upgarde.price == 0:
            return 0
        if self.user.earn_per_hour == 0:
            return upgarde.price / upgarde.earn_per_hour
        return upgarde.price / upgarde.earn_per_hour \
            + upgarde.cooldown_seconds / 3600 \
            + max((upgarde.price - self.get_spending_balance()) / self.user.earn_per_hour, 0)

    async def earn_money(self)-> User:
        user = await self.web_client.get_user_data()

        if not user.exchange_id or user.exchange_id == "hamster":
            await self.web_client.select_exchange(exchange_id:=choice(["binance", "bybit", "okx", "bingx", "htx", "kucoin"]))
            status = await self.web_client.check_task(task_id="select_exchange")
            if status is True:
                logger.success(f"[{self.profile.name}] Successfully selected exchange <y>{exchange_id}</y>")

        logger.info(f"[{self.profile.name}] Last passive earn: <g>+{user.last_passive_earn}</g> | "
                    f"Earn every hour: <y>{user.earn_per_hour}</y>")
        return user

    async def check_daily_cipher(self):
        if self.daily_cipher is None or self.daily_cipher.is_claimed:
            return False

        decoded_cipher = b64decode(f"{self.daily_cipher.cipher[:3]}{self.daily_cipher.cipher[4:]}").decode(
            "utf-8")
        self.user = await self.web_client.claim_daily_cipher(cipher=decoded_cipher)
        logger.success(f"[{self.profile.name}] Successfully get cipher reward | "
                       f"Cipher: <m>{decoded_cipher}</m> | Reward coins: <g>+{self.daily_cipher.bonus_coins}</g>")
        await self.sleep(delay=5)
    

    async def check_minigame(self):
        if self.minigame is None or self.minigame.is_claimed or self.minigame.toNextAttempt > 0  or self.minigame.remainSeconds <= 0:
            return False
        
        logger.info(f"[{self.profile.name}] Detecting one more round of the minigame, let's try to claim")

        start = self.minigame.startDate.timestamp()        
        start_str = str(int(start)) if start.is_integer() else str(start)        
        cipher = await get_minigame_cipher(start_str)
        
        game = await self.web_client.start_minigame()
        await self.sleep(delay=uniform(game.toGuess*0.8, game.toGuess*0.9))
        
        code = urlsafe_b64encode(f'{cipher}|{self.profile.id}'.encode())
        self.minigame = await self.web_client.claim_minigame(code.decode())

        if self.minigame.is_claimed:
            logger.success(f"[{self.profile.name}] Successfully claimed daily minigame key")
        else:
            logger.warning(f"[{self.profile.name}] Claim minigame failed")  

    async def check_playground(self, plyaground: Playground):        

        logger.info(f"[{self.profile.name}] Start checking Playground games, it may take a while")

        if not plyaground:
            return
        
        states = await self.web_client.get_promos()

        #check alredy auth app
        for app in self.apps:
            
            available_promo = list(filter(lambda p: not p.blocked and next((s for s in states if s["promoId"] == p.promoId), {}).get('receiveKeysToday', 0) < p.keysPerDay, app.promos))

            if not available_promo or app.is_clientToken_expired(plyaground.loginSessionTimeoutSec):
                self.apps.remove(app)
                continue

            #try to get and apply promo
            for promo in available_promo:
                if promo.registerEvent:
                    promocode = await app.createCode(promo)
                    
                    if promocode:
                        await self.sleep(delay=5)
                        try:
                            result = await self.web_client.apply_promo(promocode)
                            logger.success(f"[{self.profile.name}] Successfully applied the code for the game <e>{promo.prefix}</e>")
                        except Exception as error:
                            logger.error(f"[{self.profile.name}] Error applying code for the game <e>{promocode}</e>")
                    
                promo.registerEvent = await app.registerEvent(promo=promo) 


        # now check new app
        # remove app with blocked = True 
        apps = list(filter(lambda a: not a.blocked, plyaground.apps))
        
        # remove dup with self.app
        apps = list(filter(lambda p: not next((a for a in self.apps if a.token == p.token), None), apps))

        # register client for new app and add to self.apps 
        for app in apps:
            available_promo = list(filter(lambda p: not p.blocked and next((s for s in states if s["promoId"] == p.promoId), {}).get('receiveKeysToday', 0) < p.keysPerDay, app.promos))

            if not available_promo:
                continue

            token = await app.registerClient(self.profile.proxy)
            
            if token:
                for promo in available_promo:
                    promo.registerEvent = await app.registerEvent(promo=promo) 

                self.apps.append(app)


    async def check_daily_combo(self):
        if not self.daily_combo.is_claimed:
            reward_claimed = await self.try_claim_daily_combo()
            if reward_claimed:
                return False

            if combo.expired < time():
                logger.info(f"[{self.profile.name}] Cached combo file expired, let's try to update remotely...")
                if not await combo.update():
                    logger.warning(f"[{self.profile.name}] Remoute combo file expired. Combo update skiped.")
                    return False        

            combo_upgrades: list[Upgrade] = list(
                filter(lambda u: u.id in combo.combo and u.id not in self.daily_combo.upgrade_ids, self.upgrades))

            if not all(await asyncio.gather(*(self.ready_for_upgrade(upgrade) for upgrade in combo_upgrades))):
                logger.warning(f"[{self.profile.name}] One element of Combo not ready or conditions not met. Combo Upgarde skipped")
                return False

            for upgrade in combo_upgrades:
                ready = await self.recursive_upgrade_to(upgrade)
                if not ready:
                    return False

            await self.try_claim_daily_combo()
        return False
    
    async def ready_for_upgrade(self, upgrade: Upgrade) -> bool:
        if upgrade.can_upgrade():            
            return True
        elif upgrade.condition['_type'] == 'ByUpgrade':
            return await self.ready_for_upgrade(next((x for x in self.upgrades if x.id == upgrade.condition['upgradeId']), None))
        
        logger.warning(f"[{self.profile.name}] Upgrade <e>{upgrade.name}</e> not ready. Condition <e>{upgrade.condition}</e> not met")
        return False
    
    async def recursive_upgrade_to(self, upgrade):
        if upgrade.can_upgrade():
            if upgrade.price > max(self.user.balance - self.user.earn_per_hour*self.profile.balance_strategy, self.user.balance - self.profile.min_balance):
                logger.info(f"[{self.profile.name}] Not enough money for upgrade combo <e>{upgrade.name}</e>. Price is <e>{upgrade.price}</e>")
                self.update_preferred_sleep(
                    delay=int((upgrade.price - self.profile.min_balance) / self.user.earn_per_sec),
                    sleep_reason=SleepReason.WAIT_UPGRADE_MONEY
                )
                return True

            if upgrade.cooldown_seconds > 0:
                logger.info(f"[{self.profile.name}] Upgrade combo <e>{upgrade.name}</e> on cooldown for <y>{upgrade.cooldown_seconds}s</y>")
                self.update_preferred_sleep(
                    delay=upgrade.cooldown_seconds,
                    sleep_reason=SleepReason.WAIT_UPGRADE_COOLDOWN
                )
                return True
            
            await self.do_upgrade(upgrade=upgrade)

            logger.info(f"[{self.profile.name}] Upgrade <e>{upgrade.name}</e> for daily combo is done.")
            return True

        elif upgrade.condition['_type'] == 'ByUpgrade' and not upgrade.is_expired and upgrade.max_level >= upgrade.level:
            return await self.recursive_upgrade_to( next((x for x in self.upgrades if x.id == upgrade.condition['upgradeId']), None))

        logger.info(f"[{self.profile.name}] Can't upgrade recursive <e>{upgrade.name}</e> for daily combo. Condition <e>{upgrade.condition}</e>. Skipped")
        return False

    async def try_claim_daily_combo(self) -> bool:
        if len(self.daily_combo.upgrade_ids) != 3:
            return False
        self.user = await self.web_client.claim_daily_combo()
        logger.success(f"[{self.profile.name}] Successfully get daily combo reward | "
                       f"Reward coins: <g>+{self.daily_combo.bonus_coins}</g>")
        await self.sleep(delay=5)
        return True
    
    async def parse_config(self) -> tuple:
        daily_cipher, minigame = await self.web_client.get_config() 
        await self.sleep(delay=5)
        return daily_cipher, minigame

    async def make_upgrades(self):
        if settings.UPGRADE_DAILY_COMBO:
            wait_for_combo_upgrades = await self.check_daily_combo()
            if wait_for_combo_upgrades:
                return

        while True:
            available_upgrades = filter(lambda u: u.can_upgrade() and u.cooldown_seconds < 1800, self.upgrades)

            # if not self.profile.wait_for_most_profit_upgrades:
            #     available_upgrades = filter(
            #         lambda u: self.get_spending_balance() > u.price and u.cooldown_seconds == 0,
            #         available_upgrades)


            available_upgrades = sorted(available_upgrades, key=lambda u: self.upgrade_calculate_significance(u),
                                        reverse=False)

            if len(available_upgrades) == 0:
                logger.info(f"[{self.profile.name}] No available upgrades")
                break

            most_profit_upgrade: Upgrade = available_upgrades[0]

            if most_profit_upgrade.price > self.get_spending_balance(most_profit_upgrade):
                logger.info(f"[{self.profile.name}] Not enough money for upgrade <e>{most_profit_upgrade.name}</e>")
                self.update_preferred_sleep(
                    delay=(most_profit_upgrade.price - self.get_spending_balance()) / self.user.earn_per_sec,
                    sleep_reason=SleepReason.WAIT_UPGRADE_MONEY
                )
                break

            if most_profit_upgrade.cooldown_seconds > 0:
                logger.info(f"[{self.profile.name}] Upgrade <e>{most_profit_upgrade.name}</e> on cooldown for <y>{most_profit_upgrade.cooldown_seconds}s</y>")
                self.update_preferred_sleep(
                    delay=most_profit_upgrade.cooldown_seconds,
                    sleep_reason=SleepReason.WAIT_UPGRADE_COOLDOWN
                )
                break

            await self.do_upgrade(upgrade=most_profit_upgrade)

    async def do_upgrade(self, upgrade: Upgrade):
        sleep_time = randint(self.profile.sleep_interval_before_upgrade[0], self.profile.sleep_interval_before_upgrade[1])
        logger.info(f"[{self.profile.name}] Sleep {sleep_time}s before upgrade <e>{upgrade.name}</e>")
        await self.sleep(delay=sleep_time)

        self.user, self.upgrades, self.daily_combo = await self.web_client.buy_upgrade(upgrade_id=upgrade.id)

        logger.success(
            f"[{self.profile.name}] "
            f"Successfully upgraded <e>{upgrade.name}</e> to <m>{upgrade.level}</m> lvl | "
            f"Earn every hour: <y>{self.user.earn_per_hour}</y> (<g>+{upgrade.earn_per_hour}</g>)")

    async def apply_energy_boost(self) -> bool:
        energy_boost = next((boost for boost in self.boosts if boost.id == 'BoostFullAvailableTaps'), {})
        if energy_boost.cooldown_seconds != 0 or energy_boost.level > energy_boost.max_level:
            return False

        user = await self.web_client.apply_boost(boost_id="BoostFullAvailableTaps")

        self.user = user
        logger.success(f"[{self.profile.name}] Successfully apply energy boost")
        return True

    async def make_taps(self) -> bool:
        available_taps = int(float(self.user.available_energy) / self.user.earn_per_tap)
        if available_taps < self.user.earn_per_tap:
            logger.info(f"[{self.profile.name}] Not enough taps: {available_taps}/{self.user.earn_per_tap}")
            return True

        max_taps = int(float(self.user.max_energy) / self.user.earn_per_tap)
        taps_to_start = max_taps * self.profile.min_taps_for_clicker_in_percent / 100
        if available_taps < taps_to_start:
            logger.info(f"[{self.profile.name}] Not enough taps for launch clicker: {available_taps}/{taps_to_start}")
            return True

        current_energy = min(self.user.available_energy, self.user.max_energy)
        random_simulated_taps_percent = randint(1, 4) / 100
        # add 1-4% taps like official app when you're clicking by yourself
        simulated_taps = available_taps + int(available_taps * random_simulated_taps_percent)

        # sleep before taps like you do it in real like 6 taps per second
        sleep_time = int(available_taps / 6)
        logger.info(f"[{self.profile.name}] Sleep {sleep_time}s before taps")
        await self.sleep(delay=sleep_time)

        user = await self.web_client.send_taps(available_energy=current_energy, taps=simulated_taps)

        new_balance = int(user.balance)
        calc_taps = new_balance - self.user.balance

        self.user = user

        logger.success(f"[{self.profile.name}] Successful tapped <c>{simulated_taps}</c> times! | "
                       f"Balance: <c>{self.user.balance}</c> (<g>+{calc_taps}</g>)")
        return True

    async def sleep(self, delay: int):
        await asyncio.sleep(delay=float(delay))
        self.user.available_energy = min(self.user.available_energy + self.user.energy_recover_per_sec * delay,
                                            self.user.max_energy)
        self.user.balance += self.user.earn_per_sec * delay

    async def run(self) -> None:
        while True:
            try:
                # Sequence of requests in the client
                #     - me-telegram
                #     - config
                #     - sync
                #     - upgrades-for-buy
                #     - boosts-for-buy
                #     - list-tasks
                await self.web_client.get_me_telegram()
                self.daily_cipher, self.minigame  = await self.parse_config()

                await self.check_playground(Playground.getConfigJson())

                self.user = await self.earn_money()

                #Print info
                logger.info(f"[<r>{self.profile.name}</r>] [id: <c>{self.user.id}</c>] [balance: <c>{int(self.user.balance)}</c>] [profit: <c>{int(self.user.earn_per_hour)}</c>] [referrals: <c>{self.user.referrals_count}</c>] [keys: <c>{self.user.totalKeys}</c>]")

                self.upgrades, self.daily_combo = await self.web_client.get_upgrades()
                self.boosts = await self.web_client.get_boosts()
                self.tasks = await self.web_client.get_tasks()

                # DAILY CIPHER                
                await self.check_daily_cipher()

                # TASKS COMPLETING
                for task in self.tasks:
                    if task.is_completed is False:
                        if task.id == "invite_friends" and self.user.referrals_count == 0 :
                            continue
                        status = await self.web_client.check_task(task_id=task.id)
                        if status is False:
                            continue

                        self.user.balance += task.reward_coins
                        if task.id == "streak_days":
                            logger.success(f"[{self.profile.name}] Successfully get daily reward | "
                                           f"Days: <m>{task.days}</m> | "
                                           f"Balance: <c>{self.user.balance}</c> (<g>+{task.reward_coins}</g>)")
                        else:
                            logger.success(f"[{self.profile.name}] Successfully get reward for task <m>{task.id}</m> | "
                                           f"Balance: <c>{self.user.balance}</c> (<g>+{task.reward_coins}</g>)")

                # TAPPING
                if self.profile.auto_clicker is True:
                    await self.make_taps()

                    # APPLY ENERGY BOOST
                    if self.profile.apply_daily_energy is True and time() - self.user.last_energy_boost_time >= 3600:
                        logger.info(f"[{self.profile.name}] Sleep 5s before checking energy boost")
                        await self.sleep(delay=5)
                        if await self.apply_energy_boost():
                            await self.make_taps()

                    self.update_preferred_sleep(
                        delay=(
                                          self.user.max_energy - self.user.available_energy) / self.user.energy_recover_per_sec,
                        sleep_reason=SleepReason.WAIT_ENERGY_RECOVER
                    )

                # UPGRADES
                if self.profile.auto_upgrade is True:
                    await self.make_upgrades()
                                    
                # DAILY MINIGAME   
                await self.check_minigame()

                # SLEEP
                if self.preferred_sleep is not None:
                    sleep_time = max(self.preferred_sleep.delay - (time() - self.preferred_sleep.created_time), 40)
                    if self.preferred_sleep.sleep_reason == SleepReason.WAIT_UPGRADE_MONEY:
                        logger.info(f"[{self.profile.name}] Sleep {sleep_time}s for earn money for upgrades")
                    elif self.preferred_sleep.sleep_reason == SleepReason.WAIT_UPGRADE_COOLDOWN:
                        logger.info(f"[{self.profile.name}] Sleep {sleep_time}s for waiting cooldown for upgrades")
                    elif self.preferred_sleep.sleep_reason == SleepReason.WAIT_ENERGY_RECOVER:
                        logger.info(f"[{self.profile.name}] Sleep {sleep_time}s for recover full energy")

                    self.preferred_sleep = None
                    await self.sleep(delay=sleep_time)
                else:
                    logger.info(f"[{self.profile.name}] Sleep 3600s before next iteration")
                    await self.sleep(delay=3600)

            except InvalidSession as error:
                raise error
            except aiohttp.ClientResponseError as error:
                logger.error(f"[{self.profile.name}] Client response error: {error}")
                logger.info(f"[{self.profile.name}] Sleep 3600s before next iteration because of error")
                await self.sleep(delay=3600)
            except Exception as error:
                logger.error(f"[{self.profile.name}] Unknown error: {error}")
                traceback.print_exc()
                await self.sleep(delay=30)

async def run_tapper(profile: Profile, proxy: str | None):
    
    logger.info(f"[{profile.name}] [{'<g>proxy</g>' if proxy else '<r>no proxy</r>' }] successfully added to task list")
    
    try:
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        async with aiohttp.ClientSession(headers=Headers(), connector=proxy_conn) as http_client:
            web_client = WebClient(http_client=http_client, profile=profile)
            await Tapper(web_client=web_client).run()
    except InvalidSession:
        logger.error(f"[{profile.name}] Invalid Session")
