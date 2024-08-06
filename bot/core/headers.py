# pylint: disable=C0301
import json as json_parser

def Headers(additional = {}) -> dict:
    default =    {
        'Accept-Language': 'ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Host': 'api.hamsterkombatgame.io',
        'Origin': 'https://hamsterkombatgame.io',
        'Referer': 'https://hamsterkombatgame.io/',
        'X-Requested-With': 'org.telegram.messenger',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua': '"Android WebView";v="125", "Chromium";v="125", "Not?A_Brand";v="33"',	
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'Accept': 'application/json',
    }

    default.update(additional)
    
    return default

additional_headers_for_empty_requests = {
    'Accept': '*/*',
    'Content-Length': "0",
}


def create_headers(json: dict | None) -> dict:
    if json is None:
        return additional_headers_for_empty_requests
    return {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Content-Length': str(len(json_parser.dumps(json).encode('utf-8'))),
    }
