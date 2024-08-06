from pydantic import field_validator, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from os import makedirs
from pathlib import Path
from bot.utils import logger

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)
    
    API_ID: int | None = None
    API_HASH: str | None = None

    ROOT_PATH: Path = Path(__file__).parents[2]
    PROFILE_DIR: Path = ROOT_PATH.joinpath('profiles')
    USE_PROXY_FROM_FILE: Path | None = None
    
    ENCRYPT_KEY: str

    WAIT_FOR_MOST_PROFIT_UPGRADES: bool = True

    AUTO_UPGRADE: bool = True

    AUTO_CLICKER: bool = True

    APPLY_DAILY_ENERGY: bool = True

    UPGRADE_DAILY_COMBO: bool = True

    MIN_BALANCE: int = 1_000_000

    MIN_TAPS_FOR_CLICKER_IN_PERCENT: int = 80

    SLEEP_INTERVAL_BEFORE_UPGRADE: list[int] = [7, 30]

    BALANCE_STRATEGY: int = 10

    MAX_SLEEP_TIME: int = 10800

    DAILY_JSON_URL: str = "https://lolyinseo.github.io/HamsterKombatBot/daily_combo.json"
    
    GAMES_JSON_URL: str = "https://lolyinseo.github.io/HamsterKombatBot/games.json"

    FINGERPRINT_URL: str = "https://dev.hmstr.co.in/fingerprint"

    USERAGENT_URL: str = "https://dev.hmstr.co.in/useragent"

    SERVER_SECRET: str = "RUoK!pusp6ThEdURUtRenOwUhAsWUCLheBazl!uJLPlS8EbreWLdrupIwabRAsiBu"

    CERT_FILE: Path | None = None

    @field_validator('PROFILE_DIR', mode='after')
    def profile_dir(field):
        # Make PROFILE_DIR if not exist
        try:
            makedirs(field, exist_ok=True)
        except Exception as error:
            logger.error('Unknown error while makedirs PROFILE_DIR')
            raise
        
        return field
    
    @field_validator('USE_PROXY_FROM_FILE','CERT_FILE', mode='before')
    def validate_path(path):
        
        if path:
            path = Path(path)
            if not path.exists():

                logger.error(f'Proxy file {path.resolve()} not found')
                raise FileNotFoundError
        
        return path


settings = Settings()
