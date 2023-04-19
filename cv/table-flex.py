from bs4 import BeautifulSoup

files=[ "communities.partial", "dance.partial", "education.partial",
		"etc.partial", "film.partial", "installations.partial", "teaching.partial"]

renders=[]
for file in files:
	with open(file) as fp:
		soup = BeautifulSoup(fp, 'html.parser')

	ths=[]
	for th in soup.find_all('th'):
		ths.append(th.string.lower())

	soup.thead.decompose()
	soup.table.unwrap()
	soup.tbody.unwrap()
	for tr in soup.find_all('tr'):
		for index, td in enumerate(tr.find_all('td')):
			new_span = soup.new_tag("span", attrs={"class": ths[index]})
			new_span.contents = td.contents
			td.replace_with(new_span)
		new_div = soup.new_tag("div")
		new_div.contents = tr.contents
		tr.replace_with(new_div)

	renders.append(soup.prettify())

print(renders)

for index, file in enumerate(files):
	ff = open(file, "w")
	ff.write(renders[index])