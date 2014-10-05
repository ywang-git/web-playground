#!/usr/bin/python3.3
from random import randint
username = ["jimmy", "voodoo", "ted", "josh", "captain", "cooper", "playmaster", "doug", "ak47", "iplay"]
statname = ["coins", "play hours", "player killed", "marbles", "magic points", "levels finished", "secret weapon", "gears", "achievments", "cards"]

query = 'curl -X POST -H "Content-Type: application/json" -d \'{"username" : "$username", "statname" : "$statname", "statvalue" : "$statvalue" }\' http://localhost:3000/LDRLY/sendStat'

for user in username:
	for stat in statname:
		value = randint(0, 100)
		q = query.replace("$username", user).replace("$statname", stat).replace("$statvalue", str(value))
		print(q)
		

