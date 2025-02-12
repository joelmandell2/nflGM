import requests
from bs4 import BeautifulSoup
import pandas as pd
import math

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.sql.util import expand_column_list_from_order_by


#todo: store nfl stats in csv so you don't have to continually web scrape
#todo: normalize combines results
#todo: train model on multiple years of data (only one position per training)
#todo: predict based off of model
#todo: graph results

# 1.) Train
    # - be able to scrape combine data from x previous years
    # - parse that data into features for each player alongside their career results
        # - need metrics that determine success based off of draft position (before training so you know what position)
# use round as a measure of success
# also need to do by position
# account for missing data with null values/Average value placement
# get a scale value like height 5'5-7 feet


#globals
# a list of each dictionary mapping testing category to the player's result
maps = []
college_stats_url = 'https://www.sports-reference.com/cfb/players/'
college_stats_part2 = '/splits/'

def classify(pos, rating):
    if pos == 'QB':
        if rating > 70.0:
            return 'MVP'
        elif rating > 65.0:
            return 'All Pro'
        elif rating > 55.0:
            return 'Starter'
        elif rating > 45.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'RB':
        if rating > 51.0:
            return 'All Pro'
        elif rating > 45.0:
            return 'Starter'
        elif rating > 40.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'WR':
        if rating > 145.0:
            return 'All Pro'
        elif rating > 100.0:
            return 'Starter'
        elif rating > 60.0:
            return 'Below Average Starter'
        else:
            return 'Backup'
    elif pos == 'TE':
        if rating > 85.0:
            return 'All Pro'
        elif rating > 45.0:
            return 'Starter'
        else:
            return 'Backup'
    elif pos == 'DEF':
        if rating > 90.0:
            return 'MVP'
        if rating > 75.0:
            return 'All Pro'
        elif rating > 55.0:
            return 'Starter'
        else:
            return 'Backup'




# calculates qbr for quarterbacks
def qbr(stats):
    # player_statistics = {'Games': 0, 'ATT': 0, 'CMP': 0, 'YDS': 0, 'TD': 0, 'INT': 0}
    completions = float(stats['CMP'])
    attempts = float(stats['ATT'])
    yards = float(stats['YDS'])
    td = float(stats['TD'])
    int = float(stats['INT'])

    a = ((completions / attempts) - .3) / .2
    b = ((yards / attempts) - 3) / 4.0
    c = (td / attempts) / .05
    d = (.095 - (int / attempts)) / .04

    return (a + b + c + d) / .06

# calculates rating for running backs
def rbr(stats):
    # player_statistics = {'Games': 0, 'YDS': 0, 'AVG': 0, 'TD': 0, 'FUM': 0}
    ry = (2 * (stats['YDS'] / stats['ATT']) - 5 ) * (1.0 / 3.0)
    rt = stats['TD'] / stats['ATT'] * 35
    rf = 2.375 - (55 * (stats['FUM'] / stats['ATT']))
    return ry + rt + rf * (100.0/4.0)

def wrr(stats):
    # player_statistics = {'Games': 0, 'YDS': 0, 'AVG': 0, 'TD': 0, 'REC': 0}
    return (float(stats['YDS']) + 18.0 * float(stats['TD']) / (float(stats['Games']) / 17.0)) / 10.0

def lbr(stats):
    # player_statistics = {'Games': 0, 'TKL': 0, 'SACK': 0, 'PDEF': 0, 'INT': 0}
    return (float((stats['TKL'])) * .5 + float(stats['SACK']) * 5.0 + float(stats['PDEF']) * 1.5 + 4.0 *
            float(stats['INT'])) / (stats['Games'] / 17.0)


def calculateRating(pos, stats):
    if pos == 'QB':
        return classify(pos, qbr(stats))
    elif pos == 'RB':
        return classify(pos, rbr(stats))
    elif pos == 'WR':
        return classify(pos, wrr(stats))
    elif pos == 'TE':
        return classify(pos, wrr(stats))
    elif pos == 'LB':
        return classify(pos, lbr(stats))


def scrape_nfl_player_stats(player_name):
    # Build the URL for the player’s career stats
    player_stats = {}

    base_url = f'https://www.nfl.com/players/{player_name.lower().replace(" ", "-")}/stats/career'

    # Set up the Selenium WebDriver (ensure you have ChromeDriver installed)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(base_url)
    player_stats[player_name] = []

    try:
        # Wait until the table containing the career stats is loaded
        # We're waiting for an element with the class 'd3-o-table' (the stats table)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "d3-o-table"))
        )

        # Get the page source after JavaScript has rendered the page
        html = driver.page_source

        # Parse the page source using BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Find the career stats table (it has the class 'd3-o-table')
        stats_table = soup.find('table', {'class': 'd3-o-table'})

        # Extract all rows of the table
        rows = stats_table.find_all('tr')

        # Iterate over the rows and print the player stats
        for row in rows:
            # Extract columns (td tags)
            columns = row.find_all('td')
            if columns:  # Skip rows that don't have columns (like the header row)
                stats = [col.get_text(strip=True) for col in columns]
                player_stats[player_name].append(stats)
    finally:
        # Close the driver once we're done
        driver.quit()
        return player_stats


def parse_nfl_stats(position, stats):
    if position == 'QB':
        player_statistics = {'Games' : 0, 'ATT' : 0, 'CMP' : 0,'YDS' : 0, 'TD': 0, 'INT' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    player_statistics['Games'] += int(st[i])
                elif i == 3:
                    player_statistics['ATT'] += float(st[i])
                elif i == 4:
                    player_statistics['CMP'] += float(st[i])
                elif i == 6:
                    player_statistics['YDS'] += int(st[i])
                elif i == 9:
                    player_statistics['TD'] += int(st[i])
                elif i == 10:
                    player_statistics['INT'] += int(st[i])
        return player_statistics


    elif position == 'RB':
        player_statistics = {'Games' : 0, 'ATT' : 0, 'YDS' : 0, 'AVG' : 0, 'TD': 0, 'FUM' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    player_statistics['Games'] += int(st[i])
                elif i == 3:
                    player_statistics['ATT'] += int(st[i])
                elif i == 4:
                    player_statistics['YDS'] += int(st[i])
                elif i == 5:
                    player_statistics['AVG'] += float(st[i])
                elif i == 7:
                    player_statistics['TD'] += int(st[i])
                elif i == 12:
                    player_statistics['FUM'] += int(st[i])
        return player_statistics


    elif position == 'WR':
        player_statistics = {'Games' : 0, 'YDS' : 0, 'AVG' : 0, 'TD': 0, 'REC' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    player_statistics['Games'] += int(st[i])
                elif i == 3:
                    player_statistics['REC'] += int(st[i])
                elif i == 4:
                    player_statistics['YDS'] += int(st[i])
                elif i == 5:
                    player_statistics['AVG'] += float(st[i])
                elif i == 7:
                    player_statistics['TD'] += int(st[i])
        return player_statistics
    if position == 'DEFENSE':
        player_statistics = {'Games' : 0, 'TKL' : 0, 'SACK' : 0, 'PDEF': 0, 'INT' : 0}
        for st in stats:
            for i in range(len(st)):
                if i == 2:
                    player_statistics['Games'] += int(st[i])
                elif i == 3:
                    player_statistics['TKL'] += int(st[i])
                elif i == 6:
                    player_statistics['SACK'] += int(st[i])
                elif i == 8:
                    player_statistics['PDEF'] += int(st[i])
                elif i == 9:
                    if not int(st[i]) == '':
                        player_statistics['INT'] += int(st[i])
        return player_statistics


def get_player_url(player_name):
    base_url = r'https://www.nfl.com/players/josh-allen/stats/career/'
    names = player_name.split(' ')
    part2 = '/stats/career'
    full_name = names[0] + '-' + names[1]
    full_url = base_url + full_name.lower() + part2
    response = requests.get(full_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    x = soup.find_all('tr')
    return None


def dot(vec1, vec2):
    return sum(x * y for x, y in zip(vec1, vec2))

# parses the url of the year passed in, returns combine for that year
def getURL(year):
    baseUrl = 'https://www.pro-football-reference.com/draft/'
    extension = str(year) + '-combine.html'
    return baseUrl + extension

# takes in full url and returns tables from that url
def parseHTML(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.find_all('td')

#returns the type of stats to cipher based off of position being passed in
def stats(pos):
    wrs = {'TE', 'WR'}
    defense = {'CB', 'EDGE', 'S', 'LB', 'DT', 'DE'}
    if pos in wrs:
        return 'WR'
    if pos in defense:
        return 'DEFENSE'
    if pos == 'RB':
        return 'RB'
    if pos == 'QB':
        return 'QB'
    return False


def parseCollegeStats(position, count, attr):
    # 0 year, 1 team, 2 games, 3 tackles, 4 solo, 5 ast, 6 sack, 7 safety, 8 pdef, 9 int, 10 tds, 11 yds, 12 avg, 13 lng
    if position == 'DEFENSE':
        if count == 1:
            return ('year', attr)
        elif count == 2:
            return ('solo', attr)
        elif count == 4:
            return ('tackles', attr)
        elif count == 5:
            return ('tfl', attr)
        elif count == 6:
            return ('sack', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 10:
            return ('pd', attr)
        else:
            return -1
    # 1 = comp, 2 = attempts, 3 = pct 4 = yds, 5 = td, 6= int, 7 = rate, 8 = att, 9 = yds, 10 = avg, 11 = td
    if position == 'QB':
        if count == 3:
            return ('att', attr)
        elif count == 4:
            return ('pct', attr)
        elif count == 5:
            return ('yds', attr)
        elif count == 6:
            return ('td', attr)
        elif count == 7:
            return ('int', attr)
        elif count == 8:
            return ('rating', attr)
        elif count == 10:
            return ('r_yds', attr)
        elif count == 12:
            return ('td', attr)
        else:
            return -1
        # 1 = att, 2 = yds, 3 = yds/att, 4 = td, 5 = rec, 6 = rec yds, 7 = avg, 8 = td

    if position == 'RB':
        if count == 2:
            return ('att', attr)
        elif count == 3:
            return ('yds', attr)
        elif count == 4:
            return ('avg', attr)
        elif count == 5:
            return ('td', attr)
        elif count == 6:
            return ('rec', attr)
        elif count == 7:
            return ('rec_yds', attr)
        elif count == 9:
            return ('rec_td', attr)
        else:
            return -1
    if position == 'WR' or position == 'TE':
        if count == 0:
            return ('year', attr)
        elif count == 1:
            return ('games', attr)
        elif count == 2:
            return ('rec', attr)
        elif count == 3:
            return ('yards', attr)
        elif count == 5:
            return ('td', attr)
        else:
            return -1

#defines what the player is actually classified as based upon their position and statistic
# used for model training to define class of player
def success(position, stats):
    if position == 'DB':
        # need to create some sort of ratings calculation
        print(1)

# parses college stats
# 1 = att, 2 = yds, 3 = yds/att, 4 = td, 5 = rec, 6 = rec yds, 7 = avg, 8 = td
def cipherCollegeStats(url, pos):
    #rb qb works
    # test wr, te
    table = parseHTML(url)
    count = 1
    times = 0
    stats = []
    for row in table:
        times += 1
        if count > 11 or (count > 7 and (pos == 'WR' or pos == 'TE')):
            break
        for word in row:
            attr = word.strip('\n')
            attr = attr.strip(' ')
            attr = attr.strip('\n')
            count += 1
            if times > 1:
                stat = parseCollegeStats(pos, count, attr)
                if stat != -1:
                    stats.append(stat)
    return stats


# overall data assignment, call this method to take in a table full of draft data
# returns a tuple with dictionary with keys = testing attribute and value = the player's value, alongside what class
# that player was classified as
def assignData(table, int_year):
    attributes = {'forty_yd', 'height', 'pos', 'weight', 'shuttle', 'cone', 'broad_jump', 'bench_reps', 'vertical'}
    player = {}
    for row in table:
        dos = row.attrs['data-stat']
        for word in row:
            if dos in attributes:
                player[dos] = word
        if dos == 'draft_info':
            maps.append(player)
            player = {}
        if dos == 'college':
            words = (word.attrs['href']).split('players/')
            if len(words) > 1:
                name = words[1]
                names = name.split('-')
                nfl_name = names[0] + ' ' + names[1]
                nfl_name2 = names[0] + '-' + names[1]
                college_name = nfl_name2 + '-1'
                #todo: GOOD UNTIL HERE, NEED TO:
                # todo: 1.) PARSE OFFENSIVE STATS
                # todo:  2.) DEFINE SUCCESS
                # todo: 3.) DEAL WITH COLLEGE
                # todo: 4.) TRAIN MODEL

                remains = scrape_nfl_player_stats(nfl_name)
                nfl_s = 0
                for x, y in remains.items():
                    saved = parse_nfl_stats(stats(player['pos']), y)
                    nfl_s = saved
                college_stats = cipherCollegeStats(college_stats_url + college_name + college_stats_part2, stats(player['pos']))
                print(1)
    return player
    # do an if



# cipherCollegeStats(college_stats_url + 'kyle-hamilton' + college_stats_part2, 'DEFENSE')
assignData(parseHTML('https://www.pro-football-reference.com/draft/2022-combine.htm'), 2023)
print(maps)
# perceptron (true = draft, false = don't)

# need to parse stats to be able to pass in nfl and college stats to signify success or failure
# need to normalize values so that the perceptron can classify based on feature category



class BinaryPerceptron():
    def __init__(self, examples, iterations, round):
        # examples is a map of player name to their stats/result
        # set of Tuples(tuple of ((map: name, feature), result)

        # each example is a tuple of 2 pair tuples
        self.weight = {}
        for example in examples:
            for key, item in example[0]:
                self.weight[key] = 0
        # sets the weight of each feature to 0
        for i in range(iterations):
            for x, y in examples:
                totalDot = 0
                for k, v in x.items():
                    totalDot += self.weight[k] * v
                yCurrent = totalDot > 0
                if yCurrent != y:
                    for key, val in x.items():
                        if y:
                            self.weight[key] += val
                        else:
                            self.weight[key] -= val

    # potentially return the grade given from the prediction
    def predict(self, x):
        total = 0
        for key, val in x.items():
            total += dot([self.weight[key]], [val])
        return total > 0

class MulticlassPerceptron():
    # x = string (pass in 3 features, one for each position), tuple of chars
    # y = answer
    def __init__(self, examples, iterations):
        self.weight = {}
        self.iterations = iterations
        self.examples = examples
        for example in examples:
            label = example[1]
            self.weight[label] = {}
        for i in range(iterations):
            for x, y in examples:
                prediction = self.predict(x)
                if y != prediction:
                    for key, val in x.items():
                        if key in self.weight[y]:
                            self.weight[y][key] += val
                        else:
                            self.weight[y][key] = val
                        if key in self.weight[prediction]:
                            self.weight[prediction][key] -= val
                        else:
                            self.weight[prediction][key] = -val

    def predict(self, x):
        max_sum = -math.inf
        prediction = None
        for label, pred in self.weight.items():
            temp_sum = 0
            for key in x.keys():
                if key in pred:
                    temp_sum += pred[key] * x.get(key, 0)
            if temp_sum > max_sum:
                max_sum = temp_sum
                prediction = label
        return prediction



# graph