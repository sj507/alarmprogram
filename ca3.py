'''
    balh
'''

import sched
import time
import json
import logging
import requests
import pyttsx3
from flask import Flask
from flask import request
from flask import render_template
from uk_covid19 import Cov19API
import time_conversions

app = Flask(__name__)
engine = pyttsx3.init()
time_cont = time_conversions
s = sched.scheduler(time.time, time.sleep)

alarms = []
notifications = []

FILE_NAME = "config.json"
with open(FILE_NAME) as f:
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

LOG_FORMAT = '%(levelname)s:%(asctime)s %(message)s'
logging.basicConfig(level=logging.DEBUG, filename='pysys.log', format=LOG_FORMAT)
logging.info('server initialised')

def weather_briefing(weather_api: str,weather_city: str) -> str:
    ''' This function takes an api key and a specified city and collects the current
    weather data on it.

    firstly, it checks to make sure that the inputs are valid inputs for this function
    secondly, it checks to make sure that the weather data has been sucessfully collected
    thirdly, it builds a string response containing many aspects of the current weather
    finally, it returns that string as its output
    '''
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    if isinstance(weather_api) is str:
        api_key = weather_api
    if isinstance(weather_city) is str:
        city_name = weather_city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    response_json = response.json()
    if response_json["cod"] != "404":
        right_now = response_json["main"]
        current_temp = right_now["temp"]
        current_pressure = right_now["pressure"]
        current_humidiy = right_now["humidity"]
        weather_description_help = response_json["weather"]
        weather_description = weather_description_help[0]["description"]
        w_string = 'Weather Briefing. In',city_name,'the temperature is currently',current_temp
        w_string = w_string,'kelvin. the atmospheric pressure is currently',current_pressure
        w_string = w_string,'Hectopascal pressure units. the current humidity is',current_humidiy
        w_string = w_string,'percent. the weather is generally',weather_description
    else:
        w_string = 'Weather Briefing: sorry the waether data could not be accessed'
    return w_string

def announce(announcement: str,weather: str) -> None:
    '''This function takes in whether or not the user requested the weather and
    the name of the alarm set

    firstly, it collects the weather data by calling weather_briefing()
    then, it builds a string containing all the requested and relevant infomation
    finally it makes use of pyttsx3 to announce this to the user
    '''
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
    '''This is the function that runs while once the user has set their first alarm
    first, gathering all of the relevant data from the url
    then, checking if an alarm was set and if so setting it
    next, checking if the user requested the news and if so retrieving it
    afterwards, it performs two checks,
    1 to see if a user cancels an alarm and if so remove it,
    2 the same but for notifictions
    finally, it returns a render template, updating the browser window to
    display all the new infomation
    '''
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
        delay = time_cont.hhmm_to_seconds(alarm_hhmm) - time_cont.hhmm_to_seconds(time_cont.current_time_hhmm())
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
    return render_template('template.html', title='Alarms and Updates',
                            notifications=notifications, image='clock.png', alarms=alarms)

@app.route('/')
def main():
    '''the main function to instantiate the html and await user input'''
    return render_template('template.html', title='Welcome, Alarms and Updates', image='clock.png')

if __name__ == '__main__':
    app.run()
