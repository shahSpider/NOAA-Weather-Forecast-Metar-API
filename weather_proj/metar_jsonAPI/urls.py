from django.urls import path, re_path
from metar_jsonAPI.views import index, ping, weatherInfo

#urlpatterns here



urlpatterns = [
    path('', index, name='home'),
    path('metar/ping', ping, name='ping'),
    path('metar/info/', weatherInfo, name='weather_info'),
    
]
