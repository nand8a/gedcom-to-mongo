from enum import Enum
import person
import family
import logging
import pprint
from dbinterface import Db
import re
log = logging.getLogger(__name__)

# INT_IDX = Enum('START')


pp = pprint.PrettyPrinter(indent=4)



def file_parser(fqfn):
    counter = 0
    with open(fqfn, 'r',  encoding='utf-8-sig') as f:
        line = f.readline()
        while line != "":
            # strip away leading whitespace
            line = line.lstrip(' ')
            if line and line[0] == '0':
                if line[0] == 'TRLR':
                    # termination symbol
                    log.info('file parsing complete\nStats:')
                f = _dict_builder(f, line)
                #here. it is skipping the last one cos we are not matching to 0
            line = f.readline()


def _flush_data(data: list, fam_flg=False, person_flg=False):
    if fam_flg:
        log.debug('persisting family dictionary')
        t_dict = family.parser(data)
        Db().get_connect().collection('gedcom', 'fam_test').insert_one(t_dict)
    elif person_flg:
        t_dict = person.parser(data)
        Db().get_connect().collection('gedcom', 'person_test').insert_one(t_dict)


def _dict_builder(file_handler, line):
    log.debug('dict_builder called with {}'.format(line))
    fam_flg = False
    person_flg = False
    if bool(re.search('0 @[A-Z0-9]*@ FAM', line)):
        fam_flg = True
    elif bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
        person_flg = True
    else:
        return file_handler
    lines = [line]
    while True:
        last_pos = file_handler.tell()
        line = file_handler.readline()
        line = line.lstrip(' ').lstrip('\n')
        if not line:
            # the jig is up
            _flush_data(lines, fam_flg, person_flg)
            return file_handler
        if line and '0' in line[0]:
            # must deal sequentially due to max recursion depth
            file_handler.seek(last_pos)
            log.debug('full person record passed to parser is: {}'.format(lines))
            log.info('Connection retrieved : {}'.format(Db().get_connect()))
            _flush_data(lines, fam_flg=fam_flg, person_flg=person_flg)
            return file_handler
        elif int(line[0]) > 0:
            log.debug('appending... {}'.format(line))
            lines.append(line)

