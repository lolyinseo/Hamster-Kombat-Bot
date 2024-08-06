from enum import StrEnum

class Requests(StrEnum):
    CONFIG = "https://api.hamsterkombatgame.io/clicker/config"
    ME_TELEGRAM = "https://api.hamsterkombatgame.io/auth/me-telegram"
    TAP = "https://api.hamsterkombatgame.io/clicker/tap"
    BOOSTS_FOR_BUY = "https://api.hamsterkombatgame.io/clicker/boosts-for-buy"
    BUY_UPGRADE = "https://api.hamsterkombatgame.io/clicker/buy-upgrade"
    UPGRADES_FOR_BUY = "https://api.hamsterkombatgame.io/clicker/upgrades-for-buy"
    BUY_BOOST = "https://api.hamsterkombatgame.io/clicker/buy-boost"
    CHECK_TASK = "https://api.hamsterkombatgame.io/clicker/check-task"
    SELECT_EXCHANGE = "https://api.hamsterkombatgame.io/clicker/select-exchange"
    LIST_TASKS = "https://api.hamsterkombatgame.io/clicker/list-tasks"
    SYNC = "https://api.hamsterkombatgame.io/clicker/sync"
    CLAIM_DAILY_CIPHER = "https://api.hamsterkombatgame.io/clicker/claim-daily-cipher"
    CLAIM_DAILY_COMBO = "https://api.hamsterkombatgame.io/clicker/claim-daily-combo"
    REFERRAL_STAT = "https://api.hamsterkombatgame.io/clicker/referral-stat"
    LIST_AIRDROP_TASKS = "https://api.hamsterkombatgame.io/clicker/list-airdrop-tasks"
    CHECK_AIRDROP_TASK = "https://api.hamsterkombatgame.io/clicker/check-airdrop-task"
    WEBAPP_AUTH = "https://api.hamsterkombatgame.io/auth/auth-by-telegram-webapp"
    ADD_REFERAL = "https://api.hamsterkombatgame.io/clicker/add-referral"
    DELETE_WALLET = "https://api.hamsterkombatgame.io/clicker/delete-wallet"
    START_MINIGAME = "https://api.hamsterkombatgame.io/clicker/start-keys-minigame"
    CLAIM_MINIGAME = "https://api.hamsterkombatgame.io/clicker/claim-daily-keys-minigame"
    GET_PROMOS = "https://api.hamsterkombatgame.io/clicker/get-promos"
    APPLY_PROMO = "https://api.hamsterkombatgame.io/clicker/apply-promo"
    
