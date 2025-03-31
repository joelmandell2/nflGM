from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse


#todo: embed model
#todo: get predictions for each player (color by that prediction)
#todo: player page that shows stats of each player
#todo: allow sorting by attribute
#todo: create a three.js model that takes in time 
# to output a color and based on that color, maps helmet 
#todo: custom player creator
#todo: fix navbar and pages



# reads in file and parses out attributes based on position
# returns a dictionary of trait-val


def read_file(file_name):
    json_vals = []
    
    categories = ['40 Yard Dash', 'Height', 'Weight', 'Shuttle', '3 Cone', 'Broad Jump', 'Bench', 'Vertical']

    try:
        with open(file_name, 'r') as file:
            data = file.read()
            player_vals = {}
            count = 0
            for f in data.split(','):
                print(f)
                if count <= 7:
                    val = f
                    if val == '0':
                        val = ' '
                    player_vals[categories[count]] = val
                count += 1
                if ' ' in f and ')' not in f and '(' not in f and f != 'All Pro' and f != 'Below Average Starter':
                    player_vals['name'] = f.title()
                    json_vals.append(player_vals)
                    player_vals = {}
                    count = 0
    except FileNotFoundError:
        print('file not found error')
    return json_vals


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
    print('player request made')
    year = request.GET.get('year', 2025) # default is tom brady if none is passed in
    position = request.GET.get('position', 'WR')
    print(year, ' Year, ', position, ' position')

    test = 'csv_files/' + str(position) + str(year) + '.csv'
    print(test, ' TEST')
    # file_name = f'csv_files/' + str(position) + str(year) + '.csv'
    total_stats = read_file(test)
    return JsonResponse(total_stats, safe=False)

  

def draft_year(request):
    print('draft year request made')
    year = request.GET.get('year', 2025)
    json = {
        'players': [{  # Wrap list inside a dictionary
            'name': year,
            'yards': 10000,
        }]
    }
    print(json, ' draft year year response')
    return JsonResponse(json)