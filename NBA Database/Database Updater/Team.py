# This program is responsible for any updates regarding the team as a whole.
#  It can update:
#    1. team statistics
#    2. the roster (including check if player was cut)
#    3. team log information
#  Program cannot make changes to player folders or files within player folders
import csv
import requests
from bs4 import BeautifulSoup
import Global


# Returns a CSV of players and their characteristics:
#   1. Player name
#   2. Team
#   3. Position
#   4. Height
#   5. DOB
#   6. Nationality
#   7. Experience (Yrs)
#   8. Player Website
def getUpdatedRoster(team, seasonEndYr):
    websiteLink = getTeamWebsite(team).replace("YEAR", str(seasonEndYr))
    websiteHTML = requests.get(websiteLink)
    soup = BeautifulSoup(websiteHTML.content, "html.parser")

    table = soup.find('div', id="div_roster")

    roster = [["Player", "Team", "Position", "Height", "Weight", "DOB", "Nationality", "Experience (Yrs)", "Website"]]
    for row in table.find_all('tr')[1:]:  # Skips table header
        player = row.find('a').text
        playerWebsite = "https://www.basketball-reference.com" + row.find('a')['href']
        position = row.find('td', {'data-stat': 'pos'}).text
        height = row.find('td', {'data-stat': 'height'}).text
        weight = row.find('td', {'data-stat': 'weight'}).text
        DOB = row.find('td', {'data-stat': 'birth_date'}).text
        nationality = row.find('td', {'data-stat': 'flag'}).text.split(" ")[1]
        experience = row.find('td', {'data-stat': 'years_experience'}).text

        roster.append([player, team, position, height, weight, DOB, nationality, experience, playerWebsite])

    # print(tabulate(roster))

    return roster


# Checks if a player was cut from their team.
#  Return cut status & current roster.
def playerCut(player, team, seasonEnd):
    roster = getUpdatedRoster(team=team, seasonEndYr=seasonEnd)
    cut = True
    for playerData in roster:
        if player == playerData[0]:
            cut = False
            break

    # return cut, roster
    return False, roster         # TODO: TEMP


# Opens our database "teams list.csv" to get the team's website link.
#  Returns a URL string.
def getTeamWebsite(team):
    with open(Global.BASE_PATH + "/Database Updater/Misc Files/teams list.csv", "r", encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile)
        for line in csvReader:
            if line[0] == team:
                return line[1]

