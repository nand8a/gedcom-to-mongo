import elements
import pprint
from dbinterface import *
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

    def read(self):
        """
        parse a .ged formatted file by reading it line
        for line and interpreting the leftmost code and keys.
        :return:
        """
        with open(self.filename, 'r',  encoding='utf-8-sig') as f:
            print('ONCE')
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
                                break
                            elif int(line[0]) > 0:
                                log.debug('appending... {}'.format(line))
                                buffered_lines.append(line)
                        # done buffering
                        if elements.Family.is_family(buffered_lines[0]):
                            data_dict = elements.Family(buffered_lines).parser()
                            yield 'family', data_dict
                        elif elements.Person.is_person(buffered_lines[0]):
                            data_dict = elements.Person(buffered_lines).parser()
                            print('person done {}'.format(buffered_lines[0]))
                            yield 'person', data_dict
                line = f.readline()

    def ingest(self, *args, **kwargs):
        """
        This ingestor is tightly coupled (presently) to person and family databases
        :param args:
        :param kwargs:
        :return:
        """
        try:
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



