import numpy
import scipy.optimize


class VoltageDivider:
    def __init__(self, r_bias, scale):
        self.scale = scale
        self.r_bias = r_bias

    def reading_to_resistance(self, reading):
        try:
            return self.r_bias * (self.scale / float(reading) - 1)
        except ZeroDivisionError:
            return self.r_bias * (self.scale / 0.1 - 1)

    def get(self, reading):
        return self.reading_to_resistance(reading)


class SteinhartHart(VoltageDivider):
    def __init__(self, r_bias, scale, cold: list, warm: list, hot: list):
        """
        Where T is temp in C, and R is resistance ohms for 3 temp ranges
        :param cold:  [T, R]
        :param warm:  [T, R]
        :param hot:  [T, R]
        """
        super().__init__(r_bias, scale)
        exp_data = numpy.array([
            cold,  # [-40, 99326],  # Low end of sensor or range
            warm,  # [0, 9256],  # Ideal or reasonable middle
            hot,  # [150, 46.7]  # High end of sensor or range
        ])

        temps = exp_data[:, 0]
        resist = exp_data[:, 1]

        # give a ballpark estimate to start from, minimization won't
        # converge if we start off too far away...
        p0 = [0.1e-3, 0.1e-4, 0.1e-7]

        self.coefs, covariance = scipy.optimize.curve_fit(self._steinhart_hart, resist, temps, p0)

    def _steinhart_hart(self, r, a, b, c):
        """
        Steinhart-Hart Equation, as found on Wikipedia.
        r : resistance of a thermistor, measured in Ohms
        a,b,c : steinhart-hart coefficients [a] = 1/K

        returns : temperature in degrees celsius!
        """
        one_over_kelvins = a + b * numpy.log(r) + c * numpy.log(r) ** 3
        return 1.0 / one_over_kelvins - 273.15

    def temp(self, reading):
        r = self.reading_to_resistance(reading)
        return self._steinhart_hart(r, *self.coefs)


class Thermistor(SteinhartHart):
    def __init__(self, r_bias, scale, cold: list, warm: list, hot: list):
        self.parent = super().__init__(r_bias, scale, cold, warm, hot)

    def f(self, reading):
        c = self.temp(reading)
        return c * 1.8 + 32

    def c(self, reading):
        return self.temp(reading)

    def get(self, reading):
        # r = VoltageDivider.get(reading)
        r = self.f(reading)
        return r
