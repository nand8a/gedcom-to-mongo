import person
import family
import logging
import pprint
from dbinterface import Db
import re
import settings
log = logging.getLogger(__name__)


pp = pprint.PrettyPrinter(indent=4)


def file_parser(fqfn):
    """
    parse a .ged formatted file by reading it line
    for line and interpreting the leftmost code and keys.
    :param fqfn: a fully qualified filename
    :return:
    """
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
            line = f.readline()


def _flush_data(data: list, fam_flg=False, person_flg=False):
    """
    Depending on whether or not these data in <data> are family or
    person oriented, persist them to the relevant database --- this
    will likely move to an OOP implementation where the objects write
    themselves (this is a still the prototype TODO)
    :param data: a list lines
    :param fam_flg: boolean which is true if data is mapped to family
    :param person_flg: true if data is mapped to person
    :return:
    """
    if fam_flg:
        log.debug('persisting family dictionary')
        t_dict = family.parser(data)
        Db().get_connect().collection(settings.sink_db, settings.sink_tbl_family).insert_one(t_dict)
    elif person_flg:
        t_dict = person.parser(data)
        Db().get_connect().collection(settings.sink_db, settings.sink_tbl_person).insert_one(t_dict)
    else:
        raise ValueError('this function only caters for family and person flags')


def _dict_builder(file_handler, line):
    """
    continue incrementing over the file_handler and extract the
    components related to FAM and INDI (only implemented thus far)
    :param file_handler: the file handler that the
    :param line: the last line pulled out of the file
    :return:
    """
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

