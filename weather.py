""" Challenge 5.
    Objects! We will know be working with WeatherObjects to slowly move us
    away from being dependent on just WeatherUnderground. Refactor your
    code to have the same functionality as before but the api response
    for each zip code should be converted to a WeatherObject.

    Your WeatherObject needs to be a class that inits with a few properties
    and a few methods. The WeatherObject needs to have:

    a zip code property
    a temperature property
    a city property
    a state property
    a last updated property

    For debugging, displaying your object in code through python's print
    should display:
    WeatherObject(Zip Code: <ZIP CODE HERE>, City <CITY HERE>,
                 State <STATE HERE>Temperature: <TEMP HERE>)

    Calling a new print_weather() method in this class should pretty print
    the object to standard output but with a few additions as shown in the
    screenshot. For debugging, anytime print_weather() is called, have it
    also print the WeatherObject() info from the last paragraph.

    The celsius value of the temperature should be calculated from the
    temperature of the object and should not be set from any api response.
"""


from requests import get


class Weather(object):
    """Creates a weather object from weather data dictionary."""
    
    def __init__(self, localWeatherDict):
    """Init with a dictionary. Currently Weather Underground is supported."""
        self.localWeatherDict = localWeatherDict
    
    def __str__(self):
    """Overriding default print(Weather) behaviour for debugging"""
        debugString = 'WeatherObject(Zip code: {}, City: {}, State: {}, Temperature: {})'
        zip = self.getLocation('Zip Code')
        city = self.getLocation('City')
        state = self.getLocation('State')
        temp = self.getTemp('F')
        
        return debugString.format(zip, city, state, temp)
              
    def getLocation(self, locationFormat=None):
    """Method returns location data from the object.
    
    Keyword Parameter:
    locationFormat -- type of location requested (default None)
    """
        if not locationFormat:
            city = self.localWeatherDict['current_observation']['display_location']['city']
            state = self.localWeatherDict['current_observation']['display_location']['state']
            zip = self.localWeatherDict['current_observation']['display_location']['zip']
            return city + ', ' + state + ' ' + zip
        elif locationFormat == 'City':
            return self.localWeatherDict['current_observation']['display_location']['city']
        elif locationFormat == 'State':
            return self.localWeatherDict['current_observation']['display_location']['state']
        elif locationFormat == 'Zip Code':
            return self.localWeatherDict['current_observation']['display_location']['zip']
        else:
            raise RuntimeError('getLocation(type) optional paramter is unexpected')
    
    def getTemp(self, tempFormat=None):
    """Method returns temperature from the object.
    
    Keyword Parameter:
    tempFormat -- type of units preferred (default None)
    """
        if not tempFormat:
            return self.localWeatherDict['current_observation']['temperature_string']
        elif tempFormat == 'F':
            return self.localWeatherDict['current_observation']['temp_f']
        elif tempFormat == 'C':
            fTemp = self.localWeatherDict['current_observation']['temp_f']
            mycTemp = (fTemp - 32) * (5 / 9)
            mycTemp = format(mycTemp, '.1f')
            return mycTemp
        else:
            raise RuntimeError('getTemp(format) optional paramter is unexpected')
    
    def lastUpdated(self):
    """Method returns time of the weather observation from the object"""
        return self.localWeatherDict['current_observation']['observation_time']      


def get_weather_by_zipcode(zipcode):
    """Input zip code string. Output json dict."""
    
    apiKey = 'ad2e2aeab6b3e474'
    apiCallURLTemplate = 'http://api.wunderground.com/api/{}/conditions/q/{}.json'
    apiCallURL = apiCallURLTemplate.format(apiKey, zipcode)
         
    results = get(apiCallURL)
    # ToDo: Need to handle a bad URL/Server down. Causes ugly error right now.
    
    resultsDict = results.json()
    return resultsDict


def is_valid_weather(jsonDict):
    """original function written was Mark P."""
    if jsonDict is None:
        return False
    if 'current_observation' not in jsonDict:
        return False
    if 'temp_f' not in jsonDict['current_observation']:
        return False
    if 'city' not in jsonDict['current_observation']['display_location']:
        return False
    if 'state' not in jsonDict['current_observation']['display_location']:
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


def main():
    
    userZipcodeList = []
    highestTemp = 0
    highestDisplayString = ''
    
    userZipcodeString = input('Enter a comma separated list of zipcodes: ')
    for string in userZipcodeString.split(','):
        userZipcode = string.strip()
        if userZipcode: userZipcodeList.append(userZipcode)
     
    for userZipcode in userZipcodeList:
        
        # return error if unexpected format
        if not is_valid_zipcode(userZipcode):
            print('Error: Unexpected zipcode format: "' + userZipcode + '"')
        else:
            localWeatherDict = get_weather_by_zipcode(userZipcode)
                                    
            # return error if dict contents are unexpected 
            if not is_valid_weather(localWeatherDict):
                print('Error: Unexpected localWeatherDict contents for zipcode: "' + userZipcode + '"') 
            else:
                weatherObject = Weather(localWeatherDict)
                tempF = weatherObject.getTemp('F')
                tempC = weatherObject.getTemp('C')
                city = weatherObject.getLocation('City')
                state = weatherObject.getLocation('State')
                lastUpdated = weatherObject.lastUpdated()
                
                if tempF > highestTemp:
                    highestTemp = tempF
                    highestDisplayString = '{}, {} {} has the highest temperature of {}F'.format(city,
                                                                                                 state,
                                                                                                 userZipcode,
                                                                                                 tempF)

                displayString = 'The current temperature in {}, {} {} is {}F ({}C) '.format(city,
                                                                                            state,
                                                                                            userZipcode,
                                                                                            tempF,
                                                                                            tempC)
                print('Fetching data for zip code ' + userZipcode + '...')
                print(weatherObject)
                print(displayString, end='')
                print('[' + lastUpdated + ']')

    if highestDisplayString: print('\n' + highestDisplayString)

main()
