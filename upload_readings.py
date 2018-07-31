import csv
import datetime

from shelvd import db
from shelvd.models import Reading

# with open('readings_test.csv', 'r') as inputfile:
with open('readings.csv', 'r') as inputfile:
    for line in csv.reader(inputfile):
        reading = Reading()
        reading.id = line[0]
        reading.start_date = line[1]
        if line[2]:
            reading.end_date = line[2]
        if line[3] == "t":
            reading.ended = True
        else:
            reading.ended = False
        if line[4] == "t":
            reading.abandoned = True
        else:
            reading.abandoned = False
        if line[5]:
            reading.format = line[5]
        if line[6]:
            if line[6] == "no":
                reading.rereading = False
            else:
                reading.rereading = True
        reading.book_isbn = line[7]
        db.session.add(reading)
        db.session.commit()