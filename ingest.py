import person
import family
import logging
import pprint
from dbinterface import Db
import re
import settings
log = logging.getLogger(__name__)


pp = pprint.PrettyPrinter(indent=4)


class FileIngestor(object):

    def __init__(self, source_filename):
        self.filename = source_filename
        self.meta_data = {'count': {'person': 0, 'family': 0}}

    def ingest(self):
        self.read()

    def write(self, data: dict, tbl_key: str):
        """
        write function to persist data from the file to a mongo database
        as configured in settings
        :param data:
        :param tbl_key:
        :return:
        """
        if tbl_key not in settings.sink_tbl.keys():
            raise ValueError('provided table key {}, is not in settings list of keys'.format(tbl_key))
        Db().get_connect().collection(settings.sink_db, settings.sink_tbl[tbl_key]).insert_one(data)
        self.meta_data['count'][tbl_key] += 1

    def read(self):
        """
        parse a .ged formatted file by reading it line
        for line and interpreting the leftmost code and keys.
        :return:
        """
        with open(self.filename, 'r',  encoding='utf-8-sig') as f:
            line = f.readline()
            while line != "":
                # strip away leading whitespace
                line = line.lstrip(' ')
                if line and line[0] == '0':
                    if line[0] == 'TRLR':
                        # termination symbol
                        log.info('file parsing complete\nStats:')
                    else:
                        # start buffering lines until the next 0
                        buffered_lines = [line]
                        while True:
                            last_pos = f.tell()
                            line = f.readline()
                            line = line.lstrip(' ').lstrip('\n')
                            if not line:
                                # the jig is up
                                break
                            elif line and '0' in line[0]:
                                # must deal sequentially due to max recursion depth
                                f.seek(last_pos)
                                log.debug('full record passed to parser is: {}'.format(buffered_lines))
                                log.info('Connection retrieved : {}'.format(Db().get_connect()))
                                break
                            elif int(line[0]) > 0:
                                log.debug('appending... {}'.format(line))
                                buffered_lines.append(line)
                        # done buffering
                        if family.is_family(buffered_lines[0]):
                            data_dict = family.parser(buffered_lines)
                            self.write(data_dict, 'family')
                        elif person.is_person(buffered_lines[0]):
                            data_dict = person.parser(buffered_lines)
                            self.write(data_dict, 'person')
                line = f.readline()
