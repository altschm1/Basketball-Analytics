from selenium import webdriver
import requests

#global variables
away_score = 0
home_score = 0

def get_content_from_webpage(browser, url):
	"""returns a string of content from a chosen webpage
	
	browser: the chromedriver from Selenium
	url: the url for webpage to parse (string)"""
	
	#navigate to the proper url
	browser.get(url)
	
	#returns HTML from the browser
	html = browser.execute_script("return document.body.innerHTML")
	
	return html
	
def find_date(html):
	"""returns the date that the game took place
	
	html: the html code string to be parsed"""
	
	html_split = html.split("\n")
	for line in html_split:
		if line.find("game-summary__date") != -1:
			date = get_content_inside_tags(line, "div")
			
			#append month
			result = ''
			if date.find("Jan") != -1:
				result = "01/"
			elif date.find("Feb") != -1:
				result = "02/"
			elif date.find("Mar") != -1:
				result = "03/"
			elif date.find("Apr") != -1:
				result = "04/"
			elif date.find("May") != -1:
				result = "05/"
			elif date.find("Jun") != -1:
				result = "06/"
			elif date.find("Jul") != -1:
				result = "07/"
			elif date.find("Aug") != -1:
				result = "08/"
			elif date.find("Sep") != -1:
				result = "09/"
			elif date.find("Oct") != -1:
				result = "10/"
			elif date.find("Nov") != -1:
				result = "11/"
			elif date.find("Dec") != -1:
				result = "12/"
			
			#append day
			date_splits = date.split(",")
			temp = date_splits[0]
			if temp[-2] == ' ':
				result = result + "0" + temp[-1] + "/"
			else:
				result = result + temp[-2:] + "/"
			
			#append year
			date_splits = date.split(" ")
			result = result + date_splits[-1]
			
			return result
	
def setup_game_details(game_id, html):
	"""returns the following format of data from an individual game:
	[GAME_ID = ], INFO, [DATE = ], [AWAY = ], [HOME = ]
	[GAME_ID = ], PLAYERS: STARTER, [TEAM], [PLAYER1], [PLAYER2], [PLAYER3], [PLAYER4], [PLAYER5]
	[GAME_ID = ], PLAYERS: STARTER, [TEAM], [PLAYER1], [PLAYER2], [PLAYER3], [PLAYER4], [PLAYER5]
	[GAME_ID = ], PLAYERS: BENCH, [TEAM], [PLAYER1], [PLAYER2], [PLAYER3], [PLAYER4], [PLAYER5]...
	[GAME_ID = ], PLAYERS: BENCH, [TEAM], [PLAYER1], [PLAYER2], [PLAYER3], [PLAYER4], [PLAYER5]...
	and also returns the away team, the home team, away starters, and home starters, away bench, home bench
	
	game_id: game id from nba.com
	html: string from which following data will be parsed"""
	
	#setup DATE info
	date = find_date(html)

	#setup away and home team
	away, home = find_teams_playing(html)
	
	#setup starters for both team
	away_starters = find_starters(html, False)
	home_starters = find_starters(html, True)
	
	#setup bench for both teams
	away_bench = find_bench(html, False)
	home_bench = find_bench(html, True)
	
	return away, home, away_starters, home_starters, away_bench, home_bench, date
	
def find_teams_playing(html):
	"""returns two strings: the away team abbreviation, the home team abbreviation
	
	html: string from which following data will be parsed"""
	
	teams = []
	
	#find the teams
	if html.find("ATL ") != -1:
		teams.append("ATL")
	if html.find("BKN ") != -1:
		teams.append("BKN")
	if html.find("BOS ") != -1:
		teams.append("BOS")
	if html.find("CHA ") != -1:
		teams.append("CHA")
	if html.find("CHI ") != -1:
		teams.append("CHI")
	if html.find("CLE ") != -1:
		teams.append("CLE")
	if html.find("DAL ") != -1:
		teams.append("DAL")
	if html.find("DEN ") != -1:
		teams.append("DEN")
	if html.find("DET ") != -1:
		teams.append("DET")
	if html.find("GSW ") != -1:
		teams.append("GSW")
	if html.find("HOU ") != -1:
		teams.append("HOU")
	if html.find("IND ") != -1:
		teams.append("IND")
	if html.find("LAC ") != -1:
		teams.append("LAC")
	if html.find("LAL ") != -1:
		teams.append("LAL")
	if html.find("MEM ") != -1:
		teams.append("MEM")
	if html.find("MIA ") != -1:
		teams.append("MIA")
	if html.find("MIL ") != -1:
		teams.append("MIL")
	if html.find("MIN ") != -1:
		teams.append("MIN")
	if html.find("NOP ") != -1:
		teams.append("NOP")
	if html.find("NYK ") != -1:
		teams.append("NYK")
	if html.find("OKC ") != -1:
		teams.append("OKC")
	if html.find("ORL ") != -1:
		teams.append("ORL")
	if html.find("PHI ") != -1:
		teams.append("PHI")
	if html.find("PHX ") != -1:
		teams.append("PHX")
	if html.find("POR ") != -1:
		teams.append("POR")
	if html.find("SAC ") != -1:
		teams.append("SAC")
	if html.find("SAS ") != -1:
		teams.append("SAS")
	if html.find("TOR ") != -1:
		teams.append("TOR")
	if html.find("UTA ") != -1:
		teams.append("UTA")
	if html.find("WAS ") != -1:
		teams.append("WAS")
		
	#determine which is the home team and away team
	if html.find(teams[0] + " vs " + teams[1]) != -1: 
		away_team = teams[0]
		home_team = teams[1]
	elif html.find(teams[1] + " vs " + teams[0]) != -1: 
		away_team = teams[1]
		home_team = teams[0]
	else:
		raise RuntimeError('Could not determine who was the home or away team')
	
	return away_team, home_team

def find_starters(html, home):
	"""returns a list of the 5 starters
	
	html - a string of the content to be parsed
	home - bool True, if looking for home starters"""
	
	starters = set()
	
	#based on whether the team is home or away determines the starting point
	if not home:
		first_index = html.find("PLUS_MINUS")
	else:
		first_index = html.rfind("PLUS_MINUS")
	
	cut_content = html[first_index:]
	cut_content_splits = cut_content.split("\n")
	
	#search for 5 starters
	i = 0
	for line in cut_content_splits:
		#if we found a player's field name
		if line.find('class="player"') != -1 and line.find('data-field="PLAYER_NAME"') != -1:
			
			player_info = get_content_inside_tags(line, "a")
			player_split = player_info.split(" ")
			
			#if player only has last name
			if player_split[1].find("<sup>") != -1:
				player_first_name = ''
				player_last_name = player_split[0]
			#player has first and last name
			else:
				player_first_name = player_split[0]
				player_last_name = player_split[1]
				
			#get rid of any special characters
			player_first_name = player_first_name.replace("&#146;", "'")
			player_last_name = player_last_name.replace("&#146;", "'")
			
			player_name = player_first_name + " " + player_last_name
			if len(get_content_inside_tags(player_info, "sup")) != 0:
				starters.add(player_name)
			
			if len(starters) >= 5:
				return list(starters)

def find_bench(html, home):
	"""returns a list of the bench players
	
	html - a string of the content to be parsed
	home - bool True, if looking for home starters"""
	
	bench = set()
	
	#based on whether the team is home or away determines the starting point
	if not home:
		first_index = html.find("PLUS_MINUS")
		last_index = html.rfind("PLUS_MINUS")
	else:
		first_index = html.rfind("PLUS_MINUS")
		last_index = len(html)
	
	cut_content = html[first_index:last_index]
	cut_content_splits = cut_content.split("\n")
	
	#search for 5 starters
	for line in cut_content_splits:
		#if we found a player's field name
		if line.find('class="player"') != -1 and line.find('data-field="PLAYER_NAME"') != -1:
			
			player_info = get_content_inside_tags(line, "a")
			player_split = player_info.split(" ")
			
			#if player only has last name
			if player_split[1].find("<sup>") != -1:
				player_first_name = ''
				player_last_name = player_split[0]
			#player has first and last name
			else:
				player_first_name = player_split[0]
				player_last_name = player_split[1]
				
			player_name = player_first_name + " " + player_last_name
			bench.add(player_name)
			
	return list(bench)

def get_content_inside_tags(line, tag):
	"""returns the content inside <tag>content</tag>
	
	line - a string to be parsed
	tag - a special character such as a, td, div, etc"""
	
	first_index = line.find("<" + tag)
	last_index = line.find("</" + tag)
	
	cut = line[first_index:last_index]
	
	first_index = cut.find(">")
	
	content = cut[first_index + 1:]
	
	return content
	
def parse_shot(game_id, date, away, home, away_on_court, home_on_court, event):
	"""returns a string of the form:
	GAME_ID:a,AWAY:b,HOME:c,AWAY_LINEUP:a;b;c;d;e,HOME_LINEUP:a;b;c;d;e,AWAY_SCORE:a,HOME_SCORE:b,PLAY_TYPE:SHOT,TEAM_SHOOTING:x,PLAYER_SHOOTING:x,SHOT_DISTANCE:y,SHOT_TYPE:z,MADE:T/F,AST:T/F/MISSED,PASSER:x"
	
	game_id - game id
	away - away team abbrv
	home - home team abbrv
	away_on_court - lineup of away team
	home_on_court - lineup of home team
	event - list of form event[0] = SHOT event[1] = SHOT DETAILS, event[2] = BLK DETAILS, event[3] = REB DETAILS"""
	
	result = ''
	
	#append game_id
	result = result + "GAME_ID:" + game_id + ","
	
	#append date
	result = result + "DATE:" + date + ","
	
	#append away team and home team
	result = result + "AWAY:" + away + ",HOME:" + home + ","
	
	#append away lineup
	result = result + "AWAY_LINEUP:"
	for player in away_on_court:
		result = result + player
		if player != away_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append home lineup
	result = result + "HOME_LINEUP:"
	for player in home_on_court:
		result = result + player
		if player != home_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append away_score and home_score
	global away_score
	global home_score
	result = result + "AWAY_SCORE:" + str(away_score) + ","
	result = result + "HOME_SCORE:" + str(home_score) + ","
	
	int(away_score)
	int(home_score)
	
	#append play type
	result = result + "PLAY_TYPE:SHOT,"
	
	#append team shooting
	result = result + "TEAM_SHOOTING:"
	if event[1].find("{" + home + "}") != -1:
		result = result + home + ","
	else:
		result = result + away + ","
	
	#append player shooting
	line_splits = event[1].split(" ")
	if line_splits[1] == "MISS":
		if line_splits[2][-1] == ".":
			first_name_letter = line_splits[2][0]
			last_name = line_splits[3]
		else:
			first_name_letter = None
			last_name = line_splits[2]
	else:
		if line_splits[1][-1] == ".":
			first_name_letter = line_splits[1][0]
			last_name = line_splits[2]
		else:
			first_name_letter = None
			last_name = line_splits[1]
	player_shooting = ''
	
	if event[1].find("{" + home + "}") != -1:
		for player in home_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_shooting = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_shooting = player
				break
	else:
		for player in away_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_shooting = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_shooting = player
				break
	result = result + "PLAYER_SHOOTING:" + player_shooting + ","
	
	#append shot_distance
	distance = '0'
	if event[1].find("3PT") != -1:
		distance = "3PT"
	else:
		for i in line_splits:
		
			if len(i) > 1 and i[-1] == "'":
				distance = i[0:len(i) - 1]
	result = result + "SHOT_DISTANCE:" + distance + ","
	
	#append shot type
	if event[1].find("3PT") != -1:
		starting_index = event[1].find("3PT") + 4
	else:
		num_distance = int(distance)
		if num_distance < 10:
			starting_index = event[1].find(distance + "'") + 3
		else:
			starting_index = event[1].find(distance + "'") + 4
		
	if event[1].find("(") != -1:
		end_index = event[1].find("(") - 1
	else:
		end_index = len(event[1])
		
	shot_type = event[1][starting_index:end_index]
	result = result + "SHOT_TYPE:" + shot_type + ","
	
	#append 3PM
	if event[1].find("3PT") != -1:
		three_pointer = "T"
	else:
		three_pointer = "F"
	result = result + "3PT:" + three_pointer + ","
	
	#append made
	if event[1].find("MISS") != -1:
		made_shot = "F"
	else:
		made_shot = "T"
	result = result + "MADE:" + made_shot +  ","
	
	#append assisted
	assisted = "F"
	if made_shot == "T":
		if event[1].find("AST")!= -1:
			assisted = "T"
		elif event[1].find("AST") == -1:
			assisted = "F"	
		result = result + "AST:" + assisted + ","
	
	#append passer
	if made_shot == "T" and assisted == "T":
		#find last parentheses of assists
		last_index = event[1].rfind(")")
		first_index = event[1].rfind("(") + 1
		
		substring = event[1][first_index:last_index]
		
		#find first initial and last name
		substring_splits = substring.split(" ")
		passer = ''
		if substring_splits[0][-1] == ".":
			first_name_letter = substring_splits[0][0]
			last_name = substring_splits[1]
		else:
			first_name_letter = None
			last_name = substring_splits[0]
		
		if event[1].find("{" + home + "}") != -1:
			for player in home_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						passer = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						passer = player
					break
		else:
			for player in away_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						passer = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						passer = player
					break
		result = result + "PASSER:" + passer + ","
	
	#append blocker and team blocking if any
	if event[2] is not None:
		#if home team, append home team
		if event[1].find("{" + home + "}") != -1:
			result = result + "TEAM_BLOCKING:" + home + ","
		#if away team, append away team
		else:
			result = result + "TEAM_BLOCKING:" + away + ","
			
		#append player blocking the shot
		
		#find first initial and last name
		event_two_splits = event[2].split(" ")
		blocker = ''
		if event_two_splits[1][-1] == ".":
			first_name_letter = event_two_splits[1][0]
			last_name = event_two_splits[2]
		else:
			first_name_letter = None
			last_name = event_two_splits[1]
		
		
		if event[2].find("{" + home + "}") != -1:
			for player in home_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						blocker = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						blocker = player
					break
		else:
			for player in away_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						blocker = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						blocker = player
					break
		result = result + "BLOCK:" + blocker + ","
		
	
	#append rebounder, rebound type, and team rebounding if any
	if event[3] is not None:
		#if home team, append home team
		if event[3].find("{" + home + "}") != -1:
			result = result + "TEAM_REBOUNDING:" + home + ","
		#if away team, append away team
		else:
			result = result + "TEAM_REBOUNDING:" + away + ","
		
		#append player rebounding the shot
		
		#find first initial and last name
		event_three_splits = event[3].split(" ")
		rebounder = ''
		if event_three_splits[1][-1] == ".":
			first_name_letter = event_three_splits[1][0]
			last_name = event_three_splits[2]
		else:
			first_name_letter = None
			last_name = event_three_splits[1]
		
		
		if event[3].find("{" + home + "}") != -1:
			for player in home_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						rebounder = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						rebounder = player
					break
		else:
			for player in away_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						rebounder = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						rebounder = player
					break
		result = result + "REBOUND:" + rebounder + ","
		
		#append rebound type
		if event[1].find("{" + home + "}") != -1:
			if event[3].find("{" + home + "}") != -1:
				rebound_type = "OFF"
			else:
				rebound_type = "DEF"
		else:
			if event[3].find("{" + home + "}") != -1:
				rebound_type = "DEF"
			else:
				rebound_type = "OFF"
		result = result + "REBOUND_TYPE:" + rebound_type + ","
	
	result = result + "\n"
	
	#update home_score and away_score
	if event[1].find("MISS") == -1:
		if event[1].find("3PT") != -1 and event[1].find("{" + home + "}") != -1:
			home_score = home_score + 3
		elif event[1].find("3PT") != -1 and event[1].find("{" + away + "}") != -1:
			away_score = away_score + 3
		elif event[1].find("3PT") == -1 and event[1].find("{" + home + "}") != -1:
			home_score = home_score + 2
		elif event[1].find("3PT") == -1 and event[1].find("{" + away + "}") != -1:
			away_score = away_score + 2
	
	return result

def parse_turnover(game_id, date, away, home, away_on_court, home_on_court, event):
	"""returns a string of the form:
	GAME_ID:a,AWAY:b,HOME:c,AWAY_LINEUP:a;b;c;d;e,HOME_LINEUP:a;b;c;d;e,AWAY_SCORE:a,HOME_SCORE:b,PLAY_TYPE:TO,TEAM_TO:x,PLAYER_TO:x,TURNOVER_TYPE:y,TEAM_STL:y,PLAYER_STL:y"
	
	game_id - game id
	away - away team abbrv
	home = home team abbrv
	away_on_court - lineup of away team
	home_on_court - lineup of home team
	event - list, 1st element is TO, 2nd element is TO info, 3rd element is STL info if any"""
	
	result = ''
	
	#append game_id
	result = result + "GAME_ID:" + game_id + ","
	
	#append date
	result = result + "DATE:" + date + ","
	
	#append away team and home team
	result = result + "AWAY:" + away + ",HOME:" + home + ","
	
	#append away lineup
	result = result + "AWAY_LINEUP:"
	for player in away_on_court:
		result = result + player
		if player != away_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append home lineup
	result = result + "HOME_LINEUP:"
	for player in home_on_court:
		result = result + player
		if player != home_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append away_score and home_score
	global away_score
	global home_score
	result = result + "AWAY_SCORE:" + str(away_score) + ","
	result = result + "HOME_SCORE:" + str(home_score) + ","
	
	int(away_score)
	int(home_score)
	
	#append play type
	result = result + "PLAY_TYPE:TO,"
	
	#append team turning over
	result = result + "TEAM_TO:"
	if event[1].find("{" + home + "}") != -1:
		result = result + home + ","
	else:
		result = result + away + ","
	
	#append player turning it over
	line_splits = event[1].split(" ")
	if line_splits[1][-1] == ".":
		first_name_letter = line_splits[1][0]
		last_name = line_splits[2]
	else:
		first_name_letter = None
		last_name = line_splits[1]
		
	player_to = ''
	
	if event[1].find("{" + home + "}") != -1:
		for player in home_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_to = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_to = player
				break
	else:
		for player in away_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_to = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_to = player
				break
	result = result + "PLAYER_TO:" + player_to + ","
	
	#append turnover type
	turnover_type = ''
	if event[1].find("Shot Clock") != -1:
		turnover_type = "Shot Clock"
	else:
		#has a first initial and Jr.
		if line_splits[0].find(".") != -1 and line_splits[2].find(".") != -1:
			first_index = event[1].find(line_splits[4])
		#has a first initial and no Jr.
		elif line_splits[0].find(".") != -1 and line_splits[2].find(".") == -1:
			first_index = event[1].find(line_splits[3])
		#has no first initial and Jr.
		elif line_splits[0].find(".") == -1 and line_splits[2].find(".") != -1:
			first_index = event[1].find(line_splits[3])
		#has no first initial and no Jr.
		else:
			first_index = event[1].find(line_splits[2])
		
		last_index = event[1].rfind("Turnover") - 1
		
		turnover_type = event[1][first_index:last_index]
	result = result + "TO_TYPE:" + turnover_type + ","
	
	#append team stealing and player stealing if any
	if event[2] is not None:
		#append team stealing
		result = result + "TEAM_STL:"
		if event[2].find("{" + home + "}") != -1:
			result = result + home + ","
		else:
			result = result + away + ","

		#append player stealing
		line_splits = event[2].split(" ")
		if line_splits[1][-1] == ".":
			first_name_letter = line_splits[1][0]
			last_name = line_splits[2]
		else:
			first_name_letter = None
			last_name = line_splits[1]
		
		#append player getting steal
		player_stl = ''
		
		if event[2].find("{" + home + "}") != -1:
			for player in home_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						player_stl = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						player_stl = player
					break
		else:
			for player in away_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						player_stl = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						player_stl = player
					break
		result = result + "PLAYER_STL:" + player_stl + ","
	
	result = result + "\n"

	return result

def update_lineups(away, home, away_on_court, away_on_bench, home_on_court, home_on_bench, event):
	"""updates players on court
	away - away team
	home - home team
	away_on_court - list of 5 players currently on court for away team
	home_on_court - list of 5 players currently on court for home team
	away_on_bench - list of away starters and bench players
	home_on_bench - list of home starters and bench players
	event - event[0] is SUB, event[1] is players swapping
	"""
	#if it's a sub at the start of a period
	if event[1].find("Period") != -1:
		starting_index = event[1].find(":") + 1
		players = event[1][starting_index:].split("/")
		if event[1].find("{" + home + "}") != -1:
			i = 0
			for i in range(5):
				home_on_court[i] = players[i]
		else:
			i = 0
			for i in range(5):
				away_on_court[i] = players[i]

	#if a sub during the game
	else:
		#find indexes of name of player coming in
		player_coming_in_first_index = event[1].find("SUB:") + 5
		player_coming_in_last_index = event[1].find("FOR") - 1

		#find indexes of name of player coming out
		player_coming_out_first_index = event[1].find("FOR") + 4
		player_coming_out_last_index = len(event[1])
		
		#get name of players and split by spaces
		player_in_substring = event[1][player_coming_in_first_index:player_coming_in_last_index]
		player_out_substring = event[1][player_coming_out_first_index:player_coming_out_last_index]
		player_in_splits = player_in_substring.split(" ")
		player_out_splits = player_out_substring.split(" ")
		
		#find first name and last name of player coming in
		if player_in_splits[0][-1] == ".":
			first_name_in = player_in_splits[0][0]
			last_name_in = player_in_splits[1]
		else:
			first_name_in = None
			last_name_in = player_in_splits[0]
		
		#find first name and last name of player coming out
		if player_out_splits[0][-1] == ".":
			first_name_out = player_out_splits[0][0]
			last_name_out = player_out_splits[1]
		else:
			first_name_out = None
			last_name_out = player_out_splits[0]
		
		player_on = ''
		
		#if substition is made by home team
		if event[1].find("{" + home + "}") != -1:
			#find player coming on
			for player in home_on_bench:
				
				if player.find(last_name_in) != -1:
					if first_name_in is not None and first_name_in == player[0]:
						player_on = player
					elif first_name_in is not None and first_name_in != player[0]:
						continue
					else:
						player_on = player
					break
			
			#find player coming off
			i = 0
			for i in range(5):
				if home_on_court[i].find(last_name_out) != -1:
					if first_name_out is not None and first_name_out == home_on_court[i][0]:
						home_on_court[i] = player_on
					elif first_name_out is not None and first_name_out != home_on_court[i][0]:
						i = i + 1
						continue
					else:
						home_on_court[i] = player_on
					break
				i = i + 1
		
		#if substition is made by away team
		else:
			#find player coming on
			index_on = 0
			for player in away_on_bench:
				if player.find(last_name_in) != -1:
					if first_name_in is not None and first_name_in == player[0]:
						player_on = player
					elif first_name_in is not None and first_name_in != player[0]:
						continue
					else:
						player_on = player
					break
			
			#find player coming off
			i = 0
			for i in range(5):
				if away_on_court[i].find(last_name_out) != -1:
					if first_name_out is not None and first_name_out == away_on_court[i][0]:
						away_on_court[i] = player_on
					elif first_name_out is not None and first_name_out != away_on_court[i][0]:
						i = i + 1
						continue
					else:
						away_on_court[i] = player_on
					break
				i = i + 1

def parse_free_throw(game_id, date, away, home, away_on_court, home_on_court, event):
	"""returns a string of the form:
	GAME_ID:a,AWAY:b,HOME:c,AWAY_LINEUP:a;b;c;d;e,HOME_LINEUP:a;b;c;d;e,AWAY_SCORE:a,HOME_SCORE:b,PLAY_TYPE:FT,TEAM_FT:x,PLAYER_FT:x,MADE:T/F,ATTEMPT:X of Y,REBOUND_TEAM:,REBOUND_PLAYER:
	game_id - game id
	away - away team abbrv
	home = home team abbrv
	away_on_court - lineup of away team
	home_on_court - lineup of home team
	event - list, 1st element is TO, 2nd element is FT info, 3rd element is REB info if any"""
	
	result = ''
	
	#append game_id
	result = result + "GAME_ID:" + game_id + ","
	
	#append date
	result = result + "DATE:" + date + ","
	
	#append away team and home team
	result = result + "AWAY:" + away + ",HOME:" + home + ","
	
	#append away lineup
	result = result + "AWAY_LINEUP:"
	for player in away_on_court:
		result = result + player
		if player != away_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append home lineup
	result = result + "HOME_LINEUP:"
	for player in home_on_court:
		result = result + player
		if player != home_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append away_score and home_score
	global away_score
	global home_score
	result = result + "AWAY_SCORE:" + str(away_score) + ","
	result = result + "HOME_SCORE:" + str(home_score) + ","
	
	int(away_score)
	int(home_score)
	
	#append play type
	result = result + "PLAY_TYPE:FT,"
	
	#append team shooting free throws
	result = result + "TEAM_FT:"
	if event[1].find("{" + home + "}") != -1:
		result = result + home + ","
	else:
		result = result + away + ","
	
	#append player shooting ft
	line_splits = event[1].split(" ")
	if line_splits[1] == "MISS":
		if line_splits[2][-1] == ".":
			first_name_letter = line_splits[2][0]
			last_name = line_splits[3]
		else:
			first_name_letter = None
			last_name = line_splits[2]
	else:
		if line_splits[1][-1] == ".":
			first_name_letter = line_splits[1][0]
			last_name = line_splits[2]
		else:
			first_name_letter = None
			last_name = line_splits[1]
	player_shooting = ''
	
	if event[1].find("{" + home + "}") != -1:
		for player in home_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_shooting = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_shooting = player
				break
	else:
		for player in away_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_shooting = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_shooting = player
				break
	result = result + "PLAYER_FT:" + player_shooting + ","
	
	#append if made or miss
	if event[1].find("MISS") != -1:
		made = 'F'
	else:
		made = 'T'
	result = result + "MADE:" + made + ","
	
	#append which attempt of how many
	index_start = event[1].rfind(" of ") - 1
	index_end = event[1].rfind(" of ") + 5
	if index_start == -2:
		attempt = 'Technical'
	else:
		attempt = event[1][index_start:index_end]
	result = result + "ATTEMPT:" + attempt + ","
	
	#append rebounder, rebound type, and team rebounding if any
	if event[2] is not None:
		#if home team, append home team
		if event[2].find("{" + home + "}") != -1:
			result = result + "TEAM_REBOUNDING:" + home + ","
		#if away team, append away team
		else:
			result = result + "TEAM_REBOUNDING:" + away + ","
		
		#append player rebounding the shot
		
		#find first initial and last name
		event_three_splits = event[2].split(" ")
		rebounder = ''
		if event_three_splits[1][-1] == ".":
			first_name_letter = event_three_splits[1][0]
			last_name = event_three_splits[2]
		else:
			first_name_letter = None
			last_name = event_three_splits[1]
		
		
		if event[2].find("{" + home + "}") != -1:
			for player in home_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						rebounder = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						rebounder = player
					break
		else:
			for player in away_on_court:
				if player.find(last_name) != -1:
					if first_name_letter is not None and first_name_letter == player[0]:
						rebounder = player
					elif first_name_letter is not None and first_name_letter != player[0]:
						continue
					else:
						rebounder = player
					break
		result = result + "REBOUND:" + rebounder + ","
		
		#append rebound type
		if event[1].find("{" + home + "}") != -1:
			if event[2].find("{" + home + "}") != -1:
				rebound_type = "OFF"
			else:
				rebound_type = "DEF"
		else:
			if event[2].find("{" + home + "}") != -1:
				rebound_type = "DEF"
			else:
				rebound_type = "OFF"
		result = result + "REBOUND_TYPE:" + rebound_type + ","
	
	result = result + "\n"
	
	#update home_score and away_score
	if event[1].find("MISS") == -1:
		if event[1].find("{" + home + "}") != -1:
			home_score = home_score + 1
		else:
			away_score = away_score + 1
	
	return result
	
def find_nth(string, substring, n):
	"""find nth occurence of string in a substring
	string - giant string
	substring - string being searched
	n - which occurence of substring"""
	
	if (n == 1):
		return string.find(substring)
	else:
		return string.find(substring, find_nth(string, substring, n - 1) + 1)
	
def find_lineup(team, content, period):
	"""returns a list of the names of players starting each quarter
	team - either AWAY or HOME
	content - html from popcornmachine
	period - which period to be searching for"""
	
	#for overtime periods
	if period >= 5:
		#if team is away, look for 1st, 2nd, 3rd, 4th, and 5th occurrence of string
		if team == "AWAY":
			range = [1, 2, 3, 4, 5]
		#if team is home, look for 6th, 7th, 8th, 9th, and 10th occurrence of string
		else:
			range = [6, 7, 8, 9, 10]
		
		result = []
		
		for i in range:
			index = find_nth(content, "Period " + str(period) + "&nbsp;&nbsp;5:00", i)
			
			last_index = index - 12
			first_index = content.find("text1", last_index - 50) + 7
			
			#append player's name 
			result.append(content[first_index:last_index])
		
		return result
	#for regular quarter periods	
	else:	
		result = []
				
		#if team away, find first occurence
		if team == "AWAY":
			index = content.find("Period " + str(period) + " 12:00")
		#if team home, find last occurence
		else:
			index = content.rfind("Period " + str(period) + " 12:00")
		
		starting_index = index - 15
		
		data = get_content_inside_tags(content[starting_index:], "p")
		
		#get 5 players split by <br>
		data_splits = data.split("<br>")
		
		result.append(data_splits[-1])
		result.append(data_splits[-2])
		result.append(data_splits[-3])
		result.append(data_splits[-4])
		result.append(data_splits[-5])
		
		return result

def insert_substitions(date, away, home, list_of_events, plays_per_qtr):
	"""this will insert substition events into list_of_events so that all lineups are correct at the start of each period
	date - date of game
	away - away team
	home - home team
	list_of_events - all the list of events
	plays_per_qtr - the number of plays per quarter"""
	
	#get proper url from popcorn machine
	date_splits = date.split("/")
	if away == "UTA":
		away_team = "UTH"
	elif away == "NOP":
		away_team = "NOR"
	elif away == "PHX":
		away_team = "PHO"
	else:
		away_team = away
	if home == "UTA":
		home_team = "UTH"
	elif home == "NOP":
		home_team = "NOR"
	elif home == "PHX":
		home_team = "PHO"
	else:
		home_team = home
	url = "http://popcornmachine.net/gf?date=" + date_splits[2] + date_splits[0] + date_splits[1] + "&game=" + away_team + home_team
	#get content from website
	r = requests.get(url)
	content = r.content
	content = str(content)
	away_lineup_qtr = []
	home_lineup_qtr = []
	
	#find lineup for quarter 2
	away_lineup_qtr.append(find_lineup("AWAY", content, 2))
	home_lineup_qtr.append(find_lineup("HOME", content, 2))
	
	#find lineup for quarter 3
	away_lineup_qtr.append(find_lineup("AWAY", content, 3))
	home_lineup_qtr.append(find_lineup("HOME", content, 3))
	
	#find lineup for quarter 4
	away_lineup_qtr.append(find_lineup("AWAY", content, 4))
	home_lineup_qtr.append(find_lineup("HOME", content, 4))
	
	#if there was OT1
	if plays_per_qtr[4] != 0:
		#find lineup for quarter 5
		away_lineup_qtr.append(find_lineup("AWAY", content, 5))
		home_lineup_qtr.append(find_lineup("HOME", content, 5))
	#if there was OT2
	if plays_per_qtr[5] != 0:
		#find lineup for quarter 6
		away_lineup_qtr.append(find_lineup("AWAY", content, 6))
		home_lineup_qtr.append(find_lineup("HOME", content, 6))
	#if there was OT3
	if plays_per_qtr[6] != 0:
		#find lineup for quarter 7
		away_lineup_qtr.append(find_lineup("AWAY", content, 7))
		home_lineup_qtr.append(find_lineup("HOME", content, 7))
	#if there was OT4
	if plays_per_qtr[7] != 0:
		#find lineup for quarter 8
		away_lineup_qtr.append(find_lineup("AWAY", content, 8))
		home_lineup_qtr.append(find_lineup("HOME", content, 8))
	#if there was OT5
	if plays_per_qtr[8] != 0:
		#find lineup for quarter 9
		away_lineup_qtr.append(find_lineup("AWAY", content, 9))
		home_lineup_qtr.append(find_lineup("HOME", content, 9))
	#if there was OT6
	if plays_per_qtr[9] != 0:
		#find lineup for quarter 10
		away_lineup_qtr.append(find_lineup("AWAY", content, 10))
		home_lineup_qtr.append(find_lineup("HOME", content, 10))
	
	#create set of commands
	away_events = []
	period = 2
	for lineup in away_lineup_qtr:
		event = "{" + away + "} SUB Period " + str(period) + ":"
		for player in lineup:
			if player.find(" ") == -1:
				player_splits = ['', player]
			else:
				player_splits = player.split(" ")
			event = event + player_splits[0] + " " + player_splits[1] + "/"
		away_events.append(event)
		period = period + 1
	
	home_events = []
	period = 2
	for lineup in home_lineup_qtr:
		event = "{" + home + "} SUB Period " + str(period) + ":"
		for player in lineup:
			if player.find(" ") == -1:
				player_splits = ['', player]
			else:
				player_splits = player.split(" ")
			event = event + player_splits[0] + " " + player_splits[1] + "/"
		home_events.append(event)
		period = period + 1
	
	#add command for sub at start of each quarter
	indices = []
	curr_postition = 0
	for plays in plays_per_qtr:
		if plays != 0:
			curr_postition = curr_postition + plays
			indices.append(curr_postition)
	
	i = -2
	away_events.reverse()
	home_events.reverse()
	for event_away, event_home in zip(away_events, home_events):
		list_of_events.insert(indices[i], event_away)
		list_of_events.insert(indices[i], event_home)
		i = i - 1
	
def parse_foul(game_id, date, away, home, away_on_court, home_on_court, event):
	"""returns a string of the form:
	GAME_ID:a,AWAY:b,HOME:c,AWAY_LINEUP:a;b;c;d;e,HOME_LINEUP:a;b;c;d;e,AWAY_SCORE:a,HOME_SCORE:b,PLAY_TYPE:FT,TEAM_FT:x,PLAYER_FT:x,MADE:T/F,ATTEMPT:X of Y,REBOUND_TEAM:,REBOUND_PLAYER:
	game_id - game id
	date - time the game took place
	away - away team abbrv
	home = home team abbrv
	away_on_court - lineup of away team
	home_on_court - lineup of home team
	event - list, 1st element is TO, 2nd element is FT info, 3rd element is REB info if any"""
	
	result = ''
	
	#append game_id
	result = result + "GAME_ID:" + game_id + ","
	
	#append date
	result = result + "DATE:" + date + ","
	
	#append away team and home team
	result = result + "AWAY:" + away + ",HOME:" + home + ","
	
	#append away lineup
	result = result + "AWAY_LINEUP:"
	for player in away_on_court:
		result = result + player
		if player != away_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append home lineup
	result = result + "HOME_LINEUP:"
	for player in home_on_court:
		result = result + player
		if player != home_on_court[-1]:
			result = result + ";"
	result = result + ","
	
	#append away_score and home_score
	global away_score
	global home_score
	result = result + "AWAY_SCORE:" + str(away_score) + ","
	result = result + "HOME_SCORE:" + str(home_score) + ","
	
	int(away_score)
	int(home_score)
	
	#append play type
	result = result + "PLAY_TYPE:FOUL,"
	
	#append team committing foul
	result = result + "TEAM_FOUL:"
	if event[1].find("{" + home + "}") != -1:
		result = result + home + ","
	else:
		result = result + away + ","
	
	#append player committing foul
	line_splits = event[1].split(" ")
	if line_splits[1][-1] == ".":
		first_name_letter = line_splits[1][0]
		last_name = line_splits[2]
	else:
		first_name_letter = None
		last_name = line_splits[1]
		
	player_foul = ''
	
	if event[1].find("{" + home + "}") != -1:
		for player in home_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_foul = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_foul = player
				break
	else:
		for player in away_on_court:
			if player.find(last_name) != -1:
				if first_name_letter is not None and first_name_letter == player[0]:
					player_foul = player
				elif first_name_letter is not None and first_name_letter != player[0]:
					continue
				else:
					player_foul = player
				break
	result = result + "PLAYER_FOUL:" + player_foul + ","
	
	#append type of foul
	event_splits = event[1].split(" ")
	for s in event_splits:
		if s.find("FOUL") != -1:
			last_index = s.find("FOUL")
			foul_type = s[:last_index]
			break
	result = result + "FOUL_TYPE:" + foul_type + ","
	
	result = result + '\n'
	
	return result
	

def parse_play_by_play(game_id, date, away, home, away_on_court, home_on_court, away_bench, home_bench, html):
	"""returns a string of the parsed play-by-play data
	
	game_id - a string telling the id of the game
	date - date of game
	away - away team
	home - home team
	away_on_court - list of 5 players who were starters for the away team
	home_on_court - list of 5 players who were starters for the home team
	away_bench - players on away bench including starters
	home_bench - players on home bench including starters
	html - string of play by play html code to be parsed"""
	
	global away_score
	global home_score
	away_score = 0
	home_score = 0
	
	result = ''	
	
	html_split = html.split("\n")
	
	list_of_events = []
	
	#tells numbers of plays per quarter
	plays_per_qtr = [0,0,0,0,0,0,0,0,0,0]
	current_quarter = -1
	
	#get list of event in format "[XXX] EVENT" and figure out how many plays in each quarter
	for line in html_split:
	
		if line.find("GameEventID=") != -1:
			
			#add another play to current quarter
			plays_per_qtr[current_quarter] = plays_per_qtr[current_quarter] + 1
			
			#get event text from html code
			line_splits = line.split(";")
			title = line_splits[-1] #get only the last field
			temp = title[6:] #get rid of title=
			event = temp[0:len(temp)-2] #get rid of ">
			if line.find("VISITORDESCRIPTION") != -1:
				final = "{" + away + "} " + event
			else:
				final = "{" + home + "} " + event
		
			list_of_events.append(final)
		
		
		#if so, move to next quarter
		if line.find("Start of Q") != -1 or line.find("Start of OT") != -1:
			current_quarter = current_quarter + 1	
	
	#append substitions at start of each new quarter
	insert_substitions(date, away, home, list_of_events, plays_per_qtr)	
	
	new_list_of_events = []
	
	#rearrange list of events so that block, shot and rebounds are on same line; turnovers and steals are on the same line; personal foul and all free throws are on the same line
	for event_one, event_two, event_three, event_four in zip(list_of_events, list_of_events[1:] + [''], list_of_events[2:] + ['', ''], list_of_events[3:] + ['', '', '']):
		temp_event = []
			
		#if event_two is a shot:
		if event_two.find("Layup") != -1 or event_two.find("Jumper") != -1 or event_two.find("Fadeaway") != -1 or event_two.find("Jump Shot") != -1 or (event_two.find("Shot") != -1 and event_two.find("Shot Clock") == -1) or event_two.find("Dunk") != -1:
		
			#append shot field to temp_event
			temp_event.append("SHOT")
			temp_event.append(event_two)
			
			#if event_two is from the home team, check event_one if away team blocked it --> event_three should be rebound if MISS
			if event_two.find("{" + home + "}") != -1:
				#if away team blocked
				if event_one.find("BLK") != -1 and event_one.find("{" + away + "}") != -1:
					temp_event.append(event_one)
				else:
					temp_event.append(None)
				
				#if rebound insert as 4th element
				if event_three.find("REBOUND") != -1 or event_three.find("Rebound") != -1:
					temp_event.append(event_three)
				else:
					temp_event.append(None)
				
			#if event_two is from the away team, check event_three if home team blocked it --> event_four should be rebound if blocked, else event_three is rebound
			else:
				#if home team blocked
				if event_three.find("BLK") != -1 and event_three.find("{" + home + "}") != -1:
					temp_event.append(event_three)
					
					#if rebound insert as 4th element
					if event_four.find("REBOUND") != -1 or event_four.find("Rebound") != -1:
						temp_event.append(event_four)
					else:
						temp_event.append(None)
				else:
					temp_event.append(None)
					
					#if rebound insert as 4th element
					if event_three.find("REBOUND") != -1 or event_three.find("Rebound") != -1:
						temp_event.append(event_three)
					else:
						temp_event.append(None)
						
		#if event is a turnover/stl:
		elif event_two.find("Turnover") != -1:
			temp_event.append("TO")
			temp_event.append(event_two)
			
			#search to see if away team stole 
			if event_two.find("{" + home + "}") != -1:
				if event_one.find("STL") != -1:
					temp_event.append(event_one)
				else:
					temp_event.append(None)
			#search if home team stole the ball
			else:
				if event_three.find("STL") != -1:
					temp_event.append(event_three)
				else:
					temp_event.append(None)
			
		#if event is free throw
		elif event_two.find("Free Throw") != -1:
			temp_event.append("FT")
			temp_event.append(event_two)
			
			if event_two.find("Free Throw") != -1 and (event_two.find("1 of 1") != -1 or event_two.find("2 of 2") != -1 or event_two.find("3 of 3") != -1) and event_two.find("MISS") != -1:
				temp_event.append(event_three)
			else:
				temp_event.append(None)
				
		#if event is a sub
		elif event_two.find("SUB") != -1 and (event_two.find("FOR") != -1 or event_two.find("Period") != -1):
			temp_event.append("SUB")
			temp_event.append(event_two)
			
		#if event is a foul
		elif event_two.find("FOUL") != -1:
			temp_event.append("FOUL")
			temp_event.append(event_two)		
		
		if len(temp_event) != 0:
			new_list_of_events.append(temp_event)
	
	for event in new_list_of_events:
		if event[0] == "SHOT":
			result = result + parse_shot(game_id, date, away, home, away_on_court, home_on_court, event)
		elif event[0] == "TO":
			result = result + parse_turnover(game_id, date, away, home, away_on_court, home_on_court, event)
		elif event[0] == "SUB":
			update_lineups(away, home, away_on_court, away_bench, home_on_court, home_bench, event)
		elif event[0] == "FT":
			result = result + parse_free_throw(game_id, date, away, home, away_on_court, home_on_court, event)
		elif event[0] == "FOUL":
			result = result + parse_foul(game_id, date, away, home, away_on_court, home_on_court, event)
	return result
			
def generate(browser, game_id):
	"""purpose: to generate a string that concisely displays all the play-by-play data"""
	
	#data will hold all play-by-play data
	data = ''
	
	#get content from basic boxscore
	url = "http://stats.nba.com/game/" + (game_id) + "/"
	content = get_content_from_webpage(browser, url)
	
	#setup info/starters/bench player for individual game
	away, home, away_on_court, home_on_court, away_on_bench, home_on_bench, date = setup_game_details(game_id, content)
	
	#get content from play-by-play data
	url = url + "playbyplay/"
	content = get_content_from_webpage(browser, url)
	
	data = parse_play_by_play(game_id, date, away, home, away_on_court, home_on_court, away_on_bench, home_on_bench, content)
	
	#append game by game results to csv file
	f = open("2017-18_regular_play_by_play.csv", "a")
	f.write(data)
	f.close()	