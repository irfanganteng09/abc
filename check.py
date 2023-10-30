from datetime import datetime
import aiohttp
import asyncio
import hashlib
import time
import os

class NawalaChecker:
    def __init__(self):
        self.PANEL_URL = os.environ.get("PANEL_URL", "https://greyhal.com")
        self.PANEL_SALT = os.environ.get("PANEL_SALT", "dskvjmf39svcm")
        self.CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 60 * 5))

    def generate_salt(self):
        date = datetime.now().strftime("%Y%m%d")
        return hashlib.md5(f"{date}{self.PANEL_SALT}".encode('utf-8')).hexdigest()

    async def send_to_panel(self, domain, remark):
        url = f"{self.PANEL_URL}/api-checker/deactivate-url"
        salt = self.generate_salt()
        data = {"salt": salt, "domain": domain, "remark": remark}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as response:
                response_data = await response.json()
                return response_data

    async def check_url(self, session, url):
        try:
            async with session.get(url, allow_redirects=True) as response:
                result = await response.text()
                nawala_params = ["This site can’t be reached", "Situs ini tidak dapat dijangkau", "SITUS DIBLOKIR", "trustpositif"]
                if any(text in result for text in nawala_params):
                    raise ValueError("Nawala")
                # if url not in str(response.url):
                #     raise ValueError(f"Redirected to: {response.url}")
        except aiohttp.ClientConnectionError as e:
            error_msg = f"Client Error: {url}\n{str(e)}\n"
            print(error_msg)
        except Exception as e:
            error_msg = f"Nawala Error: {url}\n{str(e)}\n"
            print(error_msg)
            await self.send_to_panel(url, str(e))

    async def run_check(self):
        while True:
            try:
                print("Start checking...")
                start_time = time.time()
                get_list_domain = f"{self.PANEL_URL}/api-checker/get-list-url"
                salt = self.generate_salt()
                data = {"salt": salt}
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(get_list_domain, data=data) as response:
                        data = await response.json()
                        domain_list = data.get('data')
                    
                    tasks = [self.check_url(session, url) for url in domain_list]
                    await asyncio.gather(*tasks)
                
                execution_time = time.time() - start_time
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Finished in : {execution_time:.2f} seconds | {date}")
                await asyncio.sleep(self.CHECK_INTERVAL)
            except Exception as e:
                print(f"Application crashed: {e}")
                print("Restarting in 10 seconds...")
                await asyncio.sleep(10)

async def main():
    while True:
        try:
            nawala_checker = NawalaChecker()
            await nawala_checker.run_check()
        except Exception as e:
            pass

if __name__ == "__main__":
    asyncio.run(main())
