import aiohttp
import asyncio
from datetime import datetime

BOT_TOKEN = "6374582132:AAEMjw8CO2YRLNvEAl0VSzZ9AXTvaU9u96A"
CHAT_ID = "-823196726"
LINK_URL = "https://kaconkalus.site/checker/Link.txt"

async def check_nawala_domain(session, url):
    try:
        async with session.get(url) as response:
            if any(text in await response.text() for text in ["This site can’t be reached", "Situs ini tidak dapat dijangkau", "SITUS DIBLOKIR"]):
                return True
            else:
                return False
    except aiohttp.ClientError:
        return True

async def send_telegram_message(session, message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    async with session.post(url, data=data) as response:
        return await response.json()

async def main():
    output_file = "Nawala.txt"
    interval_minutes = 15  # Interval waktu dalam menit

    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(LINK_URL) as response:
                    domain_list = (await response.text()).splitlines()
            except aiohttp.ClientError:
                print("Gagal mendapatkan daftar domain dari URL.")
                domain_list = []

            nawala_domains = []

            tasks = []
            for domain in domain_list:
                domain = domain.strip()
                if domain.startswith("http://") or domain.startswith("https://"):
                    url = domain
                else:
                    url = "https://" + domain

                tasks.append(check_nawala_domain(session, url))

            results = await asyncio.gather(*tasks)

            for domain, result in zip(domain_list, results):
                if result:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    nawala_domains.append(f"{domain} | {timestamp}")

            if nawala_domains:
                message = "\n".join(nawala_domains)
                await send_telegram_message(session, message)

            with open(output_file, "a") as nawala_file:
                nawala_file.write("==================================\n")
                nawala_file.write("----------------------------------\n\n")

                for domain in nawala_domains:
                    nawala_file.write(f"{domain}\n")

                nawala_file.write("\n==================================\n")

            print("Pengecekan Selesai! Domain terkena nawala telah disimpan dan pesan telah dikirim.")

            await asyncio.sleep(interval_minutes * 60)

if __name__ == "__main__":
    asyncio.run(main())
