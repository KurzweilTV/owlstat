#!/usr/bin/env python3

import requests
import json
import sys
import argparse
import time
import datetime

sys.tracebacklimit = 0 # set to 1 to see traceback

parser = argparse.ArgumentParser(description='Gets Overwatch Leage Schedule from API')
parser.add_argument('-s', '--stage', action="store", dest="stage", default=1, help="stage number", type=int)
parser.add_argument('-w', '--week', action="store", dest="week_num", default=1, help="week number", type=int)
parser.add_argument('-t', '--today', action="store_true", dest="today", help="matches today,")
parser.add_argument('-g', '--google', action="store_true", dest="google", help="outputs for google sheets")
args = parser.parse_args()

pretty_stage = args.stage
pretty_week = args.week_num
args.week_num = args.week_num - 1

if args.stage < 3:
    args.stage = args.stage - 1

# get data
response = requests.get('https://api.overwatchleague.com/schedule')
data = response.json()

try:
    games = range(0,(len(data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"])))
except IndexError:
    print("Error: Week not found.")
    sys.exit(1)
except ValueError:
    print("Error: Argument must be an integer")
    sys.exit(1)

# methods
def get_match(week_num, match_num):
    team1 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["competitors"][0]["name"]
    team2 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["competitors"][1]["name"]
    return team1 + " vs. " + team2

def get_match_id(week_num, match_num):
    return (data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["id"])

def get_results(week_num, match_num):
    winner = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["winner"]["name"]
    score1 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["scores"][0]["value"]
    score2 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["scores"][1]["value"]
    return " (" + str(score1) + "-" + str(score2) + ")"

def get_match_date(week_num, match_num):
    startDate = str(data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][match_num]["startDateTS"])
    startDate = startDate[:10]
    return time.strftime('%D (%A)', time.localtime(int(startDate)))

def get_today():
    now = datetime.datetime.now()
    return now.strftime("%D (%A)")

def build_schedule():
    schedule = {}
    for game in games:
        date = get_match_date(args.week_num, game)
        schedule[date] = []
    for game in games:
        date = get_match_date(args.week_num, game)
        match_state = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["state"]
        team1 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["competitors"][0]["name"]
        team2 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["competitors"][1]["name"]
        if  match_state == "CONCLUDED":
            schedule[date].append(team1 + " vs. " + team2 + get_results(args.week_num, game))
        else:
            schedule[date].append(team1 + " vs. " + team2)
    return schedule

def build_google():
    schedule = {}
    for game in games:
        date = get_match_date(args.week_num, game)
        schedule[date] = []
    for game in games:
        date = get_match_date(args.week_num, game)
        match_state = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["state"]
        team1 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["competitors"][0]["name"]
        team2 = data["data"]["stages"][args.stage]["weeks"][args.week_num]["matches"][game]["competitors"][1]["name"]

        team1 = team1.split(" ")
        team2 = team2.split(" ")
        schedule[date].append(team1[-1] + " vs. " + team2[-1])
    return schedule

# display data
if args.google:
    print("\nOverwatch League: Stage %s Week %s\n" % (pretty_stage, pretty_week))
    schedule = build_google()
    day = 1
    for key, value in schedule.items():
        print("Week %s Day %d" % (pretty_week, day))
        print(*value, sep='\n')
        day += 1
    sys.exit(0)

print("\nOverwatch League: Stage %s Week %s\n" % (pretty_stage, pretty_week))
schedule = build_schedule()
for key, value in schedule.items():
    print(key)
    print(*value, sep='\n')
    print()
sys.exit(0)
