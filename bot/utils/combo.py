from pydantic import BaseModel, model_validator
from json import dump
from time import time
from bot.config import settings
from bot.utils import logger

import aiohttp

class Combo(BaseModel, validate_assignment=True):

    combo: list[str] = None
    expired: int = 0

    @model_validator(mode='after')
    def save_combo(self, info):
        
        if info.context and ('rewrite', False) in info.context.items():
            return self
        
        with open(settings.ROOT_PATH.joinpath("daily_combo.json"), 'w', encoding='utf-8') as file:
            dump(self.model_dump(), file, ensure_ascii=False, indent=4)

        return self 

    async def update(self):      
        try:
            async with aiohttp.ClientSession() as http_client:
                response = await http_client.get(settings.DAILY_JSON_URL)
                response_json = await response.json()
                
                if (expired := response_json.get('expired')) < time():
                    return False

                self.combo = response_json.get('combo')
                self.expired = expired           

                # if self.expired < int(time()):
                #     return False
                
        except aiohttp.ClientConnectorError as error:
            logger.error(f"Error while get new combo file: {error}")
            return None
        
        return True

combo = Combo.model_validate_json(json_data = settings.ROOT_PATH.joinpath("daily_combo.json").read_text(), context = {'rewrite': False})