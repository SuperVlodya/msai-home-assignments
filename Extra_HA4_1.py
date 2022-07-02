import asyncio
import aiohttp
from extra_ha_4_1_config import Config
import time
import random
import nest_asyncio
nest_asyncio.apply()


async def execute(req, session):
    body = req['body'] if req['body'] != 'None' else None
    return await session.request(req['method'], req['url'], headers=req['headers'], data=body)

async def request(req):
    url = req['url']
    for stage in Config().stages:
        for rep in range(int(stage['repeats'])):
            number = 0
            success = 0
            errors = 0
            start = time.time()
            duration = stage['duration']
            finish = start + duration
            rps_from = stage['rps_from']
            rps_to = stage['rps_to']
            if rps_from > rps_to:
                rps_from = stage['rps_to']
                rps_to = stage['rps_from']
            while time.time() < finish:
                count_rate = random.randint(rps_from, rps_to)
                number += count_rate
                async with aiohttp.ClientSession(loop=loop) as session:
                    futures = [execute(req, session) for _ in range(count_rate)]
                    responses = await asyncio.gather(*futures)
                    for r in responses:
                        if 200 <= r.status <= 299:
                            success += 1
                        else:
                            errors += 1
                if (finish - time.time()) > 0:
                    delay = random.randint(0, (finish - time.time()) // 2)
                    duration -= delay
                    await asyncio.sleep(delay)
        print(f'''
            {number} of requests sent to {url};
            {success / number * 100}% of requests are successful;
            {errors / number * 100}% of errors;
            Average query duration is {duration / number} seconds.
            '''
        )
        await asyncio.sleep(stage['timeout'])


async def tasks():
    start = time.time()
    tasks = []
    for i in Config().requests:
        tasks.append(asyncio.ensure_future(request(i)))

    await asyncio.wait(tasks)
    print("Process took: {:.2f} seconds".format(time.time() - start))


loop = asyncio.get_event_loop()
result = loop.run_until_complete(tasks())
loop.close()



