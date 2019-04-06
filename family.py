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
        self._i += 1
        return self._lines[self._i]

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

