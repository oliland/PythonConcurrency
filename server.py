from flask import Flask
import asyncio
import aiohttp
import time
from typing import List


DELAY_URLS = [
    "http://httpbin.org/delay/5",
    "http://httpbin.org/delay/3",
]


app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Looking to get <a href="/delay-me">delayed</a>?</h1>'

@app.route('/delay-me')
def get_delays():
    start = time.time()
    asyncio.run(main(DELAY_URLS))
    end = time.time()
    delay = round(end - start, 3)
    return f"Your day has been delayed by {delay} seconds!"


async def get(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url) as response:
            await response.read()


async def main(urls: List[str]):
    await asyncio.gather(*[get(url) for url in urls])


if __name__ == '__main__':
    app.run()
