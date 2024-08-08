
```                           _                                _           _     ___       _   
  /\  /\__ _ _ __ ___  ___| |_ ___ _ __ /\ /\___  _ __ ___ | |__   __ _| |_  / __\ ___ | |_ 
 / /_/ / _` | '_ ` _ \/ __| __/ _ \ '__/ //_/ _ \| '_ ` _ \| '_ \ / _` | __|/__\/// _ \| __|
/ __  / (_| | | | | | \__ \ ||  __/ | / __ \ (_) | | | | | | |_) | (_| | |_/ \/  \ (_) | |_ 
\/ /_/ \__,_|_| |_| |_|___/\__\___|_| \/  \/\___/|_| |_| |_|_.__/ \__,_|\__\_____/\___/ \__|
```                                                                                            

> 🇪🇳 README in english available [here](README-EN.md)

![bot_log_screen](https://github.com/user-attachments/assets/252329d2-9c9a-465c-b346-459e07057b5f)

## Функционал  
| Функционал                                                     | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅        |
| Привязка прокси к профилю                                      |        ✅        |
| Авто-покупка предметов при наличии монет (tap, energy, charge) |        ✅        |
| Поддержка tdata / pyrogram .session / telethon .session        |        ✅        |
| Сбор ключей                                                    |        ✅        |
| Регистрация рефералов                                          |        ✅        |


## [Настройки](https://github.com/lolyinseo/HamsterKombatBot/blob/main/.env)
| Настройка                             | Описание                                                                                                  |
|---------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **API_ID / API_HASH**                 | Данные платформы, с которой запускать сессию Pyrogram _(сток - Android)_                                  |
| **AUTO_UPGRADE**                      | Улучшать ли пассивный заработок _(True / False)_                                                          |
| **AUTO_CLICKER**                      | Включить автоматический кликер _(True / False)_                                                           |
| **WAIT_FOR_MOST_PROFIT_UPGRADES**     | Копить деньги на самый выгодный апгрейд                                                                   |
| **APPLY_DAILY_ENERGY**                | Использовать ли ежедневный бесплатный буст энергии _(True / False)_                                       |
| **MAX_SLEEP_TIME**                    | Максимальное время сна в сек, лучше ставить не более 3ч _(10800)_                                         |
| **MIN_BALANCE**                       | Минимальный баланс, который нужно оставлять не тронутым _(1000000)_                                       |
| **BALANCE_STRATEGY**                  | Множитель стратегии **Профит в час * X = Баланс**  _(10)_                                                 |
| **MIN_TAPS_FOR_CLICKER_IN_PERCENT**   | Минимальный процент тапов (от доступного кол-ва) при котором кликер будет запускаться. По умолчанию 80%   |
| **SLEEP_INTERVAL_BEFORE_UPGRADE**     | Задержка перед каждым апгрейдом. Задается диапазон. По умолчанию [10, 40]                                 |
| **USE_PROXY_FROM_FILE**               | Использовать-ли прокси из указанного файла. Например `./proxies.txt`                                      |

## [Профили](https://github.com/lolyinseo/HamsterKombatBot/blob/main/profiles/example.json)
Профили генерируются автоматически, если вы используете авторизацию через бота. Вы можете создавать профили вручную, если у вас уже есть authToken [read more](docs/android-auth-info-extraction-guide_en.md). Пример профиля ./profiles/example.json. Для запуска профиля нужно минимум заполнить name(имя профиля, любое), id(ваш telegram id), и token(authToken игры) .

## Быстрый старт 📚
1. Чтобы установить библиотеки в Windows, запустите INSTALL.bat.
2. Для запуска бота используйте `START.bat` (или в консоли: `python main.py`).

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) версии 3.12.

## [Получение токена authToken на Android](docs/android-auth-info-extraction-guide.md)

## Получение API ключей (не обязательно, если у вас уже есть authToken)
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/lolyinseo/HamsterKombatBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
~ >>> git clone https://github.com/lolyinseo/HamsterKombatBot.git 
~ >>> cd HamsterKombatBot

# Linux
~/HamsterKombatBot >>> python3 -m venv hamsterbot
~/HamsterKombatBot >>> source hamsterbot/bin/activate
~/HamsterKombatBot >>> pip3 install -r requirements.txt
~/HamsterKombatBot >>> nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH, другие парвметры или остальное берется по умолчанию
~/HamsterKombatBot >>> python3 main.py

# Windows
~/HamsterKombatBot >>> python -m venv venv
~/HamsterKombatBot >>> venv\Scripts\activate
~/HamsterKombatBot >>> pip install -r requirements.txt
~/HamsterKombatBot >>> # Указываете ваши API_ID и API_HASH, другие парвметры или остальное берется по умолчанию
~/HamsterKombatBot >>> python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/HamsterKombatBot >>> python3 main.py --action (1/2)
# Или
~/HamsterKombatBot >>> python3 main.py -a (1/2)

# 1 - Регистрация новой сессии
# 2 - Запускает кликер
```
