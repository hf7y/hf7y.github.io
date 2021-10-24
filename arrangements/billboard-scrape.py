import requests
page = requests.get("https://www.billboard.com/charts/hot-100")

from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')

# chart=[]

# for li in soup.find_all('li', class_="chart-list__element"):
# 	information = [
# 		li.find(class_="chart-element__information__song").string,
# 		li.find(class_="chart-element__information__artist").string]
# 	chart.append(information)

catalog=[]
import csv
with open('noteflight.csv', newline='\n') as csv_file:
	csv_reader = csv.reader(csv_file)
	for row in csv_reader:
		catalog.append(row)

from dominate import document
from dominate.tags import *

# from fuzzywuzzy import fuzz

# def close_match(array1, array2):
# 	ratio0 = fuzz.token_set_ratio(array1[0], array2[0])
# 	ratio1 = fuzz.token_set_ratio(array1[1], array2[1])
# 	return ratio0 * ratio1 > 8000

# for entry in chart:
# 	for item in catalog:
# 		if close_match(entry, item):
# 			print(entry[0] + item[0])


# with document(title='Catalog') as doc:
# 	h1('Top 40')
# 	with table():
# 		with tr():
# 			th("Rank")
# 			th("Song")
# 			th("Artist")
# 			th("Score")

# 		for rank, entry in enumerate(chart, start=1):
# 			if rank <= 40:
# 				with tr():
# 					td(rank)
# 					td(entry[0])
# 					td(entry[1])

# 					with td():
# 						for item in catalog:
# 							if close_match(entry, item):
# 								a(item[3], href=item[2])
# 			if rank > 40:
# 				for item in catalog:
# 					if close_match(entry, item):
# 						with tr():
# 							td(rank)
# 							td(entry[0])
# 							td(entry[1])
# 							with td():
# 								a(item[3], href=item[2])

with document(title='Arrangements') as doc:
	script(type='text/javascript', src='sort.js')
	h1('Arrangements')
	with table():
		with thead():
			with tr():
				with th():
					a("Song", href="javascript:sort('song', true)")
				with th():
					a("Artist", href="javascript:sort('artist', true)")
				with th():
					a("Instrumentation", href="javascript:sort('instrumentation', false)")
		with tbody():
			for entry in catalog:
				with tr():
					td(entry[0],_class="song")
					td(entry[1],_class="artist")
					td(entry[3],_class="instrumentation")
					with td():
						a("score", href=entry[2])

f = open("index.html", "w")
f.write(doc.render())