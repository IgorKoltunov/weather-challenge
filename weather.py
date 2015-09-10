""" Program gets weather data from Weather Underground and Open Weather
    Map by given zip code. Also lists the hottest location.
"""

import requests
import os
import time
import itertools


# Overriding server time zone to user time zone.
os.environ['TZ'] = 'US/Pacific'


class Weather(object):
    """Object that stores weather data."""
    
    def __init__(self, source, zipcode, tempF, city, state=None, lastUpdatedEpoch=None):
        self.source = source
        self.zipcode = zipcode
        self.tempF = tempF
        self.city = city
        self.state = state
        self.lastUpdatedEpoch = lastUpdatedEpoch
        self.tempC = format((self.tempF - 32) * (5 / 9), '.1f')

    def __str__(self):
        debugString = 'WeatherObject(Source: {}, Zip code: {}, City: {}, State: {}, Temperature: {} [Last Update: {}])'
        return debugString.format(self.source, self.zipcode, self.city, self.state, self.tempF, self.last_updated_local())
        
    def print_weather(self):
        
        if self.state:
            displayString = '{}: The current temperature in {}, {} {} is {}F ({}C) [Last Update: {}] '
            return displayString.format(self.source,
                                        self.city,
                                        self.state,
                                        self.zipcode,
                                        self.tempF,
                                        self.tempC,
                                        self.last_updated_local())
        else:
            displayString = '{}: The current temperature in {}, {} is {}F ({}C) [Last Update: {}] '
            return displayString.format(self.source,
                                        self.city,
                                        self.zipcode,
                                        self.tempF,
                                        self.tempC,
                                        self.last_updated_local())
    
    def last_updated_local(self):
        lastUpdatedLocal = time.strftime("%B %d, %I:%M:%S %p %Z", time.localtime(self.lastUpdatedEpoch))
        return lastUpdatedLocal
        

def get_zip_codes_from_user():
    """ Returns a list of zip codes from input. """

    userZipcodeList = []
    userZipcodeString = input('Enter a comma separated list of zip codes (ex. 91801, 94107): ')
    for string in userZipcodeString.split(','):
        # Remove leading and trailing spaces
        userZipcode = string.strip()
        if userZipcode:
            if is_valid_zipcode(userZipcode):
                userZipcodeList.append(userZipcode)
            else:
                print('Error: Unexpected zipcode format: "' + userZipcode + '"')
    return userZipcodeList


def is_valid_zipcode(zipcode):
    """ Validate a zip code string."""
    
    if not zipcode.isdigit():
        return False
    if len(zipcode) != 5:
        return False
    
    # All conditions met
    return True


def request_weather_by_zipcode(zipcode, source):
    """ Input zip code string and source. Return json weather dictionary."""

    if source == 'WU':
        apiCallURLTemplate = 'http://api.wunderground.com/api/ad2e2aeab6b3e474/conditions/q/{}.json'
    elif source == 'OWM':
        apiCallURLTemplate = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&units=imperial'
    else:
        return print('Error: get_weather_by_zipcode supports only WU or OWM as source')

    apiCallURL = apiCallURLTemplate.format(zipcode)
    results = requests.get(apiCallURL)
    # Checking http response code.
    if results.status_code == 200:
        resultsDict = results.json()
        return resultsDict
    else:
        return print('Error: Unexpected http response status code:', results.status_code)


def is_valid_weather_dict(jsonDict, source):
    """Check if weather dict contains expected data. """
    
    if jsonDict is None:
        return False
        
    if source == 'WU':
        if 'current_observation' not in jsonDict:
            return False
        if 'temp_f' not in jsonDict['current_observation']:
            return False
        if 'city' not in jsonDict['current_observation']['display_location']:
            return False
        if 'state' not in jsonDict['current_observation']['display_location']:
            return False
    elif source == 'OWM':
        if 'name' not in jsonDict:
            return False
        if 'temp' not in jsonDict['main']:
            return False
    else:
        # Catch for source being unexpected/missing
        return False
            
    # All conditions met
    return True
    
            
def create_weather_object(zipcode, source):
    """ Creates weather object for given zip code."""
    if source in ['WU', 'OWM']:
        print('Fetching data for zip code', zipcode, 'from', source, '...')
        localWeatherDict = request_weather_by_zipcode(zipcode, source)
    else:
        return print('Error: source parameter unexpected/missing')
    
    if is_valid_weather_dict(localWeatherDict, source):
        if source == 'WU':
            tempF = localWeatherDict['current_observation']['temp_f']
            city = localWeatherDict['current_observation']['display_location']['city']
            state = localWeatherDict['current_observation']['display_location']['state']
            lastUpdatedEpoch = float(localWeatherDict['current_observation']['observation_epoch'])
            weatherObject = Weather(source, zipcode, tempF, city, state, lastUpdatedEpoch)
        elif source == 'OWM':
            tempF = localWeatherDict['main']['temp']
            city = localWeatherDict['name']
            lastUpdatedEpoch = float(localWeatherDict['dt'])
            weatherObject = Weather(source, zipcode, tempF, city, lastUpdatedEpoch=lastUpdatedEpoch)
    else:
        return print('Error: Unexpected', source, 'localWeatherDict contents for zipcode:"' + zipcode + '"')

    if weatherObject:
        return weatherObject
    else:
        return None


def get_warmest_weather_string_from_weather_objects(weatherObjectsList):
    """ Select object with highest temperature and construct output string.
    """
    highestDisplayString = ''
    if not weatherObjectsList:
        return print('Error: weatherObjectsList is None')
    
    # Setting first object as basis for iterative comparison.    
    highestTemp = weatherObjectsList[0].tempF
    for weatherObject in weatherObjectsList:
        if weatherObject.tempF >= highestTemp:
            highestTemp = weatherObject.tempF
            
            # Supporting object with and without State attribute
            if weatherObject.state:
                highestDisplayString = '{}, {} {} has the highest temperature of {}F'
                highestDisplayString = highestDisplayString.format(weatherObject.city,
                                                                   weatherObject.state,
                                                                   weatherObject.zipcode,
                                                                   weatherObject.tempF)

            else:
                highestDisplayString = '{}, {} has the highest temperature of {}F'
                highestDisplayString = highestDisplayString.format(weatherObject.city,
                                                                   weatherObject.zipcode,
                                                                   weatherObject.tempF)

    return highestDisplayString

    
def get_recent_weather_objects(weatherObjectsList):
    """ Return a list of weather objects for same location where
        lastUpdatedEpoch is most recent.
    """
    
    if not weatherObjectsList:
        return print('Error: weatherObjectsList is empty')
    
    recentWeatherObjectList = []
    # Compare objects to each other without duplication
    for weatherObject, weatherObjectOther in itertools.combinations(weatherObjectsList, 2):
         # Compare only same zip codes from different sources.
         if (weatherObject.zipcode == weatherObjectOther.zipcode and
                weatherObject.source != weatherObjectOther.source):
            # Add most recent zip code to the recent objects list.
            if weatherObject.lastUpdatedEpoch >= weatherObjectOther.lastUpdatedEpoch:
                recentWeatherObjectList.append(weatherObject)
            else:
                recentWeatherObjectList.append(weatherObjectOther)
        
    zipCodeList = []
    for weatherObject in recentWeatherObjectList:
        zipCodeList.append(weatherObject.zipcode)
    
    # Catch a list with only one zip code or returned from only one source.
    for weatherObject in weatherObjectsList:
        if weatherObject.zipcode not in zipCodeList:
            recentWeatherObjectList.append(weatherObject)
    
    if recentWeatherObjectList:
        return recentWeatherObjectList
    else:
        return print('Error: recentWeatherObjectList is empty')
    
    
def main():
    
    # Get list of zip codes from input.
    userZipcodeList = get_zip_codes_from_user()
    
    # Create weatherObject list and add WU and OWM objects.
    weatherObjectsList = []
    for userZipcode in userZipcodeList:
        weatherObject = create_weather_object(userZipcode, source='WU')
        if weatherObject:
            weatherObjectsList.append(weatherObject)
        weatherObject = create_weather_object(userZipcode, source='OWM')
        if weatherObject:
            weatherObjectsList.append(weatherObject)
    print('')
   
    # Print most recent weather objects from weatherObjectsList.
    recentWeatherObjectList = get_recent_weather_objects(weatherObjectsList)
    for weatherObject in recentWeatherObjectList:
        print(weatherObject.print_weather())
    print('')
    
    # Print warmest weather
    print(get_warmest_weather_string_from_weather_objects(recentWeatherObjectList))

main()
