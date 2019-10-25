import random
import typing
from time import sleep
from walrus import Message

import botcannon


class CollectorDemo(botcannon.Collector):
    """
    Collectors need the 2 method definitions below with similar behavior.

    an instance of the collector will be created and remain active until the process exits.

    read needs to be a generator and should yield

    taskback is called as the last action after a successful validate AND each task is sucessful.
    taskback is optional and allows tasks to call process resources (connections, hardware, etc)
    """
    def __init__(self, room_temp, room_light):
        self.s = 0.5
        self.d = {'temp': room_temp, 'light': room_light}

    def read(self) -> typing.Generator[dict, None, None]:
        """Yields dicts to validate via workers"""

        sleep(float(self.s))
        yield {self.d['temp']: random.randint(600, 700),
               self.d['temp']: random.randint(1000, 1023)}


    def taskback(self, message: Message) -> None:
        """
        :param message: Message from worker
        :return:
        """
        print(f'taskback call: {message.data}')

