from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
import requests
import json
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from metar import Metar
from django.conf import settings
import redis
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
import redis


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

# Connect to Redis instance
redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                  port=settings.REDIS_PORT, db=0)


# Create your views here.

# view for homepage

def index(request):
	template_name = "metar_jsonAPI/index.html"
	return render(request, template_name)





#view to test ping our website
@api_view()
def ping(request):
    
    if request.method == "GET":
            
        data = {
            "data" : "pong"
        }

        return Response(data)




@vary_on_cookie
@api_view()
def weatherInfo(request):

	#get metar report and convert it in json reponse and displays json response on the browser
	#store it in redis cache for 5 minutes

	if request.GET.get('scode') and not request.GET.get('nocache'):
		scode = request.GET['scode']
		r = requests.get('http://tgftp.nws.noaa.gov/data/observations/metar/stations/{}.TXT'.format(scode))

		info = r.text
		metar_data = [z for z in info.split("\n")]

		obs = Metar.Metar(metar_data[1])
		result = {'data' : obs.string()}

		redis_instance.set("data", obs.string(), CACHE_TTL)

		response = {
			'data' : result
		}

		return Response(response)




	#if the user nocache param is given in the url
	if request.GET.get('nocache'):
		nocache = request.GET.get('nocache')
		
		#if nocache is not 1 so the data will be fetched from cached in redis and returned json reponse on the browser
		if nocache != '1':

			cacheData = redis_instance.get("data")
			
			response = {
			'data' : cacheData
			}

			return Response(response)

		#if nocache param is 1 so it will get referesh/flush the redis cache and fetch live data from the website tgftp.nooa.gov
		#and displays json reponse on browser

		else:
			redcache = redis.Redis()
			redcache.flushdb()
			scode = request.GET['scode']
			r = requests.get('http://tgftp.nws.noaa.gov/data/observations/metar/stations/{}.TXT'.format(scode))
		    
		    

			info = r.text
			metar_data = [z for z in info.split("\n")]

			obs = Metar.Metar(metar_data[1])
			# result = {'data' : obs.string()}

			response = {
				'data' : obs.string()
			}

			return Response(response)
