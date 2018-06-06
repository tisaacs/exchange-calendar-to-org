from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem, Message, \
    Mailbox, Attendee, Q
from exchangelib.folders import Calendar

import configparser
import html2text
import datetime
import os


def main():
    config_file_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'exchange-calendar-to-org.cfg')

    config = configparser.ConfigParser()
    config.read(config_file_path)

    email = config.get('Settings', 'email')
    try:
        server_url = config.get('Settings', 'server_url')
    except configparser.NoOptionError:
        server_url = None
    password = config.get('Settings', 'password')
    sync_days = int(config.get('Settings', 'sync_days'))
    org_file_path = config.get('Settings', 'org_file')
    tz_string = config.get('Settings', 'timezone_string')

    tz = EWSTimeZone.timezone(tz_string)

    credentials = Credentials(username=email, password=password)

    if server_url is None:
        account = Account(
            primary_smtp_address=email,
            credentials=credentials,
            autodiscover=True,
            access_type=DELEGATE)
    else:
        server = Configuration(server=server_url, credentials=credentials)
        account = Account(
            primary_smtp_address=email,
            config=server,
            autodiscover=False,
            access_type=DELEGATE)

    now = datetime.datetime.now()
    end = now + datetime.timedelta(days=sync_days)

    items = account.calendar.filter(
        start__lt=tz.localize(EWSDateTime(end.year, end.month, end.day)),
        end__gt=tz.localize(EWSDateTime(now.year, now.month, now.day)), )

    text = []
    text.append('* Calendar')
    text.append('\n')
    for item in items:
        text.append(get_item_text(item, tz))
        text.append('\n')

    f = open(org_file_path, 'w')
    f.write(''.join(text))


def get_item_text(item, tz):
    text = []
    text.append('** ' + item.subject)
    start_date = item.start.astimezone(tz)
    start_date_text = get_org_date(start_date)

    # If the end date is at midnight, the event is an all day event
    # so we subtract a minute so it doesn't cross the day boundary.
    # This stops it appearing under both days.
    end_date = item.end.astimezone(tz)
    if (end_date.hour == 0 and end_date.minute == 0):
        end_date = end_date - datetime.timedelta(minutes=1)

    end_date_text = get_org_date(end_date)
    text.append('<' + start_date_text + '>--<' + end_date_text + '>')
    if item.location is not None:
        text.append('Location: ' + item.location)
    if item.required_attendees is not None or item.optional_attendees is not None:
        text.append('Attendees:')

    if item.required_attendees is not None:
        for person in item.required_attendees:
            text.append('- ' + str(person.mailbox.name))

    if item.optional_attendees is not None:
        for person in item.optional_attendees:
            text.append('- ' + str(person.mailbox.name))

    if item.body is not None:
        text.append('')
        text.append('*** Information')
        text.append(html2text.html2text(item.body).replace('\n\n', '\n'))

    return '\n'.join(text)


def get_org_date(date):
    return date.strftime('%Y-%m-%d %a %H:%M')


if __name__ == '__main__':
    main()
