from flask import Flask
from flask import request
from flask import render_template
from uk_covid19 import Cov19API
import time_conversions
import pyttsx3
import sched
import time
import requests
import json
import logging

app = Flask(__name__)
engine = pyttsx3.init()
time_controller = time_conversions
s = sched.scheduler(time.time, time.sleep)

alarms = [] 
notifications = []  

file_name = "config.json"
with open(file_name) as f:
    data = json.load(f)

city = data['city']
news_api_key = data['news_api_key']
news_source = data['news_source']
weather_api_key = data['weather_api_key']
covid_data_filter = data['england_only'] 
covid_data_structure = data['cases_and_deaths']

api = Cov19API(filters=covid_data_filter, structure=covid_data_structure)
api_timestamp = api.last_update
covid_data = api.get_json()
today_covid = covid_data['data'][0]

log_format = '%(levelname)s:%(asctime)s %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='pysys.log', format=log_format)
logging.info('server initialised')

def weather_briefing(weather_api: str,weather_city: str) -> str:
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    
    if type(weather_api) is str:
        api_key = weather_api
    
    if type(weather_city) is str:
        city_name = weather_city
    
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()

    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        current_pressure = y["pressure"]
        current_humidiy = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        w_string = 'Weather Briefing. In',city_name,'the temperature is currently',current_temperature,'kelvin. the atmospheric pressure is currently',
        w_string = w_string,current_pressure,'Hectopascal pressure units. the current humidity is',current_humidiy,'percent. the weather is generally',weather_description
    else:
        w_string = 'Weather Briefing: sorry the waether data could not be accessed'
    return w_string

def announce(announcement: str,weather: str) -> None:
    try:
        engine.endLoop()
    except:
        pass
    
    weather_string = ''
    covid_string = ''
    if weather:
        logging.info('weather requested')
        weather_string = weather_briefing(weather_api_key,city)
    
    
    covid_string = 'Covid-19 briefing..',today_covid['newCasesByPublishDate'],'new cases today.'
    covid_string = covid_string,'..',today_covid['cumCasesByPublishDate'],'cases in total.'
    
    logging.info('alarm triggered')
    
    temp_string = 'Alarm called',announcement,'has just gone off',weather_string,covid_string
    engine.say(temp_string)
    engine.runAndWait()

@app.route('/index')
def index():
    
    alarm_time = request.args.get("alarm")
    alarm_name = request.args.get("two")
    news = request.args.get("news")
    weather = request.args.get("weather")
    alarm_cancel = request.args.get("alarm_item")
    notif_cancel = request.args.get("notif")
    
    

    s.run(blocking=False)
    
    

    if alarm_time:
        logging.info('alarm entered')
        alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        delay = time_controller.hhmm_to_seconds(alarm_hhmm) - time_controller.hhmm_to_seconds(time_controller.current_time_hhmm())
        alarms.append({'title': alarm_name, 'content':alarm_time})
        s.enter(int(delay), 1, announce, [alarms[0]['title'],weather])

    if news:
        logging.info('news requested')
        base_news_url = "http://newsapi.org/v2/top-headlines?"
        complete_url = base_news_url + "sources=" + news_source + "&apiKey=" + news_api_key
        top_news_stories = requests.get(complete_url).json()
        for story in top_news_stories['articles']:
            notifications.append({'title': story['title'], 'content':story['description']})

        



    for alarm in alarms:
        if alarm_cancel == alarm['title']:
            alarms.remove(alarm)
            logging.info('alarm removed')
            

    for notif in notifications:
        if notif_cancel == notif['title']:
            notifications.remove(notif)
            logging.info('notification removed')
    
    return render_template('template.html', title='Alarms and Updates', notifications=notifications, image='clock.png', alarms=alarms)

@app.route('/')
def main():
    
    return render_template('template.html', title='Welcome, Alarms and Updates', image='clock.png')

if __name__ == '__main__':
    
    app.run()
