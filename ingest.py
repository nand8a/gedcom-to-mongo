import elements
import pprint
from dbinterface import *
import logging
from typing import Iterator
log = logging.getLogger(__name__)


pp = pprint.PrettyPrinter(indent=4)


class FileIngestor(object):

    def __init__(self, source_filename):
        self.filename = source_filename
        self.meta_data = {'count': {'person': 0, 'family': 0}}
        self.sinks = {}

    def write(self, data: dict, datastore: DataStore):  # todo pass in the correct data connector here
        """
        write function to persist data from the file to a mongo database
        as configured in settings
        :param data:
        :param datastore: a datastore to write to
        :return:
        """
        datastore.write(data)
        #MongoDb().collection(settings.sink_db, settings.sink_tbl[tbl_key]).insert_one(data)
        # todo can get the collection name out here and use it for the metacount
        #self.meta_data['count'] += 1

    def _buffered_read(self, filehandler, buffered_lines):
        """
        A helper function to buffer the lines. It is operator on the references so it is changing the
        filehandler and the buffered_lines data structure.
        :param filehandler:
        :param buffered_lines:
        :return:
        """
        while True:
            last_pos = filehandler.tell()
            line = filehandler.readline()
            if not line:  # readline can return None if the file ends unexpectedly
                break
            line = line.lstrip(' ').lstrip('\n')
            if line and '0' in line[0]:
                # must deal sequentially due to max recursion depth
                filehandler.seek(last_pos)
                log.debug('full record passed to parser is: {}'.format(buffered_lines))
                break
            else:  # int(line[0]) > 0
                log.debug('appending... {}'.format(line))
                buffered_lines.append(line)

    def read(self) -> Iterator[tuple]:
        """
        parse a .ged formatted file by reading it line
        for line and interpreting the leftmost code and keys.
        This is a generator function
        :return:
        """
        with open(self.filename, 'r',  encoding='utf-8-sig') as f:
            line = f.readline()
            while line != "":
                # strip away leading whitespace
                line = line.lstrip(' ')
                if line and line[0] == '0':
                    if line.startswith('0 TRLR'):
                        # termination symbol - explicitly terminate
                        log.info('file parsing complete\nStats:')
                        raise StopIteration('completed file parsing')
                    else:
                        # start buffering lines until the next 0
                        buffered_lines = [line]
                        self._buffered_read(f, buffered_lines)
                        # done buffering
                        if elements.Family.is_family(buffered_lines[0]):
                            data_dict = elements.Family(buffered_lines).parser()
                            yield 'family', data_dict
                        elif elements.Person.is_person(buffered_lines[0]):
                            data_dict = elements.Person(buffered_lines).parser()
                            yield 'person', data_dict
                        else:
                            log.debug('this non-breaking functionality is not implemented')
                else:
                    raise RuntimeError('gedcom format not as expected, or buffering of reads is failing')
                line = f.readline()

    def ingest(self, *args, **kwargs):
        """
        This ingestor is tightly coupled (presently) to person and family databases
        :param args:
        :param kwargs:
        :return:
        """
        try:
            # todo - fix this key poop. smelly
            self.sinks['person'] = kwargs['person']
            self.sinks['family'] = kwargs['family']
        except KeyError as e:
            log.error('ingest function not correctly called with "person=person.datasource", '
                      'or "family=family.datasource"')
            raise

        try:
            reader = self.read()
            while True:
                key, data = next(reader)
                self.write(data, self.sinks[key])
        except StopIteration as e:
            pass



