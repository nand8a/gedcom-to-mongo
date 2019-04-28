import unittest
import embedding_person as ep
from unittest import mock

from unittest.mock import MagicMock, call, mock_open, patch
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

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_ingest_read_with_nothing(self, mock_open):
        io = ingest.FileIngestor('nf')
        with self.assertRaises(StopIteration) as context:
            next(io.read())

    @patch("builtins.open", new_callable=mock_open, read_data="0 TRLR stuff")
    @patch('ingest.log')
    def test_ingest_read_at_trlr(self, mock_log, mock_open):
        io = ingest.FileIngestor('nf')
        with self.assertRaises(StopIteration) as context:
            next(io.read())
        expected_calls_to_logger = [
            call('file parsing complete\nStats:')
        ]
        #print(mock_log.info.call_args_list)
        mock_log.info.assert_has_calls(expected_calls_to_logger, any_order=True)

    def test_private_buffered_read(self):
        filehandler = MagicMock()
        filehandler.tell.side_effect = [10, 11, 12, 13]  # same length as readline
        lines = ['1 line 1', '2 line 2', '3 line 3', '0 end']
        filehandler.readline.side_effect = lines
        io = ingest.FileIngestor('nf')
        buffered_lines = ['start']
        io._buffered_read(filehandler, buffered_lines)
        self.assertListEqual(['start'] + lines[:-1], ['start', '1 line 1', '2 line 2', '3 line 3'])

    def test_private_buffered_read_conditionals(self):
        # test line being none conditional
        filehandler = MagicMock()
        buffered_lines = ['start']
        filehandler.tell.side_effect = [10, 11, 12, 13]  # same length as readline
        filehandler.readline.return_value = None
        io = ingest.FileIngestor('nf')
        io._buffered_read(filehandler, buffered_lines)
        self.assertListEqual(['start'], buffered_lines)

        # deal with case where



    # @patch("builtins.open", new_callable=mock_open, read_data="0 @I1@\n1 LINE1\n0 STUFF")
    # @patch('ingest.log')
    # @patch('elements.Person') # you are here
    # def test_ingest_read_at_trlr(self, mock_log, mock_open):
    #     io = ingest.FileIngestor('nf')
    #     next(io.read())