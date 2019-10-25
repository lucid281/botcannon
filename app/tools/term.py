from math import ceil, floor


def plot(series, minimum=None, maximum=None, offset=4, height=7, placeholder='{:8.2f} ', chat=False):
    """ Possible cfg parameters are 'minimum', 'maximum', 'offset', 'height' and 'format'.
    cfg is a dictionary, thus dictionary syntax has to be used.
    Example: print(plot(series, { 'height' :10 }))
    """
    maximum = maximum if maximum else max(series)
    minimum = minimum if minimum else min(series)
    if minimum == maximum:
        minimum -= 1
        maximum += 1
    interval = abs(float(maximum) - float(minimum))
    ratio = height / interval
    min2 = floor(float(minimum) * ratio)
    max2 = ceil(float(maximum) * ratio)

    intmin2 = int(min2)
    intmax2 = int(max2)

    rows = abs(intmax2 - intmin2)
    width = len(series) + offset

    result = [[' '] * width for i in range(rows + 1)]

    # axis and labels
    for y in range(intmin2, intmax2 + 1):
        label = placeholder.format(float(maximum) - ((y - intmin2) * interval / rows))
        result[y - intmin2][max(offset - len(label), 0)] = label
        result[y - intmin2][offset - 1] = '┼' if y == 0 else '┤'

    y0 = int(series[0] * ratio - min2)
    result[rows - y0][offset - 1] = '┼'  # first value

    for x in range(0, len(series) - 1):  # plot the line
        yr0 = round(series[x + 0] * ratio)
        yr1 = round(series[x + 1] * ratio)
        try:
            y0 = int(yr0 - intmin2)
        except ValueError:
            y0 = None

        try:
            y1 = int(yr1 - intmin2)
        except ValueError:
            y1 = None

        if not isinstance(y0, int):
            result[rows - 0][x + offset] = '='

        elif not isinstance(y1, int):
            result[rows - 0][x + offset] = '!'

        else:
            if y0 == y1:
                result[rows - y0][x + offset] = '─'  # '─'
            else:
                result[rows - y1][x + offset] = '╰' if y0 > y1 else '╭'
                result[rows - y0][x + offset] = '╮' if y0 > y1 else '╯'
                start = min(y0, y1) + 1
                end = max(y0, y1)
                for y in range(start, end):
                    result[rows - y][x + offset] = '│'
    r = '\n'.join([''.join(row) for row in result])
    if chat:
        return f'```\n' \
               f'{r}\n' \
               f'```'
    else:
        return r
