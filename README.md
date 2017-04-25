# exchange-calendar-to-org

`exchange-calendar-to-org` is a small python script which syncs Microsoft Exchange calendar appointments to an org mode file.

It uses the [exchangelib](https://github.com/ecederstrand/exchangelib) library to retrieve the calendar events.

There is no support for syncing back to the Exchange calendar.

Each time it is run it overwrites the org mode file and it only syncs future events.
This is by design, appointments should be refiled to other org mode files for time tracking and archiving purposes.

## Setup

First copy the example config to a new config file:

`cp exchange-calendar-to-org.cfg.example exchange-calendar-to-org.cfg`

Next edit the configuration file:

`vim exchange-calendar-to-org.cfg`

The possible options are:

* `email`: The email address of the account to sync

* `password`: The password of the account to sync

* `sync_days`: The number of future days to sync

* `org_file`: The path to the org file to write the appointments in. Note this file is overwritten.

Next, install the requirements (ideally in a virtual environment):

`pip install -r requirements.txt`

Finally, run the script:

`python3 exchange-calendar-to-org.py`

This command can be scheduled to update the org mode file periodically.


