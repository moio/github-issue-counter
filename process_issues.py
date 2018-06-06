#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, datetime
from json_helpers import extract_datetime

# tweak here the names of the github org and repo to analyse
ORG = 'SUSE'
REPO = 'spacewalk'
FILENAME_ISSUES = ORG + 'issues.json'

one_day = datetime.timedelta(days=1)
now = datetime.datetime.now(datetime.timezone.utc)

f = open(FILENAME_ISSUES)
data = json.load(f)
f.close()

if REPO not in data.keys() and len(data[REPO]) == 0:
    raise SystemExit()

# convert all date strings to datetime objects
for i in data[REPO].keys():
    data[REPO][i]['created_at'] = extract_datetime(data[REPO][i]['created_at'])
    if data[REPO][i]['closed_at'] is not None:
        data[REPO][i]['closed_at'] = extract_datetime(data[REPO][i]['closed_at'])

# drop uninteresting issues
for i in list(data[REPO]):
    element = data[REPO][i]
    if element['is_pull_request'] or ('bug' not in element['labels']):
        del data[REPO][i]

# retrieve highest issue number
last_number = min([int(i) for i in data[REPO].keys()])
first_date = extract_datetime(data[REPO][str(last_number)]['created_at'])

day = datetime.datetime(first_date.year, first_date.month, first_date.day, tzinfo=datetime.timezone.utc)

result = {}

f = open('result.tsv', 'w')
f.write('date\tweek\topen_bugs\tclosed_bugs\n')

while day < now:
    key = day.strftime('%Y-%m-%d')
    print(key)

    week = day.strftime('%Y') + 'w%02d' % day.isocalendar()[1]
    open_issue_count = 0
    closed_issue_count = 0

    for i in data[REPO]:
        element = data[REPO][i]

        if element['created_at'] > day and element['created_at'] < (day + one_day):
            open_issue_count += 1

        if element['closed_at'] is not None:
            if element['closed_at'] > day and (element['closed_at'] < (day + one_day)):
                closed_issue_count += 1

    output = '%s\t%s\t%i\t%i'%(key, week, open_issue_count, closed_issue_count)

    f.write(output + '\n')

    day += one_day

f.close()
