
import unittest
import os
from update_graffiti import GraffitiUpdater, GraffitiReader

class TestGraffitiUpdater(unittest.TestCase):
  def setUp(self):
    td = "testdata"
    self.good = os.path.join(td, 'simple')
    self.emptylines = os.path.join(td, 'somelinesempty')
    self.offby1 = os.path.join(td, 'offby1')
    self.empty = os.path.join(td, 'emptyfile')
    self.notutf8good = os.path.join(td, 'notutf8good')

    self.output_file = "testdata/graf_updater_output"

    with open(self.good, 'r') as f:
      self.good_lines = f.readlines()

    with open(self.emptylines, 'r') as f:
      self.emptylines_lines = f.readlines()

    with open(self.notutf8good, 'r') as f:
      self.notutf8good_lines = f.readlines()

  def tearDown(self):
    if os.path.exists(self.output_file):
      os.remove(self.output_file)

  def _check_output(self, expected):
    with open(self.output_file, 'r') as f:
      got = f.readline()
      self.assertEqual(got, expected)

  def test_writing_empty(self):
    updater = GraffitiUpdater(GraffitiReader(self.emptylines),
                              self.output_file)

    for line in self.emptylines_lines:
      updater.update()
      self._check_output(line)


  def test_writing(self):
    updater = GraffitiUpdater(GraffitiReader(self.good),
                              self.output_file)

    for line in self.good_lines:
      updater.update()
      self._check_output(line)

  def test_writing_emoji(self):
    updater = GraffitiUpdater(self.notutf8good,
                              self.output_file)

    for line in self.notutf8good_lines:
      updater.update()
      self._check_output(line)

  def test_loop(self):
    updater = GraffitiUpdater(GraffitiReader(self.good),
                             self.output_file,
                             loop=True)

    test_for = 100
    for i in range(test_for):
      updater.update()
      self._check_output(self.good_lines[i%len(self.good_lines)])

  def test_no_loop(self):
    updater = GraffitiUpdater(GraffitiReader(self.good),
                              self.output_file,
                              loop=False)

    test_for = 100
    for i in range(test_for):
      updater.update()
      if i >= len(self.good_lines):
        check_for = self.good_lines[-1]
      else:
        check_for = self.good_lines[i]
      self._check_output(check_for)

  def test_start_line(self):
    start_from = 4
    updater = GraffitiUpdater(GraffitiReader(self.good),
                              self.output_file,
                              line_index=start_from)

    for line in self.good_lines[start_from:]:
      updater.update()
      self._check_output(line)

  def test_start_line_last_line(self):
    start_from=7
    updater = GraffitiUpdater(GraffitiReader(self.good),
                              self.output_file,
                              line_index=start_from)

    for line in self.good_lines[start_from:]:
      updater.update()
      self._check_output(line)

  def test_start_line_too_big(self):
    start_from = 8
    with self.assertRaises(Exception):
      updater = GraffitiUpdater(GraffitiReader(self.good),
                                self.output_file,
                                line_index=start_from)

  def test_start_line_loop(self):
    start_from=5
    updater = GraffitiUpdater(GraffitiReader(self.good),
                              self.output_file,
                              line_index=start_from,
                              loop=True)
    test_for=24
    for i in range(test_for):
      updater.update()
      ii = i + start_from
      self._check_output(self.good_lines[ii%len(self.good_lines)])
