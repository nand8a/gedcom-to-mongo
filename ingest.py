from enum import Enum
import person
import logging
import pprint
from dbinterface import Db
log = logging.getLogger(__name__)

# INT_IDX = Enum('START')


pp = pprint.PrettyPrinter(indent=4)
FILENAME = '/home/jacques/industria/nand/gedcom/ged/duplessis_utf8.ged'



def file_parser(fqfn):
    reading = True
    with open(fqfn, 'r',  encoding='utf-8-sig') as f:
        while reading:
            line = f.readline()
            # strip away leading whitespace
            line = line.lstrip(' ')
            if line[0] == '0':
                if line[0] == 'TRLR':
                    # termination symbol
                    log.info('file parsing complete\nStats:')
                f = _person_reader(f, line)


def _person_reader(file_handler, line):
    log.debug('person_reader {}'.format(line))
    lines = []
    if 'INDI' not in line:
        return file_handler
    else:
        # add the first line of person record
        lines.append(line)
    while True:
        last_pos = file_handler.tell()
        line = file_handler.readline()
        line = line.lstrip(' ')
        if '0' in line[0]:
            # must deal sequentially due to max recursion depth
            file_handler.seek(last_pos)
            log.debug('full person record passed to parser is: {}'.format(lines))
            log.info('Connection retrieved : {}'.format(Db().get_connect()))
            Db().get_connect().coll.insert_one(person.parser(lines))
            return file_handler
        elif int(line[0]) > 0:
            log.debug('appending... {}'.format(line))
            lines.append(line)
