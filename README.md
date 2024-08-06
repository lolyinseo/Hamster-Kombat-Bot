![img1](.github/images/demo.png)

> 🇪🇳 README in english available [here](README-EN.md)

## Функционал  
| Функционал                                                     | Поддерживается  |
|----------------------------------------------------------------|:---------------:|
| Многопоточность                                                |        ✅        |
| Привязка прокси к сессии                                       |        ✅        |
| Авто-покупка предметов при наличии монет (tap, energy, charge) |        ✅        |
| Поддержка tdata / pyrogram .session / telethon .session        |        ✅        |


## [Настройки](https://github.com/shamhi/HamsterKombatBot/blob/main/.env-example)
| Настройка                             | Описание                                                                                                  |
|---------------------------------------|-----------------------------------------------------------------------------------------------------------|
| **API_ID / API_HASH**                 | Данные платформы, с которой запускать сессию Telegram _(сток - Android)_                                  |
| **AUTO_UPGRADE**                      | Улучшать ли пассивный заработок _(True / False)_                                                          |
| **AUTO_CLICKER**                      | Включить автоматический кликер _(True / False)_                                                           |
| **WAIT_FOR_MOST_PROFIT_UPGRADES**     | Копить деньги на самый выгодный апгрейд                                                                   |
| **APPLY_DAILY_ENERGY**                | Использовать ли ежедневный бесплатный буст энергии _(True / False)_                                       |
| **MIN_BALANCE**                       | Минимальный баланс, который нужно оставлять не тронутым                                                   |
| **MIN_TAPS_FOR_CLICKER_IN_PERCENT**   | Минимальный процент тапов (от доступного кол-ва) при котором кликер будет запускаться. По умолчанию 60%   |
| **SLEEP_INTERVAL_BEFORE_UPGRADE**     | Задержка перед каждым апгрейдом. Задается диапазон. По умолчанию [10, 40]                                 |
| **USE_PROXY_FROM_FILE**               | Использовать-ли прокси из файла `bot/config/proxies.txt` _(True / False)_                                 |

## Быстрый старт 📚
1. Чтобы установить библиотеки в Windows, запустите INSTALL.bat.
2. Для запуска бота используйте `START.bat` (или в консоли: `python main.py`).

## Предварительные условия
Прежде чем начать, убедитесь, что у вас установлено следующее:
- [Python](https://www.python.org/downloads/) версии 3.11.

## [Получение токена на Android устройстве](docs/android-auth-info-extraction-guide.md)

## Получение API ключей
1. Перейдите на сайт [my.telegram.org](https://my.telegram.org) и войдите в систему, используя свой номер телефона.
2. Выберите **"API development tools"** и заполните форму для регистрации нового приложения.
3. Запишите `API_ID` и `API_HASH` в файле `.env`, предоставленные после регистрации вашего приложения.

## Установка
Вы можете скачать [**Репозиторий**](https://github.com/shamhi/HamsterKombatBot) клонированием на вашу систему и установкой необходимых зависимостей:
```shell
~ >>> git clone https://github.com/shamhi/HamsterKombatBot.git 
~ >>> cd HamsterKombatBot

# Linux
~/HamsterKombatBot >>> python3 -m venv venv
~/HamsterKombatBot >>> source venv/bin/activate
~/HamsterKombatBot >>> pip3 install -r requirements.txt
~/HamsterKombatBot >>> cp .env-example .env
~/HamsterKombatBot >>> nano .env  # Здесь вы обязательно должны указать ваши API_ID и API_HASH , остальное берется по умолчанию
~/HamsterKombatBot >>> python3 main.py

# Windows
~/HamsterKombatBot >>> python -m venv venv
~/HamsterKombatBot >>> venv\Scripts\activate
~/HamsterKombatBot >>> pip install -r requirements.txt
~/HamsterKombatBot >>> copy .env-example .env
~/HamsterKombatBot >>> # Указываете ваши API_ID и API_HASH, остальное берется по умолчанию
~/HamsterKombatBot >>> python main.py
```

Также для быстрого запуска вы можете использовать аргументы, например:
```shell
~/HamsterKombatBot >>> python3 main.py --action (1/2)
# Или
~/HamsterKombatBot >>> python3 main.py -a (1/2)

# 1 - Создает сессию
# 2 - Запускает кликер
```
