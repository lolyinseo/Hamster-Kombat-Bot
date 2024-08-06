from typing_extensions import Optional
from pydantic import BaseModel, model_validator
from json import dump
from pathlib import Path

from bot.config import settings

class Profile(BaseModel, validate_assignment=True):
    name: str
    
    id: Optional[int] = None
    token: Optional[str] = None
    session: Optional[str] = None
    
    wallet: Optional[str] = None
    mnemonic: Optional[str] = None

    wait_for_most_profit_upgrades : bool = settings.WAIT_FOR_MOST_PROFIT_UPGRADES 
    auto_upgrade: bool = settings.AUTO_UPGRADE 
    auto_clicker: bool = settings.AUTO_CLICKER 
    apply_daily_energy: bool = settings.APPLY_DAILY_ENERGY 

    min_balance: int = settings.MIN_BALANCE 
    min_taps_for_clicker_in_percent: int = settings.MIN_TAPS_FOR_CLICKER_IN_PERCENT 
    sleep_interval_before_upgrade: list[int] = settings.SLEEP_INTERVAL_BEFORE_UPGRADE 

    balance_strategy: int = settings.BALANCE_STRATEGY

    user_agent: str = 'Mozilla/5.0 (Linux; Android 13; SM-A135N Build/TP1A.220624.014; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6422.165 Mobile Safari/537.36'
    sec_ch_ua: str = '"Android WebView";v="125", "Chromium";v="125", "Not?A_Brand";v="33"'

    proxy: Optional[str] = None

    @model_validator(mode='after')
    def save_settings(self, info):
        
        if info.context and ('rewrite', False) in info.context.items():
            return self
        
        with open(Path.joinpath(settings.PROFILE_DIR, f"{self.name}.json"), 'w', encoding='utf-8') as file:
            dump(self.model_dump(), file, ensure_ascii=False, indent=4)

        return self
    
    @staticmethod
    def load(name: str):

        profile_file= settings.PROFILE_DIR.joinpath(f"{name}.json") 

        if not profile_file.exists():
            raise FileNotFoundError(f"Not found profile with name {name}")

        return Profile.model_validate_json(json_data = settings.PROFILE_DIR.joinpath(profile_file).read_text(),
                                            context = {'rewrite': False})