import unittest
import embedding_person as ep
from unittest import mock
from unittest.mock import MagicMock, call
import ingest



class TestIngest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def test_constructor(self):
        io = ingest.FileIngestor('nonsense.file')
        self.assertEqual(io.filename, 'nonsense.file')
        self.assertDictEqual(io.sinks, {})
        # omitting metadata for now

    def test_ingest_method(self):
        io = ingest.FileIngestor('nf')

        with self.assertRaises(KeyError) as context:
            io.ingest(notakey='notakey')

        io.read = MagicMock()
        read_mock = MagicMock()
        # these keys have much code smell
        io.read.return_value = iter([('person', [1, 2, 3])])
        io.write = MagicMock()
        io.ingest(person=read_mock, family='family')