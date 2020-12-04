import select
import systemd

service="prysmvalidator.service"

journal = systemd.journal.Reader()
journal.log_level(journal.LOG_INFO)
journal.add_match(_SYSTEMD_UNIT=service)
journal.seek_tail()
journal.get_previous()

poll = select.poll()
poll.register(journal, journal.get_events())

while poll.poll():
  if journal.process() != systemd.journal.APPEND:
    continue

  for entry in journal:
    print(entry)
