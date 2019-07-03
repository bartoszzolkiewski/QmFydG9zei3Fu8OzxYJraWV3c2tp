import asyncio
import time
from collections import defaultdict
from time import sleep

import requests
from sanic.log import logger


class Url:
    URL_DICT = {}
    LAST_ID = 1

    FIELDS = set(['id', 'url', 'interval'])

    def __init__(self, url, interval):
        self.url = url
        self.interval = interval

        self.id = Url.LAST_ID
        Url.LAST_ID += 1

        Url.URL_DICT[self.id] = self

        loop = asyncio.get_event_loop()
        loop.create_task(self.retrieve())

    def update(self, url, interval):
        self.url = url
        self.interval = interval

        Url.URL_DICT[self.id] = self

    def as_dict(self, fields = FIELDS):
        fields = set(fields)

        if fields and fields.issubset(Url.FIELDS):
            return {x: y for (x, y) in self.__dict__.items() if x in fields}
        else:
            raise ValueError

    async def retrieve(self, timeout = 5):
        try:
            logger.info("Pobieranie z url %s" % self.url)
            response = requests.get(self.url, timeout = timeout)
            response_time = response.elapsed.total_seconds()

        except requests.exceptions.Timeout:
            logger.error("Timeout dla url %s" % self.url)
            response = None
            response_time = timeout
        
        except Exception as e:
            logger.error("Error %s" % e)
            response = None
            response_time = timeout

        if response:
            logger.info("Zwrotka z url %s: %s" % (self.url, response.text[:15]))
            History.add_for_url(self, response.text, response_time)
        
        obj = Url.URL_DICT.get(self.id, None)
        if obj:
            # jeśli del, zatrzyma wykonywanie
            await asyncio.sleep(timeout)

            loop = asyncio.get_event_loop()
            loop.create_task(obj.retrieve(timeout = obj.interval))

    def remove(self):
        History.del_for_url(self)
        del Url.URL_DICT[self.id]

    @classmethod
    def get_by_id(cls, id):
        return Url.URL_DICT.get(id, None)

    @classmethod
    def get_all(cls):
        return Url.URL_DICT.values()

class History(object):
    HISTORY_DICT = defaultdict(list)
    
    FIELDS = set(['response', 'duration', 'created_at'])

    def __init__(self, response, duration):
        self.response = response
        self.duration = duration
        self.created_at = time.time()

    def as_dict(self, fields = FIELDS):
        fields = set(fields)

        if fields and fields.issubset(History.FIELDS):
            return {x: y for (x, y) in self.__dict__.items() if x in fields}
        else:
            raise ValueError

    @classmethod
    def add_for_url(cls, url, response, duration):
        obj = History(response, duration)
        History.HISTORY_DICT[url.id].append(obj)

    @classmethod
    def del_for_url(cls, url):
        del History.HISTORY_DICT[url.id]

    @classmethod
    def get_for_url(cls, url):
        history_dict_list = []
        for h in History.HISTORY_DICT[url.id]:
            history_dict_list.append(h.as_dict())

        return history_dict_list