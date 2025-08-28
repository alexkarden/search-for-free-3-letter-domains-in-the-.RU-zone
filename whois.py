import asyncio
import logging

import aiosqlite
import requests


DATABASE_NAME = "base.db"
LETTERS = "abcdefghijklmnopqrstuvwxyz0123456789"
SLEEP_BETWEEN = 6  # секунд между проверками


async def init_db():
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Создание таблицы domains, если она еще не существует
            await db.execute(
                ""
                "CREATE TABLE IF NOT EXISTS domains ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "domain TEXT)"
                ""
            )
            await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")


async def add_new_domain(domain):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            await db.execute("" "INSERT INTO domains (domain) VALUES (?)", (domain,))
            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")


def check_domain(domain: str) -> None:
    api = f"http://whoisapi.netfox.ru/api_v1/?domain={domain}"
    try:
        resp = requests.get(api, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"{domain} - Ошибка запроса WHOIS API: {e}")
        return None

    if resp.text == "1":
        return True
    else:
        return False


async def main():
    print("Собираем данные о доменах")
    await init_db()
    for let1 in LETTERS:
        for let2 in (
            "-" + LETTERS
        ):  # тире не может быть в домене в начале или в конце - только посеридине
            for let3 in LETTERS:
                name = f"{let1}{let2}{let3}.ru"
                await asyncio.sleep(SLEEP_BETWEEN)
                print(f"\r{name}", end="", flush=True)
                result = await check_domain(name)
                if result is False:
                    logging.info(f"{name} - Возможно свободен")
                    await add_new_domain(name)
                elif result is None:
                    logging.info(f"{name} - Ошибка - стоит перепроверить")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.ERROR,
        filename="logfile.log",
        filemode="w",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error("Exit")
