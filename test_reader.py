import unittest
from os import path
from update_graffiti import GraffitiReader

class TestGraffitiReader(unittest.TestCase):
  def setUp(self):
    td = "testdata"
    self.good = path.join(td, 'good')
    self.long = path.join(td, 'superlong')
    self.emptylines = path.join(td, 'somelinesempty')
    self.offby1 = path.join(td, 'offby1')
    self.empty = path.join(td, 'emptyfile')
    self.notutf8good = path.join(td, 'notutf8good')
    self.notutf8toolong = path.join(td, 'notutf8long')


  def test_valid(self):
    """
    File with all lines <= 32 bytes should pass
    """
    reader = GraffitiReader(self.good)
    self.assertEqual(7, len(reader.lines))

  def test_valid_empty_lines(self):
    """
    Empty lines should count as lines
    """
    reader = GraffitiReader(self.emptylines)
    self.assertEqual(9, len(reader.lines))

  def test_empty(self):
    """
    Empty file should pass
    """
    reader = GraffitiReader(self.empty)
    self.assertEqual(0, len(reader.lines))

  def test_too_long(self):
    """
    File with more than 32 bytes per line should fail
    """
    with self.assertRaises(Exception):
      reader = GraffitiReader(self.long)

  def test_too_long_by_1(self):
    """
    File with 33 byte line should fail
    """
    with self.assertRaises(Exception):
      reader = GraffitiReader(self.offby1)

  def test_notutf8(self):
    """
    Non utf-8 input should pass if <= 32 bytes
    """
    reader = GraffitiReader(self.notutf8good)
    self.assertEqual(5, len(reader.lines))

  def test_notutf8toolong(self):
    """
    Non utf-8 input which is < 32 chars but > 32 bytes should fail
    """
    with self.assertRaises(Exception):
      reader = GraffitiReader(self.notutf8toolong)
