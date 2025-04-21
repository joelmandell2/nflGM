from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from functools import cmp_to_key
import random
import joblib
import os
import re


#todo: custom player creator
#   - allow input that switches with next button (accumulates in state)
#   - fetch prediction based on that data (normalize each)
#   - output prediction
#todo: create about me
#todo: make sure security is solid (protects from xcision attacks)
#todo: host on a server 

#todo: create a three.js model that takes in time 
# to output a color and based on that color, maps helmet 


#comparators used to sort based on attribute

def num_convert(x):
    if x == 'MVP':
        return 5
    if x == 'All Pro':
        return 4
    if x == 'Starter':
        return 3
    if x == 'Below Average Starter':
        return 2
    return 1


def prediction_comp(a, b):
    a_comp = a['classification']
    b_comp = b['classification']
    a_num = num_convert(a_comp)
    b_num = num_convert(b_comp)
    return (b_num > a_num) - (a_num > b_num)

def height_comp(a, b):
    a_height = a['Height']
    b_height = b['Height']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    a_height = a_height.replace('-', '.')
    b_height = b_height.replace('-', '.')
    return (float(b_height) > float(a_height)) - (float(a_height) > float(b_height))

def weight_comp(a, b):
    # need to accomodate blank values
    a_height = a['Weight']
    b_height = b['Weight']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))


def bench_comp(a, b):
    # need to accomodate blank values
    a_height = a['Bench']
    b_height = b['Bench']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))

def broad_comp(a, b):
    # need to accomodate blank values
    a_height = a['Broad']
    b_height = b['Broad']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (int(b_height) > int(a_height)) - (int(a_height) > int(b_height))

def forty_comp(a, b):
    a_height = a['Forty']
    b_height = b['Forty']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def cone_comp(a, b):
    a_height = a['Cone']
    b_height = b['Cone']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def shuttle_comp(a, b):
    a_height = a['Shuttle']
    b_height = b['Shuttle']
    if a_height == ' ':
        a_height = 10000
    if b_height == ' ':
        b_height = 10000
    return (float(a_height) > float(b_height)) - (float(b_height) > float(a_height))

def vert_comp(a, b):
    a_height = a['Vertical']
    b_height = b['Vertical']
    if a_height == ' ':
        a_height = 0
    if b_height == ' ':
        b_height = 0
    return (float(b_height) > float(a_height)) - (float(a_height) > float(b_height))


# overall sorting function
def sort(json_list, sortBy):
    if sortBy == 'name':
        sorted_list = sorted(json_list, key=lambda x: x['name'])
        return sorted_list
    elif sortBy == 'classification':
        sorted_list = sorted(json_list, key=cmp_to_key(prediction_comp))
        return sorted_list
    elif sortBy == 'Height':
        sorted_list = sorted(json_list, key=cmp_to_key(height_comp))
        return sorted_list
    elif sortBy == 'Weight':
        sorted_list = sorted(json_list, key=cmp_to_key(weight_comp))
        return sorted_list
    elif sortBy == '40 Yard Dash':
        sorted_list = sorted(json_list, key=cmp_to_key(forty_comp))
        return sorted_list
    elif sortBy == 'Shuttle':
        sorted_list = sorted(json_list, key=cmp_to_key(shuttle_comp))
        return sorted_list
    elif sortBy == '3 Cone':
        sorted_list = sorted(json_list, key=cmp_to_key(cone_comp))
        return sorted_list
    elif sortBy == 'Broad Jump':
        sorted_list = sorted(json_list, key=cmp_to_key(broad_comp))
        return sorted_list
    elif sortBy == 'Bench Press':
        sorted_list = sorted(json_list, key=cmp_to_key(bench_comp))
        return sorted_list
    elif sortBy == 'Vertical':
        sorted_list = sorted(json_list, key=cmp_to_key(vert_comp))
        return sorted_list
    return json_list



def load_minmax(position):
    # read in minmax file
    minmax = {}
    file_name = 'norms.csv'
    if position == 'TE':
        file_name = 'normsTE.csv'
    elif position == 'RB':
        file_name = 'normsRB.csv'
    elif position == 'QB':
        file_name = 'normsQB.csv'
    # elif position == 'RB':
    #     file_name = 'norms.RB.csv'
    
    with open(file_name, 'r') as file:
        count = 0
        prevWord = ''
        for str in file:
            split_words = str.split(',')
            for word in split_words:
                if word == 'Receptions':
                    word = 'Rec'
                if count == 0:
                    minmax[word] = []
                    prevWord = word
                    count += 1
                else:
                    minmax[prevWord].append(word)
                    count += 1
                if count == 3:
                    count = 0
    return minmax

# read in normalized values 
def normalize(key, val, position):
    if val == 0 or val == ' ' or val == '':
        return .5
    # need to read in these values
    minmax = load_minmax(position)
    if key == 'Receptions':
        key = 'Rec'
    if key == 'Height':
        if val == '5-11' or val == '5-10':
            val = 5.99
        else:
            val = str(val).replace('-', '.')
    min = float(minmax[key][0])
    max = float(minmax[key][1])
    if max == min:
        min = max - 1
    output = (float(val) - float(min)) / (float(max) - float(min))
    return output




# takes in json and returns the normalized values of each attribute 
def getVector(vals, position):
    normalized_list = []
    for key, val in vals.items():
        if key == 'name':
            return normalized_list
        new_val = normalize(key, val, position)
        new_val = max(new_val, 0.0)
        normalized_list.append(new_val)
    if len(normalized_list) < 11:
        while len(normalized_list < 11):
            normalized_list.append(.5)
    return normalized_list



# NEED TO CHANGE SO THAT IT RETRIEVES YOUR ACTUAL PREDICTION
def random_prediction(js, position):
    #issue is you don't have any stats and the models expect college stats


    forest_wr_model = joblib.load('random_forest_model_wr.pkl')
    logistic_wr_model = joblib.load('logistic_model_wr.pkl')
    qb_model = joblib.load('logistic_model_qb.pkl')
    rb_model = joblib.load('perc_model_rb.pkl')
    te_model = joblib.load('perc_model_te.pkl')
    #need to read in min/max/mean values

    # need to switch model based off of position

    vec = getVector(js, position)
    x = len(vec)
    if position == 'RB':
        while x < 12:
            vec.append(.5)
            x = len(vec)
        rb_prediction = rb_model.predict([vec])
        return rb_prediction
    elif position == 'TE':
        while x < 11:
            vec.append(.5)
            x = len(vec)
        return te_model.predict([vec])
    elif position == 'QB':
        while x < 16:
            vec.append(.5)
            x = len(vec)
        qb_prediction = qb_model.predict([vec])
        return qb_prediction
    else:
        while x < 11:
            vec.append(.5)
            x = len(vec)
        forest_prediction = forest_wr_model.predict([vec])
        try:
            # print(forest_prediction, ' FOREST PREDICTION')
            if forest_prediction != 'All Pro' or forest_prediction != 'Backup':
                return logistic_wr_model.predict([vec])
            return forest_prediction
        except Exception as e:
            print(e, ' error')

    # need to pass in vectors to the model
    num = random.randint(1, 5)
    if num == 1:
        return 'All Pro'
    if num == 2:
        return 'Starter'
    if num == 3:
        return 'Below Average Starter'
    else:
        return 'Backup'
    

def clean(word):
    try:
        if len(word) > 0:
            trimmed = word.strip(" '\[]()")
            test = float(trimmed)
            return test
        else:
            return 0
    except ValueError:
        if word == '5-10' or word == '5-11':
            return 5.99
        else:
            cleaned = word.strip(" '\[]()")
            cleaned = cleaned.replace('-', '.')
        try:
            if len(cleaned) > 0:
                test = float(cleaned[0])
                return cleaned
        except ValueError:
            return False
        

def isName(word):
    cats = {'All Pro', 'Below Average Starter', ' RB', ' QB', ' WR', ' TE'}
    return ' ' in word and word not in cats and ')' not in word and '(' not in word

def classify(count, word, position):
    categories = ['Forty', 'Height', 'Weight', 'Shuttle', 'Cone', 'Broad', 'Bench', 'Vertical']
    cats = {'All Pro', 'Below Average Starter', ' RB', ' QB', ' WR', ' TE'}
    word = clean(word)
    if count > 8 and word != False:
        if position == 'RB':
            if count == 9:
                return 'ATT'
            elif count == 11:
                return 'Yards'
            elif count == 15:
                return 'Touchdowns'
        elif position == 'QB':
            if count == 11:
                return 'PCT'
            elif count == 15:
                return 'Touchdowns'
            elif count == 19:
                return 'Rating'
        else:
            if count == 9:
                return 'Receptions'
            elif count == 11:
                return 'Yards'
            elif count == 13:
                return 'Touchdowns'
    else:
        return -1
        

def search_file(file_name, name, position):
    print(file_name, ' fn ', name, ' name ', position, ' position')
    try:
        with open(file_name, 'r') as file:
            print('file opened')
            data = file.read()
            cache = {}
            count = 0
            for row in data.split(','):
                print(row, ' row')
                if isName(row):
                    print(row, ' name found, name desired : ', name)
                    if row.title() == name:
                        print('is name ', row.title())
                        cache['name'] = row.title()
                        if position == 'QB':
                            if 'PCT' not in cache:
                                cache['PCT'] = 0
                            if 'Touchdowns' not in cache:
                                cache['Touchdowns'] = 0
                            if 'Rating' not in cache:
                                cache['Rating'] = 0
                        elif position == 'RB':
                            if 'ATT' not in cache:
                                cache['ATT'] = 0
                            if 'Touchdowns' not in cache:
                                cache['Touchdowns'] = 0
                            if 'Yards' not in cache:
                                cache['Yards'] = 0
                        elif position == 'WR' or position == 'TE':
                            if 'Receptions' not in cache:
                                cache['Receptions'] = 0
                            if 'Touchdowns' not in cache:
                                cache['Touchdowns'] = 0
                            if 'Yards' not in cache:
                                cache['Yards'] = 0
                        if None in cache:
                            cache.pop(None, None)
                        print('cache being returned: ', cache)
                        return cache
                    else:
                        cache = {}
                        count = 0
                else:
                    attribute = classify(count, row, position)
                    cleaned = clean(row)
                    if attribute != -1:
                        cache[attribute] = cleaned
                    count += 1
        return {}
    except FileNotFoundError:
        print('file not found error')

    return 1



#reads in file
def read_file(file_name, sortBy, position):
    json_vals = []
    
    categories = ['Forty', 'Height', 'Weight', 'Shuttle', 'Cone', 'Broad', 'Bench', 'Vertical']

    try:
        with open(file_name, 'r') as file:
            data = file.read()
            player_vals = {}
            count = 0
            for f in data.split(','):
                if count <= 7:
                    val = f
                    if val == '0':
                        val = ' '
                    if count == 2 and (val == '5-10' or val == '5-11'):
                        val = 5.99
                    player_vals[categories[count]] = val
                elif count < 26 and count > 8:
                    val = f
                    val = re.sub(r'[^0-9.]', '', val)
                    if position == 'RB':
                        if count == 9:
                            player_vals['Rec'] = val
                        elif count == 11:
                            player_vals['Yards'] = val
                        elif count == 13:
                            player_vals['avg'] = val
                        elif count == 15:
                            player_vals['Touchdowns'] = val
                    elif position == 'QB':
                        if count == 9:
                            player_vals['att'] = val
                        elif count == 11:
                            player_vals['pct'] = val
                        elif count == 13:
                            player_vals['yds'] = val
                        elif count == 15:
                            player_vals['td'] = val
                        elif count == 17:
                            player_vals['int'] = val
                        elif count == 19:
                            player_vals['rating'] = val
                        elif count == 21:
                            player_vals['rush_yards'] = val
                        elif count == 23:
                            player_vals['r_td'] = val
                    else:
                        if val == '':
                            val = ' '
                        if count == 9:
                            player_vals['Receptions'] = val
                        elif count == 11:
                            player_vals['Yards'] = val
                        elif count == 13:
                            player_vals['Touchdowns'] = val
                count += 1
                if ' ' in f and ')' not in f and '(' not in f and f != 'All Pro' and f != 'Below Average Starter' and f != ' RB' and f != ' QB':
                    player_vals['name'] = f.title()
                    player_vals['classification'] = random_prediction(player_vals, position)[0]
                    if position == 'RB':
                        if 'Rec' in player_vals:
                            del player_vals['Rec']
                        if 'Yards' in player_vals:
                            del player_vals['Yards']
                        if 'avg' in player_vals:
                            del player_vals['avg']
                        if 'Touchdowns' in player_vals:
                            del player_vals['Touchdowns']
                    elif position == 'QB':
                        if 'att' in player_vals:
                            del player_vals['att']
                        if 'pct' in player_vals:
                            del player_vals['pct']
                        if 'yds' in player_vals:
                            del player_vals['yds']
                        if 'td' in player_vals:
                            del player_vals['td']
                        if 'int' in player_vals:
                            del player_vals['int']
                        if 'rating' in player_vals:
                            del player_vals['rating']
                        if 'r_yds' in player_vals:
                            del player_vals['r_yds']
                        if 'r_td' in player_vals:
                            del player_vals['r_td']
                    else:
                        if 'Receptions' in player_vals:
                            del player_vals['Receptions']
                        if 'Yards' in player_vals:
                            del player_vals['Yards']
                        if 'Touchdowns' in player_vals:
                            del player_vals['Touchdowns']
                    json_vals.append(player_vals)
                    player_vals = {}
                    count = 0
    except FileNotFoundError:
        print('file not found error')
    sorted_json = sort(json_vals, sortBy)
    return sorted_json


# views go here
def index(request):
    print('basic request made')
    json = {
        'name' : 'kk',
        'yards' : 10000,
    }
    return JsonResponse(json)



def player(request):

    #need to get position and draft year
    year = request.GET.get('year', 2025) # default is tom brady if none is passed in
    position = request.GET.get('position', 'WR')
    sortBy = request.GET.get('sort', 'name')
    test = 'csv_files/' + str(position) + str(year) + '.csv'


    # file_name = f'csv_files/' + str(position) + str(year) + '.csv'
    total_stats = read_file(test, sortBy, position)
    # print(total_stats, ' RESPONSE BEING RETURNED IN API')
    return JsonResponse(total_stats, safe=False)



def player_page(request):
    #todo: cache results and test name
    print('player page request actually made...shocking')
    name = request.GET.get('p_name', '')
    # name = 'gunnar helm'
    year = request.GET.get('draft_year', 2025)
    pos = request.GET.get('position', 'TE')

    file_name = 'csv_files/' + str(pos) + str(year) + '.csv'

    print(name, ' name ' ,year, ' year ', pos, ' position ', file_name, ' file name')
    player_stats = search_file(file_name, name, pos)
    print(player_stats, ' what is actually being returned')
    return JsonResponse(player_stats, safe=False)

  

def draft_year(request):
    print('draft year request made')
    year = request.GET.get('year', 2025)
    json = {
        'players': [{  # Wrap list inside a dictionary
            'name': year,
            'yards': 10000,
        }]
    }
    return JsonResponse(json)

def clamp(val, min, max):
    if val >= min and val <= max:
        return val
    elif val < min:
        return min
    return max

def get_prediction(request):
    # make sure to clamp input values
    # normalize values 
    # fix url being passed into fetch
    # get the response prediction from the json
    # transform the color of the card based on that prediction
    # display the acutal prediction
    # allow resetting of predictor
    position = request.GET.get('position', 'RB')
    forty = request.GET.get('forty', 4.5)
    height = request.GET.get('height', 6.2)
    weight = request.GET.get('weight', 210)
    broad = request.GET.get('broad', 100)
    cone = request.GET.get('cone', 4.15)
    vertical = request.GET.get('vertical', 35)
    shuttle = request.GET.get('shuttle', 6.9)
    bench = request.GET.get('bench', 20)

    attempts = request.GET.get('attempts', 100)
    pct = request.GET.get('percent', 50)
    pass_yards = request.GET.get('pass_yards', 1500)
    pass_td = request.GET.get('pass_td', 10)
    interceptions = request.GET.get('interceptions', 10)
    qbr = request.GET.get('qbr', 50)
    r_yds = request.GET.get('r_yds', 10)
    r_td = request.GET.get('r_td', 1)
    r_avg = request.GET.get('r_avg', 1)
    r_att = request.GET.get('r_att', 1)
    rec = request.GET.get('rec', 1)
    rec_yds = request.GET.get('rec_yds', 1)
    rec_avg = request.GET.get('rec_avg', 1)
    rec_td = request.GET.get('rec_td', 1)

    # categories = ['Forty', 'Height', 'Weight', 'Shuttle', 'Cone', 'Broad', 'Bench', 'Vertical']

    norms = []


    try:
        forty = float(clean(forty))
    except ValueError:
        forty = 4.7 
    forty = normalize('Forty', clean(clamp(forty, 4.1, 6.0)), position)
    norms.append(forty)

    try:
        height = float(clean(height))
    except ValueError:
        height = 6.0 
    height = normalize('Height', clean(clamp(height, 5.5, 6.9)), position)
    norms.append(height)


    try:
        weight = float(clean(weight))
    except ValueError:
        weight = 200 
    weight = normalize('Weight', clean(clamp(weight, 130, 350)), position)
    norms.append(weight)

    try:
        shuttle = float(clean(shuttle))
    except ValueError:
        shuttle = 6.9 
    shuttle = normalize('Shuttle', clean(clamp(shuttle, 5.0, 9.9)), position)
    norms.append(shuttle)

    try:
        broad = float(clean(broad))
    except ValueError:
        broad = 100
    broad = normalize('Broad', clean(clamp(broad, 50, 200)), position)
    norms.append(broad)
    
    try:
        cone = float(clean(cone))
    except ValueError:
        cone = 100
    cone = normalize('Cone', clean(clamp(broad, 3.0, 10.0)), position)
    norms.append(cone)

    try:
        vertical = float(clean(vertical))
    except ValueError:
        vertical = 100
    vertical = normalize('Vertical', clean(clamp(broad, 0, 80)), position)
    norms.append(vertical)

    try:
        bench = float(clean(bench))
    except ValueError:
        bench = 100
    bench = normalize('Cone', clean(clamp(bench, 0, 80)), position)
    norms.append(bench)

    if position == 'QB':
        # all the qb attributes
        try:
            att = float(clean(attempts))
        except ValueError:
            att = 100
        att = normalize('Attempts', clean(clamp(att, 0, 100000)), position)
        norms.append(att)

        try:
            pct = float(clean(pct))
        except ValueError:
            pct = 50
        pct = normalize('Percent', clean(clamp(pct, 0, 101)), position)
        norms.append(pct)
    # starts here
        try:
            pass_yards = float(clean(pass_yards))
        except ValueError:
            pass_yards = 100
        pass_yards = normalize('p_yards', clean(clamp(pass_yards, 0, 100000)), position)
        norms.append(pass_yards)

        try:
            pass_td = float(clean(pass_td))
        except ValueError:
            pass_td = 20
        pass_td = normalize('p_td', clean(clamp(pass_td, 0, 10000)), position)
        norms.append(pass_td)

        try:
            interceptions = float(clean(interceptions))
        except ValueError:
            interceptions = 10
        interceptions = normalize('interceptions', clean(clamp(interceptions, 0, 200)), position)
        norms.append(interceptions)

        try:
            qbr = float(clean(qbr))
        except ValueError:
            qbr = 10
        qbr = normalize('qbr', clean(clamp(qbr, 0, 300)), position)
        norms.append(qbr)

        try:
            r_yds = float(clean(r_yds))
        except ValueError:
            r_yds = 10
        r_yds = normalize('r_yds', clean(clamp(r_yds, 0, 10000)), position)
        norms.append(r_yds)

        try:
            r_td = float(clean(r_td))
        except ValueError:
            r_td = 10
        r_td = normalize('r_td', clean(clamp(r_td, 0, 800)), position)
        norms.append(r_td)

    elif position == 'RB':
        # rb attributes
        try:
            r_yds = float(clean(r_yds))
        except ValueError:
            r_yds = 10
        r_yds = normalize('r_yds', clean(clamp(r_yds, 0, 10000)), position)
        norms.append(r_yds)


        try:
            r_td = float(clean(r_td))
        except ValueError:
            r_td = 10
        r_td = normalize('r_td', clean(clamp(r_td, 0, 10000)), position)
        norms.append(r_td)


        try:
            r_att = float(clean(r_att))
        except ValueError:
            r_att = 10
        r_att = normalize('r_att', clean(clamp(r_att, 0, 10000)), position)
        norms.append(r_att)

        try:
            r_avg = float(clean(r_avg))
        except ValueError:
            r_avg = 10
        r_avg = normalize('r_avg', clean(clamp(r_avg, 0, 100)), position)
        norms.append(r_avg)

    else:
        # wr attributes

        try:
            rec = float(clean(rec))
        except ValueError:
            rec = 10
        rec = normalize('rec', clean(clamp(rec, 0, 10000)), position)
        norms.append(rec)

        try:
            rec_yds = float(clean(rec_yds))
        except ValueError:
            rec_yds = 10
        rec_yds = normalize('rec_yds', clean(clamp(rec_yds, 0, 10000)), position)
        norms.append(rec_yds)

        try:
            rec_avg = float(clean(rec_avg))
        except ValueError:
            rec_avg = 10
        rec_avg = normalize('rec_avg', clean(clamp(rec_avg, 0, 100)), position)
        norms.append(rec_avg)


        try:
            rec_td = float(clean(rec_td))
        except ValueError:
            rec_td = 10
        rec_td = normalize('rec_td', clean(clamp(rec_td, 0, 300)), position)
        norms.append(rec_td)
    
    forest_wr_model = joblib.load('random_forest_model_wr.pkl')
    logistic_wr_model = joblib.load('logistic_model_wr.pkl')
    qb_model = joblib.load('logistic_model_qb.pkl')
    rb_model = joblib.load('perc_model_rb.pkl')
    te_model = joblib.load('perc_model_te.pkl')


    if position == 'QB':
        pred = {'prediction' : qb_model.predict([norms])}
        return JsonResponse(pred)
    elif position == 'RB':
        pred = {'prediction' : rb_model.predict([norms])}
        return JsonResponse(pred)
    elif position == 'TE':
        pred = {'prediction' : te_model.predict([norms])}
        return JsonResponse(pred)
    else:
        forest_prediction = forest_wr_model.predict([norms])
        if forest_prediction != 'All Pro' or forest_prediction != 'Backup':
            pred = {'prediction' : logistic_wr_model.predict([norms])}
            return JsonResponse(pred)
        pred = {'prediction' : forest_prediction}
        return JsonResponse(pred)