import logging
import pprint
log = logging.getLogger(__name__)
import utils

pp = pprint.PrettyPrinter(indent=4)


def _parse_chan(lines, i):
    """
    Deal with special case where integer counter follows [1,2,3] sequence
    and splits the date tne time.
    > 1 CHAN
    > 2 DATE 28 Feb 2016
    > 3 TIME 00: 00:00
    create --> {chan_date = ISODate('28 Feb 2016')}
    :param lines:
    :param i:
    :return: on success {chan_date: <datetime>}, on error
    {'raw': <raw string date>: 'error': <parse error>}
    """
    if '1 CHAN' not in lines[i]:
        return {}
    else:
        if '1 chan' not in lines[i].lower():
            Exception('parse error: expected "1 chan", got "{}"'.format(lines[i].lower()))
        i += 1
        key = 'chan_date'
        print(' lines ---- chan ---- {}'.format(lines))
        if '2 DATE'.lower() not in lines[i].lower():
            print('warning: expected a date first... pluggin')
            date = ''
        else:
            date = lines[i].lstrip('2 DATE').replace('\n', '')
        i += 1
        if '3 time' not in lines[i].lower():
            print('warning: expected a time, but none')
            time = ''
        else:
            time = lines[i].lstrip('3 TIME ').replace('\n', '')
        i += 1
        ret = utils.get_date_dictionary(key, "{} {}".format(date, time))
        if ret:
            return ret, i
        else:
            log.error('could not parse date: {} time: {}'.format(date, time))
            return {}, i


def _person_sub(lines, current_i, current_level):
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
            # special case, return either root {key: None} or {key: value}
            value = None
            try:
                value = split_lines[2]
            except Exception as e:
                pass
            i += 1
            return {key: value}, i
        if level != current_level:
            break
        level_dict[key] = ' '.join(split_lines[2:])
        print(key.lower() == 'date')
        if key.lower() == 'date':  # think about moving this to a place that applies to whole person dict (recursive)
            level_dict.update(utils.get_date_dictionary(key, level_dict[key]))
        i += 1
    return level_dict, i


def parser(lines):
    person_dict = {}
    i = 0
    line = lines[i]
    while i < len(lines):
        if 'INDI' in line:
            identifier = line.split(' ')[1]
            log.debug('INDI: {}'.format(identifier))
            person_dict['_id'] = identifier
            i += 1
            line = lines[i]
        if '1 NAME' in line:
            name = line  # this can be in the big loop
            log.debug('NAME: {}'.format(name))
            person_dict['name'] = {'name': name}
            i += 1
            while i < len(lines) and lines[i].split(' ')[0] != '1':
                level = line.split(' ')[0]
                local_dict, i = _person_sub(lines, i, level)
                person_dict['name'].update(local_dict)
                line = lines[i]
        if lines[i].startswith('1') and \
                '1 CHAN' not in lines[i]:
            local_dict, i = _person_sub(lines, i, lines[i].split(' ')[0])
            person_dict.update(local_dict)
            key = list(local_dict.keys())[0]
            while i < len(lines) and (lines[i].split(' ')[0] != '1'):
                local_dict, i = _person_sub(lines, i, lines[i].split(' ')[0])
                person_dict[key] = local_dict
        else:
            ret_dict, i = _parse_chan(lines, i)
            person_dict.update(ret_dict)
    log.debug(pp.pprint(person_dict))
    return person_dict

