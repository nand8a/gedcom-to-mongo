import dateutil.parser


def _parse_chan(lines, i):
    """
    expected format
    # 1 CHAN
    # 2 DATE 28 Feb 2016
    # 3 TIME 00: 00:00
    # --> creates {" chan_date = isodate('28 Feb 2016') }
    :param lines:
    :param i:
    :return:
    """
    print(len(lines))
    if '1 CHAN' not in lines[i]:
        print(lines[i])
        return {}
    else:
        if '1 chan' not in lines[i].lower():
            Exception('parse error: expected "1 chan", got "{}"'.format(lines[i].lower()))
        i += 1
        print('chan date')
        key = 'chan_date'
        if '2 DATE'.lower() not in lines[i].lower():
            print('warning: expected a date first... pluggin')
            date = ''
        else:
            date = lines[i].lstrip('2 DATE')
        i += 1
        if '3 time' not in lines[i].lower():
            print('warning: expected a time, but none')
            time = ''
        else:
            time = lines[i].lstrip('3 TIME ')
        try:
            date_obj = dateutil.parser.parse("{} {}".format(date, time))
        except ValueError as e:
            print('failed to convert {} {}'.format(date, time))
            raise e
        i += 1
        return {key: date_obj}, i
