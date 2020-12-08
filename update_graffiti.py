# Copyright Pig Frown 2020
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 23):
# <pigfrown@protonmail.com> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.   Pig Frown
# ----------------------------------------------------------------------------
#
#
# Until prysm adds the ability to update the graffiti tag, this script can be used to change
# graffiti everytime a block is found. It can (maybe) be used with other clients.
# ~~ Assumptions:
# 1) prysm validator is running as a systemd service.
# 2) prysm validator systemd service reads from (by default) /tmp/graffiti to populate the
# contents of the --graffiti field (see example service file on github)
# ~~ How it works
# Read in a list of graffiti lines we want to add, in order, to the blockchain.
# Each line must be equal to or less than 32 bytes
# Poll the systemd journal for the prysmvalidator service until a block is submitted.
# When a block has been submitted, update (by default) /tmp/graffiti with the new graffiti.
# Restart the systemd service to use the new graffiti.
# ~~ Bugs
# Probably some.
# ~~ Security Issues
# anyone with write access to /tmp/graffiti can fuck up your shit.
# Probably more.
# ~~ TODO
# Better subprocess/systemctl restart error checking
# Proper handling/escaping of input lines

import argparse
import select
import systemd.journal
import subprocess

class Graffiti():
  """
  Polls the journal looking for an submitted block and updates the given path when that happens
  """
  def __init__(self, service_name, update_path, graffiti_input, line_index=0, loop=False, search_for=None):
    """
    Polls systemd log for block submissions and updates graffiti file when one is found

    :param service_name: The systemd service name to poll and restart
    :param update_path: The graffiti file we will update (systemd service should read graf here)
    :param graffiti_input: newline seperated list of graffiti "tags" to use (32bytes or less)
    :param line_input: the line number of graffiti_input to start with
    :param loop: If True then return to the start of graffiti_input once all lines have been used
    :param search_for: The string to search for the logs. (maybe) can be used to make this script
                       work with clients other than prysm
    """
    self.service_name = service_name
    self.update_path = update_path
    self.service = ServiceRestarter(service_name)
    self.graffiti_reader = GraffitiReader(graffiti_input)
    self.graffiti_updater = GraffitiUpdater(self.graffiti_reader,
                                            update_path,
                                            line_index=line_index,
                                            loop=True)

    #This is for prysm. Change this to make the script (maybe) work on other clients
    if search_for is None:
        self.search_for = "Submitted new block"
    else:
        self.search_for = search_for

  def _setup_journal(self):
    #Thanks stackoverflow :)
    self.journal = systemd.journal.Reader()
    self.journal.log_level(systemd.journal.LOG_INFO)
    self.journal.add_match(_SYSTEMD_UNIT=self.service)
    self.journal.seek_tail()
    self.journal.get_previous()

    self.poll = select.poll()
    self.poll.register(self.journal, self.journal.get_events())

  def start(self):
    #Set the graffiti file to the first line requested and restart the service so it's used
    self.graffiti_updater.update()
    self.service.restart()
    self._setup_journal()
    while self.poll.poll():
      if self.journal.process() != systemd.journal.APPEND:
        continue

      for entry in self.journal:
        if self.search_for in entry['MESSAGE']:
          self.block_submitted()

  def block_submitted(self):
    print("We've submitted a block 😎")
    self.graffiti_updater.update()
    print(f"Restarting {self.service_name}")
    self.service.restart()


class ServiceRestarter():
  """
  Helper to restart the systemd service
  """
  def __init__(self, service_name):
    self.service_name = service_name
    self.cmd = f"systemctl restart {self.service_name}"

  def restart(self):
    print(f"Restarting {self.service_name}")
    print(self.cmd)
    done = subprocess.run(self.cmd, shell=True)
    #TODO check it actually worked derp

class GraffitiUpdater():
  """
  Updates the Graffiti file
  """
  def __init__(self, graffiti_input, graffiti_path, line_index=0, loop=False):
    self.input_lines = graffiti_input.lines
    self.graffiti_path = graffiti_path
    self.line_index = line_index
    self.lines_len = len(self.input_lines)
    self.loop = loop

    if self.line_index > self.lines_len:
      raise Exception("Requested to start at line {line_index} but only given {lines_len} lines")

  def get_line(self):
      return self.input_lines[self.line_index%self.lines_len]

  def update(self):
    if (self.line_index >= self.lines_len) and not self.loop:
      print("Reached the end of the lines and no loop requested. Not updating")
      return


    with open(self.graffiti_path, 'w') as f:
      line = self.get_line()
      print(f"Writing line: {line}")
      f.write(line)
    self.line_index += 1
    print(f"Next grafiti line will be : {self.line_index}, {self.get_line()}")

class GraffitiReader():
  """
  Reads and checks the input
  """
  def __init__(self, path):
    self.path = path
    self.read_lines()
    self.check_lines()

  def read_lines(self):
    with open(self.path, 'r') as f:
      self.lines = f.readlines()

  #TODO encoding of input could change byte length. Check this
  def check_lines(self):
    for i, line in enumerate(self.lines):
      #Remove the newline so it doesn't get counted
      #TODO: this will probably fail on windows? 🤷
      stripped_line = line.rstrip("\n")
      #Count the bytes not the characters.
      #Encode will default to utf-8.. which might not be the encoding
      #but it will count the bytes correctly
      length = len(stripped_line.encode())
      if length > 32:
        raise Exception(f"line {i} ({line}) is too long ({length} chars)")
    return True

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Update ETH grafiti when block proposed")
  parser.add_argument('--service',
                      dest="service",
                      type=str,
                      help="Service name of validator",
                      required=False,
                      default="prysmvalidator.service")
  parser.add_argument('--output',
                      dest="output",
                      type=str,
                      help="Path name of output file. Service file should use this file to populate graffiti",
                      required=False,
                      default="/tmp/graffiti")
  parser.add_argument('input',
                      type=str,
                      help="Path name of file containing graffiti lines. Each line should be <= 32 bytes",
                      )
  parser.add_argument('--line_index',
                      dest="line_index",
                      type=int,
                      help="The line index to start from",
                      required=False,
                      default=0)
  parser.add_argument("--search_for",
                      dest="search_for",
                      type=str,
                      help="The string that is used to detect if a block has been proposed",
                      required=False,
                      default="Submitted new block") #works with prysm
  parser.add_argument('--loop',
                      action="store_true",
                      help="If set, loop over the input lines")

  parser.set_defaults(loop=False)
  args = parser.parse_args()

  print("Running GraffitiUpdater with:")
  print(f"Service   : {args.service}")
  print(f"Output    : {args.output}")
  print(f"Input     : {args.input}")
  print(f"Start Line: {args.line_index}")
  print(f"Looping   : {args.loop}")
  print(f"Search For: {args.search_for}")

  updater = Graffiti(args.service,
                     args.output,
                     args.input,
                     line_index=args.line_index,
                     loop=args.loop,
                     search_for=args.search_for)

  updater.start()
