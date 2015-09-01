""" Refactored weather object code.
"""

import requests
import time
import os


class Weather(object):
    """Object that stores weather data."""
    
    def __init__(self, zipcode, tempF, city=None, state=None, lastUpdated=None):
        self.zipcode = zipcode
        self.tempF = tempF
        self.city = city
        self.state = state
        self.lastUpdated = lastUpdated
        
    def __str__(self):
        debugString = 'WeatherObject(Zip code: {}, City: {}, State: {}, Temperature: {})'
        return debugString.format(self.zipcode, self.city, self.state, self.tempF)
        
    def print_weather(self):
        
        tempC = convert_temp_to(self.tempF, 'C')
        if self.state:
            displayString = 'The current temperature in {}, {} {} is {}F ({}C) [{}] '
            return displayString.format(self.city, self.state, self.zipcode, self.tempF, tempC, self.lastUpdated) 
        else:
            displayString = 'The current temperature in {}, {} is {}F ({}C) [{}] '
            return displayString.format(self.city, self.zipcode, self.tempF, tempC, self.lastUpdated) 
            

def get_weather_by_zipcode(zipcode, apiCallURLTemplate):
    """Input zip code string and API call URL Output json dict."""
    
    apiCallURL = apiCallURLTemplate.format(zipcode)
         
    results = requests.get(apiCallURL)
    # ToDo: Need to handle a bad URL/Server down. Causes ugly error right now.
    
    resultsDict = results.json()
    return resultsDict


def is_valid_weather(jsonDict, source):
    """original function written was Mark P."""
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
    if source == 'OWM':
        if 'name' not in jsonDict:
            return False
        if 'temp' not in jsonDict['main']:
            return False
    # All conditions met
    return True


def is_valid_zipcode(zipcode):
    """Simple zip code validator."""
    
    if not zipcode.isdigit():
        return False
    if len(zipcode) != 5:
        return False
    
    # All conditions met
    return True

    
def convert_temp_to(temp, desiredFormat):
    """Convert temperature to specified format"""

    if desiredFormat == 'C':
        tempC = (temp - 32) * (5 / 9)
        tempC = format(tempC, '.1f')
        return tempC
    if desiredFormat == 'F':
        tempF = temp * 9/5 + 32
        tempF = format(tempF, '.1f')
        return tempF
    return print('Error: convert_temp function expects C or F as second parameter')


def print_warmest_weather(weatherObjectsList):
    highestTemp = 0
    highestDisplayString = ''
    if not weatherObjectsList:
        return print('Error: weatherObjectsList is empty')

    for weatherObject in weatherObjectsList:
        if weatherObject.tempF > highestTemp:
            highestTemp = weatherObject.tempF
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
            
    return print(highestDisplayString)
    

def main():
    
    userZipcodeList = []
    weatherObjectsList = []

    userZipcodeString = input('Enter a comma separated list of zip codes: ')
    for string in userZipcodeString.split(','):
        userZipcode = string.strip()
        if userZipcode:
            userZipcodeList.append(userZipcode)
     
    for userZipcode in userZipcodeList:
        
        # return error if unexpected format
        if not is_valid_zipcode(userZipcode):
            print('Error: Unexpected zipcode format: "' + userZipcode + '"')
        else:
            print('Fetching data for zip code ' + userZipcode + ' from WU...')
            apiCallURLTemplate = 'http://api.wunderground.com/api/ad2e2aeab6b3e474/conditions/q/{}.json'
            localWeatherDict = get_weather_by_zipcode(userZipcode, apiCallURLTemplate)
                                    
            # return error if dict contents are unexpected 
            if not is_valid_weather(localWeatherDict, source='WU'):
                print('Error: Unexpected WU localWeatherDict contents for zipcode: "' + userZipcode + '"') 
            else:
                tempF = localWeatherDict['current_observation']['temp_f']
                city = localWeatherDict['current_observation']['display_location']['city']
                state = localWeatherDict['current_observation']['display_location']['state']
                lastUpdatedEpochWU = float(localWeatherDict['current_observation']['observation_epoch'])
                lastUpdated = localWeatherDict['current_observation']['observation_time']
                
                weatherObject = Weather(userZipcode, tempF, city, state, lastUpdated)
                weatherObjectsList.append(weatherObject)
            
            print('Fetching data for zip code ' + userZipcode + ' from OWM...')
            apiCallURLTemplate = 'http://api.openweathermap.org/data/2.5/weather?zip={},us&units=imperial'
            localWeatherDict = get_weather_by_zipcode(userZipcode, apiCallURLTemplate) 
            
            if not is_valid_weather(localWeatherDict, source='OWM'):
                print('Error: Unexpected OWM localWeatherDict contents for zipcode: "' + userZipcode + '"') 
            else:
                tempF = localWeatherDict['main']['temp']
                city = localWeatherDict['name']
                state = None
                lastUpdatedEpochOWM = float(localWeatherDict['dt'])
                os.environ['TZ'] = 'US/Pacific'
                lastUpdated = time.strftime("%B %d, %H:%M %p %Z", time.localtime(lastUpdatedEpochOWM))
                
                if lastUpdatedEpochWU < lastUpdatedEpochOWM:
                    weatherObjectsList.remove(weatherObject)
                    weatherObject = Weather(userZipcode, tempF, city, state, lastUpdated)
                    weatherObjectsList.append(weatherObject)
                 
    for weatherObject in weatherObjectsList:
        print(weatherObject.print_weather())
    print('')
    print_warmest_weather(weatherObjectsList)
    
main()
