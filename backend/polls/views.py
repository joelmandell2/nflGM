from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse



# need to import names and read in data
#todo: import names by class
# get player data for each name









# views go here
def index(request):
    print('basic request made')
    json = {
        'name' : 'kk',
        'yards' : 10000,
    }
    return JsonResponse(json)



def player(request):
    print('player request made')
    player_name = request.GET.get('year', 2025) # default is tom brady if none is passed in
    if player_name == 2025:
        json = json = [
            # returns an array of dictionaries (each must have same keys) 
            {
                'name': 'Rico Flores',
                'yards': 10000,
            }, 
            {
                'name': 'joe flacco',
                'yards': 32000,
            }
        ]

        print(json, ' json response')
        return JsonResponse(json, safe=False)
    else: 
        json = json = [
            # returns an array of dictionaries (each must have same keys) 
            {
                'name': 'Tito Johnson',
                'yards': 10000,
            }, 
            {
                'name': 'Archibald Rogers',
                'yards': 32000,
            }
        ]

        print(json, ' json response')
        return JsonResponse(json, safe=False)


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