import csv

from shelvd import db
from shelvd.models import Author, Book

# with open('authors_test.csv', 'r') as inputfile:
with open('authors.csv', 'r') as inputfile:
	csv_reader = csv.reader(inputfile)
	for line in csv_reader:
		author = Author()
		author.id = 10000 + int(line[0])
		author.name = line[1]
		author.nationality = line[2]
		author.ethnicity = line[3]
		author.gender = line[4]
		db.session.add(author)
		db.session.commit()