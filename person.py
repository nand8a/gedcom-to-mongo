import logging
import pprint
log = logging.getLogger(__name__)
import utils
import re

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
        i += 1
        return {}, i  # todo deal with this outside of chan which is now acting as a catch-all - superbad.
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
            date = lines[i].lstrip('2 DATE ').replace('\n', '')
        i += 1
        if '3 time' not in lines[i].lower():
            print('warning: expected a time, but none')
            time = ''
        else:
            # todo this lstrip chap is dangerous
            time = lines[i].lstrip('3 TIME ').replace('\n', '')
        # todo there is surely a bug here
        i += 1
        ret = utils.get_date_dictionary(key, "{} {}".format(date, time))
        if ret:
            return ret, i
        else:
            log.error('could not parse date: {} time: {}'.format(date, time))
            return {}, i


def _person_note(lines, i):
    """
    helper function to pull out the commentary
    todo: this needs to be cleaned up as far as these awful
    string keys are concerned - move them to enum or other class
    :param lines:
    :param i:
    :return:
    """
    if lines[i].startswith('1 NOTE'):
        ret = re.sub('^1 NOTE ', '', lines[i]) + ' '
        i += 1
        while lines[i].startswith('2 CONC'):
            ret += re.sub('^2 CONC ', '', lines[i]) + ' '
            i += 1
        # remove space introduced to account for continuations
        ret = ret[:-1]
        return ret, i
    else:
        return [], i


def _person_name(lines, i):
    log.debug('name before strip {}'.format(lines[i]))
    name = re.sub('^1 NAME ', '', lines[i])
    log.debug('NAME: {}'.format(name))
    local_dict = {'name': name}
    i += 1
    while i < len(lines) and lines[i].split(' ')[0] != '1':
        level = lines[i].split(' ')[0]
        person_sub_dict, i = utils.ged_sub_structure(lines, i, level)
        local_dict.update(person_sub_dict)
    return local_dict, i


def parser(lines):
    person_dict = {}
    i = 0
    while i < len(lines):
        if 'INDI' in lines[i]:
            identifier = lines[i].split(' ')[1]
            log.debug('INDI: {}'.format(identifier))
            person_dict['_id'] = identifier
            i += 1
        if '1 NAME' in lines[i]:
            person_dict['name'], i = _person_name(lines, i)
            log.debug('after name insertion: {}'.format(person_dict))
        if '1 NOTE ' in lines[i]:  # todo: not DRY - duplicating string check
            person_dict['note'], i = _person_note(lines, i)
            # todo: get rid of this awful index scheme
        if lines[i].startswith('1') and \
                '1 CHAN' not in lines[i]:  # add exclusion for NAME here in case of i error
            local_dict, i = utils.ged_sub_structure(lines, i, lines[i].split(' ')[0])
            person_dict.update(local_dict)
            key = list(local_dict.keys())[0]
            while i < len(lines) and (lines[i].split(' ')[0] != '1'):
                local_dict, i = utils.ged_sub_structure(lines, i, lines[i].split(' ')[0])
                person_dict[key] = local_dict
        else:
            ret_dict, i = _parse_chan(lines, i)
            person_dict.update(ret_dict)
    log.debug(pp.pprint(person_dict))
    return person_dict

