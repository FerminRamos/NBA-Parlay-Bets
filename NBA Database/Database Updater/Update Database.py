# This program can update our NBA database. Interface is the console. A user
#  may choose to:
#    1. Add a new season to our database
#    2. Copy/paste the file/folder path that they want to be
#       updated.
#  A valid file/folder path should contain all the necessary information
#  to update the necessary files.
import csv
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
import Schedule
import os

BASE_PATH = "/Users/speak_easy/Python UNM/NBA-Parlay-Bets/NBA Database"


# Creates a new "20XX-20XX Season" folder. ASSUMES a duplicate folder name DNE.
#  After creation, it populates the folder with sub-folders & placeholder files.
def createSeasonFolder(seasonStartYr, seasonEndYr):
    if seasonEndYr - seasonStartYr != 1:
        print(">> Season date invalid <<  Aborted season creation ")
        return None

    # Make Season Folder
    newSeasonPath = BASE_PATH + f"/{seasonStartYr}-{seasonEndYr} Season"
    os.mkdir(newSeasonPath)

    # Game Schedule
    gameSchedule = Schedule.getSchedule(seasonEndYr)
    Schedule.updateSchedule(gameSchedule, seasonEndYr)

    # Make Teams Folders
    createTeamsFolders(newSeasonPath)

    # TODO: Create player folders to each team folder
    for teamFolder in getFolderPaths(newSeasonPath):
        continue

    return None


# Creates a team folder for all 30 NBA teams. ASSUMES the parent folder
#  "20XX-20XX Season" is already created. "Placeholder" files are also
#  created for each team:
#    1. Team Statistics
#    2. Log information
#  Player folders are also populated with real data. Details on files
#  contained for each player folder can be found in a different function.
# TODO: Add placeholder log files when creating each team folder
# TODO: Add boolean arg, if need to populate with roster folders for each team
def createTeamsFolders(path):
    # Gets the pre-set list of teams
    teams = []
    with open(BASE_PATH + "/Database Updater/Misc Files/teams list.csv", encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile)
        for line in csvReader:
            teams.append(line[0])
    teams.pop(0)  # Pop the CSV header

    # Make folders if DNE
    for team in teams:
        try:
            os.mkdir(path + f"/{team}")
        except FileExistsError:
            continue


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


# Opens our database "teams list.csv" to get the team's website link.
#  Returns a URL string.
def getTeamWebsite(team):
    with open(BASE_PATH + "/Database Updater/Misc Files/teams list.csv", "r", encoding='utf-8') as csvFile:
        csvReader = csv.reader(csvFile)
        for line in csvReader:
            if line[0] == team:
                return line[1]


# Returns the list of folders found in a path
def getFolderPaths(path):
    folders = []
    for file in os.listdir(path):
        if file.find(".") == -1:
            folders.append(path + f"/{file}")
    return folders


if __name__ == "__main__":
    getUpdatedRoster(team="Atlanta Hawks", seasonEndYr=2025)
    print()
