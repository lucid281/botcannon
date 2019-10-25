from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants

from walrus import Message

from botcannon.models import Collector


class AnalogIn:
    def __init__(self, board, pin_id, constant):
        self.pin_id = None
        self.value = None
        board.set_pin_mode(pin_id, constant, self.callback)

    def callback(self, data):
        """
        :param data: data[0] contains the pin number, data[1] contains the data value
        :return:
        """
        self.pin_id = data[0]
        self.value = data[1]


class DigitalOut:
    def __init__(self, board, pin_id):
        self.pin = pin_id
        self.board = board
        self.board.set_pin_mode(pin_id, Constants.OUTPUT)

    def on(self):
        self.board.digital_write(self.pin, 1)

    def off(self):
        self.board.digital_write(self.pin, 0)


class FirmataCollector(Collector):
    def __init__(self, sleep, a_in, d_out):
        self.sleep = float(sleep)
        self.a_in = a_in
        self.d_out = d_out
        self.board = None
        self.digi = None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.board.shitdown()

    def read(self):
        self.board = PyMata3() if not self.board else self.board
        self.digi = [DigitalOut(self.board, i) for i in [int(i) for i in self.d_out.split(',')]]

        while True:
            try:
                results = {}
                for pin in [AnalogIn(self.board, i, Constants.ANALOG) for i in
                            [int(i) for i in self.a_in.split(',')]]:
                    results[pin.pin_id] = pin.value
                    # print(f'{str(pin.pin_id):>2}:{str(pin.value)}:<4 ', end='')
                # print('')
                self.board.sleep(self.sleep)
                yield results  # {0: 0-1023, 1: 0-1023}
            except (KeyboardInterrupt, SystemExit):
                self.board.shutdown()

    def task(self, message: Message, **kwargs) -> dict:
        pass

    def taskback(self, message: Message) -> None:

        if not self.board:
            print('No board, cannot call.')
            return

        d = message.data
        if '5' in d:
            print(d["5"])
            # for pin in self.digi:
            #     pin.on()
            #     self.board.sleep(1)
            #     pin.off()


class DataWarning:
    def __init__(self, pin):
        self.pin = str(pin)

    def task(self, message: Message, **kwargs) -> dict:
        d = message.data
        if self.pin in d:
            # print(d[self.pin])
            pass
