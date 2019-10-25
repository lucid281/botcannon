import pandas as pd

import botcannon

from .hardware.firmata import FirmataCollector
from .hardware.firmata import DataWarning
from .hardware.sensors import Thermistor
from .hardware.sensors import VoltageDivider
from .tools.term import plot


class Thermistors:
    gm_ntc = [-40, 99326], [0, 9256], [150, 46.7]


class RoomShell:
    """Commands for getting viewing sensor data."""
    def __init__(self, service_name, room_temp, room_light):
        self._b = botcannon.BotCannon()
        self._service = self._b.service(service_name)
        self._service.dataframes.chat = True
        df = self._service.dataframes
        self._pin_index = {"room_temp": room_temp,
                           "room_light": room_light, }
        self._pin_funcs = {
            room_temp: Thermistor(10000, 1023, *Thermistors.gm_ntc),
            room_light: VoltageDivider(10000, 1023),
        }
        #                               [min, max, offset]
        self._samples = {
            'room_temp': {
                'week': {
                    #    [sample, set]
                    's': {"func": [df.days, 7], "args": ['12h', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'today': {
                    #    [sample, set]
                    's': {"func": [df.hour, 12], "args": ['30min', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'hours': {
                    #    [sample, set]
                    's': {"func": [df.hour, 1], "args": ['12h', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'now': {
                    #    [sample, set, min, max, h, offset]
                    's': {"func": [df.now, 301], "args": ['30s', 'mean', 5]},
                    'l': ['30min', 'mean', 5],
                },
            },
            'room_light': {
                'week': {
                    #    [sample, set]
                    's': {"func": [df.days, 7], "args": ['12h', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'today': {
                    #    [sample, set]
                    's': {"func": [df.hour, 12], "args": ['30min', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'hours': {
                    #    [sample, set]
                    's': {"func": [df.hour, 1], "args": ['30min', 'mean', 5]},
                    'l': {"t": 12, "args": ['3h', 'mean', 5]},
                },
                'now': {
                    #    [sample, set, min, max, h, offset]
                    's': {"func": [df.now, 301], "args": ['30s', 'mean', 5]},
                    'l': ['30min', 'mean', 5],
                },
            },

        }
        #                                 [min,max,offset]
        self._scales = {"room_temp": [None, None, 4],
                        "room_light": [None, None, 4], }

    def _get_frame(self, sensor, dataframe) -> pd.Series:
        sensor = self._pin_index[sensor]
        func = self._pin_funcs[sensor].get
        return dataframe[sensor][sensor].apply(func)

    def _plot(self, dataframe, sample, stat_mode, h=5, min=60, max=90, offset=3):
        # df = self.apply(sensor, dataframe)
        df = dataframe

        if stat_mode == 'min':
            series = df.resample(sample).min()
        elif stat_mode == 'max':
            series = df.resample(sample).max()
        else:
            series = df.resample(sample).mean()

        return plot(series, min, max, offset, h, chat=False)

    def _stat_text(self, dataframe: pd.Series):
        return f'{dataframe.max():.1f} / {dataframe.min():.1f}' \
               f' / {dataframe.max() - dataframe.min():.1f}' \
               f' / {dataframe.std():.1f}'

    def _p_args(self, sensor, when, size):
        return []

    def _time_span(self, frame):
        span = (frame.index.max() - frame.index.min())
        h, remainder = divmod(span.total_seconds(), 3600)
        m, s = divmod(remainder, 60)
        return f'span: *{h}h* *{m}m* *{s:.1f}s*'

    def today(self):
        sensor = "room_temp"
        s_data = self._samples[sensor]["today"]["s"]
        func, param = s_data["func"]
        data = func(param)
        room_temp = self._get_frame(sensor, data)

        s = f'`{sensor}` last 12hr: *~{room_temp.mean():.1f}* [{self._stat_text(room_temp)}]\n' \
            f'```\n{self._plot(room_temp, *s_data["args"], *self._scales[sensor])}\n```\n' \
            f'{self._time_span(room_temp)}'
        return s

    def now(self, seconds=None):
        sensor = "room_temp"
        msg = "last 5min"
        s_data = self._samples[sensor]["now"]["s"]
        func, param = s_data["func"]
        data = func(param) if not seconds else func(seconds)
        room_temp = self._get_frame(sensor, data)

        result = f'`{sensor}` {msg}:  *~{room_temp.mean():.1f}* [{self._stat_text(room_temp)}]\n' \
                 f'```\n{self._plot(room_temp, *s_data["args"], *self._scales[sensor])}\n```\n' \
                 f'{self._time_span(room_temp)}'
        return result

    def week(self):
        sensor = "room_temp"
        s_data = self._samples[sensor]["week"]["s"]
        func, param = s_data["func"]
        data = func(param)
        room_temp = self._get_frame(sensor, data)

        s = f'`{sensor}` last week: *~{room_temp.mean():.1f}* [{self._stat_text(room_temp)}]\n' \
            f'```\n{self._plot(room_temp, *s_data["args"], *self._scales[sensor])}\n```\n' \
            f'{self._time_span(room_temp)}'
        return s

    def hours(self, hours, frequency):
        sensor = "room_temp"
        s_data = self._samples[sensor]["hours"]["s"]
        func, param = s_data["func"]
        data = func(hours)
        room_temp = self._get_frame(sensor, data)

        s = f'`{sensor}` last {hours}h: *~{room_temp.mean():.1f}* [{self._stat_text(room_temp)}]\n' \
            f'```\n{self._plot(room_temp, frequency, "mean", 5, *self._scales[sensor])}\n```\n' \
            f'{self._time_span(room_temp)}'
        return s

    def light(self, hours):
        sensor = "room_light"
        s_data = self._samples[sensor]["hours"]["s"]
        func, param = s_data["func"]
        data = func(hours)
        room_temp = self._get_frame(sensor, data)

        s = f'`{sensor}` last {hours}h: *~{room_temp.mean():.1f}* [{self._stat_text(room_temp)}]\n' \
            f'```\n{self._plot(room_temp, *s_data["args"], *self._scales[sensor])}\n```\n' \
            f'{self._time_span(room_temp)}'
        return s