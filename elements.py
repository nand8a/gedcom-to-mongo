import logging
import pprint
log = logging.getLogger(__name__)
import utils
import re
from abc import ABCMeta

pp = pprint.PrettyPrinter(indent=4)


class GedcomElement(metaclass=ABCMeta):

    def __init__(self, lines: list):
        self._lines = lines
        self._i = 0
        self._parsed_dict = {}

    def current(self):
        try:
            return self._lines[self._i]
        except IndexError as e:
            return None

    def next(self):
        """
        get the next lines element
        :return:
        """
        try:
            self._i += 1
            return self._lines[self._i]
        except IndexError as e:
            return None

    def has_next(self):
        """
        is there a next item
        :return:
        """
        if self._i + 1 < len(self._lines):
            return True
        else:
            return False


class Family(GedcomElement):

    def __init__(self, lines: list):
        super(Family, self).__init__(lines)

    @staticmethod
    def is_family(line: str):
        if bool(re.search('0 @[A-Z0-9]*@ FAM', line)):
            return True
        else:
            return False

    def _children(self):
        children_list = []
        while self.current() and bool(re.search('1 CHIL', self.current())):
            # extract the child id
            child = re.search(r"@[A-Z0-9]*@", self.current()).group(0)
            children_list.append(child)
            if self.has_next():
                self.next()
            else:
                break
        return children_list

    def parser(self):
        """
        parse the family elements
        :return:
        """
        while self.has_next():
            if self.is_family(self.current()):
                identifier = self.current().split(' ')[1]
                log.debug('FAM: {}'.format(identifier))
                self._parsed_dict['_id'] = identifier
                self.next()
            elif self.current().startswith('1'):
                if '1 CHIL' in self.current():
                    key = 'chil'
                    if key not in self._parsed_dict:
                        self._parsed_dict[key] = []
                    child_list = self._children()
                    self._parsed_dict[key] += child_list
                else:  # todo - not dry - move to that function
                    local_dict, self._i = utils.ged_sub_structure(self._lines, self._i,
                                                            self.current().split(' ')[0])
                    self._parsed_dict.update(local_dict)
                    key = list(local_dict.keys())[0]
                    while self.has_next() and (self.current().split(' ')[0] != '1'):
                        local_dict, self._i = utils.ged_sub_structure(self._lines, self._i,
                                                                      self.current().split(' ')[0])
                        self._parsed_dict[key] = local_dict
            else:
                current_level = self.current()[0]
                ret_dict, self._i = utils.ged_sub_structure(self._lines, self._i, current_level)
                self._parsed_dict.update(ret_dict)
        log.debug(pp.pprint(self._parsed_dict))
        return self._parsed_dict


class Person(GedcomElement):

    def __init__(self, lines: list):
        super(Person, self).__init__(lines)

    @staticmethod
    def is_person(line: str):
        if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
            return True
        else:
            return False

    def _parse_chan(self):
        """
        Deal with special case where integer counter follows [1,2,3] sequence
        and splits the date tne time.
        > 1 CHAN
        > 2 DATE 28 Feb 2016
        > 3 TIME 00: 00:00
        create --> {chan_date = ISODate('28 Feb 2016')}
        :return: on success {chan_date: <datetime>}, on error
        {'raw': <raw string date>: 'error': <parse error>}
        """
        if '1 chan' not in self.current().lower():
            Exception('parse error: expected "1 chan", got "{}"'.format(self._lines[self._i].lower()))
        self.next()
        key = 'chan_date'
        log.debug(' lines ---- chan ---- {}'.format(self._lines))
        if '2 DATE'.lower() not in self.current().lower():
            log.debug('warning: expected a date first... pluggin')
            date = ''
        else:
            date = self.current().lstrip('2 DATE ').replace('\n', '')
        self.next()
        if '3 time' not in self.current().lower():
            log.debug('warning: expected a time, but none')
            time = ''
        else:
            # todo this lstrip chap is dangerous
            time = self.current().lstrip('3 TIME ').replace('\n', '')
        # todo there is surely a bug here
        self.next()
        ret = utils.get_date_dictionary(key, "{} {}".format(date, time))
        if ret:
            return ret
        else:
            log.error('could not parse date: {} time: {}'.format(date, time))
            return {}

    def _person_note(self):
        """
        helper function to pull out the commentary
        todo: this needs to be cleaned up as far as these awful
        string keys are concerned - move them to enum or other class
        """
        log.debug('doing person NOTE NOTE NOTE')
        if self.current() and self.current().startswith('1 NOTE'):
            log.debug('definitely doing NOTE NOTE NOTE')
            ret = re.sub('^1 NOTE ', '', self.current()) + ' '
            self.next()
            log.debug('next is {}'.format(self.current()))
            while self.current() and self.current().startswith('2 CON'):  # deals with CONC or CONT
                ret += re.sub('^2 CON[CT]* ', '', self.current()) + ' '
                self.next()
            # remove space introduced to account for continuations
            ret = ret[:-1]
            return ret
        else:
            return []

    def _person_name(self):
        log.debug('name before strip {}'.format(self.current()))
        name = re.sub('/', '', re.sub('^1 NAME ', '', self.current()))  # there is an annoying / in the name too
        log.debug('NAME: {}'.format(name))
        local_dict = {'name': name}
        self.next()
        while self.current() and self.current().split(' ')[0] != '1':
            level = self.current().split(' ')[0]
            person_sub_dict, self._i = utils.ged_sub_structure(self._lines, self._i, level)
            local_dict.update(person_sub_dict)
        return local_dict

    def parser(self):
        """
        Given the list of string lines provided in the constructor,
        construct a dictionary in the necessary format
        """
        # counter = 0
        while self.has_next():
            if 'INDI' in self.current():
                identifier = self.current().split(' ')[1]
                log.debug('INDI: {}'.format(identifier))
                self._parsed_dict['_id'] = identifier
                self.next()
            elif '1 NAME' in self.current():
                self._parsed_dict['name'] = self._person_name()
            elif '1 NOTE ' in self.current():  # todo: not DRY - duplicating string check
                self._parsed_dict['note'] = self._person_note()
                # todo: get rid of this awful index scheme
            elif self.current().startswith('1') and \
                    '1 CHAN' not in self.current():  # add exclusion for NAME here in case of i error
                local_dict, self._i = utils.ged_sub_structure(self._lines, self._i, self.current().split(' ')[0])
                self._parsed_dict.update(local_dict)
                key = list(local_dict.keys())[0]
                while self.current() and (self.current().split(' ')[0] != '1'):
                    local_dict, self._i = utils.ged_sub_structure(self._lines, self._i, self.current().split(' ')[0])
                    self._parsed_dict[key] = local_dict
            elif '1 CHAN' in self.current():
                ret_dict = self._parse_chan()
                self._parsed_dict.update(ret_dict)
        log.debug(pp.pprint(self._parsed_dict))
        return self._parsed_dict

