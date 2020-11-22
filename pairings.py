import requests
import json
import re
from bs4 import BeautifulSoup
from chord import Chord

pairings = []
people = set()
with open('data.json') as data:
    data = json.load(data)
    for key, value in data.items():
        characters = value['characters']
        if any(isinstance(c, list) for c in value['characters']):
            for pair in characters:
                if isinstance(pair, list):
                    for i in range(len(pair)):
                        for j in range(i + 1, len(pair)):
                            pairings.append([pair[i], pair[j]])
                            people.add(pair[i])
                            people.add(pair[j])

        elif len(characters) == 2:
            for i in range(len(characters)):
                for j in range(i + 1, len(characters)):
                    pairings.append([characters[i], characters[j]])
                    people.add(characters[i])
                    people.add(characters[j])
people = list(people)
m = [[0 for i in range(len(people))] for j in range(len(people))]
for pair in pairings:
    i = people.index(pair[0])
    j = people.index(pair[1])
    m[i][j] = m[i][j] + 1
    m[j][i] = m[j][i] + 1
for x in range(len(m)):
    temp = [0 if a_ < 2000 else a_ for a_ in m[x]]
    m[x] = temp

filter_m = []
filter_people = []
delete_index = []
for index, i in enumerate(m):
    if any(v > 0 for v in i):
        filter_m.append(i)
        filter_people.append(people[index])
    elif all(v == 0 for v in i):
        delete_index.append(index)

for index in sorted(delete_index, reverse=True):
    for i in filter_m:
        del i[index]
Chord(filter_m, filter_people, width=2000).to_html()
