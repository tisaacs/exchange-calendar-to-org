from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem, Message, \
    Mailbox, Attendee, Q
from exchangelib.folders import Calendar

import configparser
import html2text
import datetime
import os

def main():
    config_file_path = os.path.dirname(os.path.realpath(__file__)) + '\exchange-calendar-to-org.cfg'

    config = configparser.ConfigParser()
    config.read(config_file_path)

    email = config.get('Settings', 'email')
    password = config.get('Settings', 'password')
    sync_days = int(config.get('Settings', 'sync_days'))
    org_file_path = config.get('Settings', 'org_file')

    tz = EWSTimeZone.timezone('Europe/London')

    credentials = Credentials(username=email, password=password)

    account = Account(primary_smtp_address=email, credentials=credentials,
                    autodiscover=True, access_type=DELEGATE)

    now = datetime.datetime.now()
    end = now + datetime.timedelta(days=sync_days)

    items = account.calendar.filter(
        start__lt=tz.localize(EWSDateTime(end.year, end.month, end.day)),
        end__gt=tz.localize(EWSDateTime(now.year, now.month, now.day)),
    )

    text = []
    text.append('* Calendar')
    text.append('\n')
    for item in items:
        text.append(get_item_text(item))
        text.append('\n')

    f = open(org_file_path, 'w')
    f.write(''.join(text))

def get_item_text(item):
    text = []
    text.append('** ' + item.subject)
    text.append('<' + get_org_date(item.start) + '>--<' + get_org_date(item.end) + '>')
    if item.location != None:
        text.append('Location: ' + item.location)
    if item.required_attendees != None or item.optional_attendees != None:
        text.append('Attendees:')

    if item.required_attendees != None:
        for person in item.required_attendees:
            text.append('- ' + str(person.mailbox.name))

    if item.optional_attendees != None:
        for person in item.optional_attendees:
            text.append('- ' + str(person.mailbox.name))

    if item.body != None:
        text.append('')
        text.append('*** Information')
        text.append(html2text.html2text(item.body).replace('\n\n', '\n'))

    return '\n'.join(text)


def get_org_date(date):
    return date.strftime('%Y-%m-%d %a %H:%M')

if __name__ == '__main__':
    main()
