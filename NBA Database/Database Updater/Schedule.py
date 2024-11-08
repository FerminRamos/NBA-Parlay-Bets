# This program is called by "Update_Database.py" to update the schedule.
import csv
import requests
from bs4 import BeautifulSoup
import os
import Request_Ticker


# Gets the game schedule for a given season. Assumes "season schedule"
#  website exists (i.e. not user does not want schedule +20 years in the future)
def getSchedule(seasonEndYr):
    website = f'https://www.basketball-reference.com/leagues/NBA_{seasonEndYr}_games.html'

    Request_Ticker.addRequest()
    websiteContent = requests.get(website).content
    soup = BeautifulSoup(websiteContent, "html.parser")

    table = soup.find('tbody').find_all('tr')

    schedule = [["Game", "Home Team", "Visitor Team", "Date", "Time", "Arena"]]
    for event in table:
        date = event.find('a').text.strip()
        time = event.find('td', {'data-stat': 'game_start_time'}).text.strip()
        visitorTeam = event.find('td', {'data-stat': 'visitor_team_name'}).find('a').text.strip()
        homeTeam = event.find('td', {'data-stat': 'home_team_name'}).find('a').text.strip()
        arena = event.find('td', {'data-stat': 'arena_name'}).text.strip()

        schedule.append([f'{visitorTeam} @ {homeTeam}', homeTeam, visitorTeam, date, time, arena])

    return schedule


# Given a CSV schedule, it updates (or makes) the game schedule. Usually
#  called after getSchedule().
def updateSchedule(schedule, seasonEndYr):
    seasonStartYr = seasonEndYr - 1
    filepath = f"{seasonStartYr}-{seasonEndYr} Season/{seasonStartYr}-{seasonEndYr} Game Schedule.csv"

    try:
        with open(filepath, "w", newline='', encoding='utf-8') as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerows(schedule)

    except FileNotFoundError:  # If dir DNE -> Make dir and try again :)
        os.mkdir(f"{seasonStartYr}-{seasonEndYr} Season")
        with open(filepath, "w", newline='', encoding='utf-8') as csvFile:
            csvWriter = csv.writer(csvFile)
            csvWriter.writerows(schedule)


if __name__ == "__main__":
    getSchedule(2024)
