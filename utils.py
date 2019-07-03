import datetime
import logging
log = logging.getLogger(__name__)


valid_formats = ['%Y', "%Y-%M-%D", "%Y%M%D",
                 "%d %b %Y", "%d %b %Y %H:%M:%S", "%b %Y %H:%M:%S"]


def get_date_dictionary(key: str, date: str):
    """
    format dictionary to program required structure
    :param key: the key that we are currently processing
    :param date: a date to translate to datetime object
    :return: a field if successful, else error field and raw value
    """
    date_obj = get_date(date)
    if date_obj:
        return {key: date_obj}
    else:
        return {key: {'raw': date, 'error': True}}


def get_date(date: str):
    """
    using the locally defined 'fmt' options, attempt to
    format the date string to a datetime object
    :param date: a date string
    :return: a datetime object
    """
    # deal with exception where it is a year only
    try:
        if len(date) == 4 and int(date) > 1000:
            log.debug("suspected YYYY only date: {}".format(date))
    except ValueError as e:
        pass
    for fmt in valid_formats:
        try:
            return datetime.datetime.strptime(date, fmt)
        except Exception as e:
            pass
    return None



def ged_sub_structure(lines, current_i, current_level):
    """
    :param lines: list of lines
    :param current_i: the current index into the list
    :param current_level: the current 'level' (where level in [2,3,4,...]
    :return: a dictionary where all level elements are nested at the same depth
    """
    i = current_i
    level_dict = {}
    # we increment only after the first run of the loop
    log.debug('params: current_i: {}, current_level: {}'.format(current_i, current_level))
    log.debug('called with line: {}'.format(lines[i]))
    while i < len(lines):
        split_lines = lines[i].rstrip('\n').split(' ')
        level, key = split_lines[0], split_lines[1].lower()
        if current_level == '1':
            # special case, return either root {key: None} or {key: value}  - this forces the insert
            value = None
            try:
                value = split_lines[2]
            except Exception as e:
                pass
            i += 1
            return {key: value}, i
        if level < current_level:
            log.debug('level {} != current_level {}'.format(level, current_level))
            break
        level_dict[key] = ' '.join(split_lines[2:])
        if key.lower() == 'date':
            log.debug('key == date, updating "date" : {}'.format(level_dict[key]))
            level_dict.update(get_date_dictionary(key, level_dict[key]))
        i += 1
    log.debug(level_dict)
    return level_dict, i
