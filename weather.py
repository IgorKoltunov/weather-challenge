""" Program gets weather data from Weather Underground and Open Weather
    Map by given zip code. Also lists the hottest location.
"""

import requests
import os
import time
import itertools
import argparse


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
        return debugString.format(self.source,
                                  self.zipcode,
                                  self.city,
                                  self.state,
                                  self.tempF,
                                  self.last_updated_local())

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


def get_zip_codes_from_input():
    """ Returns a list of zip codes from input.
    :rtype: list
    """

    inputZipcodeList = []
    inputZipcodeString = input('Enter a comma separated list of zip codes (ex. 91801, 94107): ')
    for string in inputZipcodeString.split(','):
        # Remove leading and trailing spaces
        inputZipcode = string.strip()
        if inputZipcode:
            if is_valid_zipcode(inputZipcode):
                if inputZipcode not in inputZipcodeList:
                    inputZipcodeList.append(inputZipcode)
            else:
                print('Error: Unexpected zipcode format: "' + inputZipcode + '"')
    return inputZipcodeList


def get_zip_codes_from_cli(cliZipCodeString):
    """ Returns a list of zip codes from command line interface.
    :rtype: list
    """
    print('Parsing zip codes from the command line...')
    cliZipCodeList = []
    for string in cliZipCodeString.split(','):
        # Remove leading and trailing spaces, if any
        cliZipCode = string.strip()
        if cliZipCode:
            if is_valid_zipcode(cliZipCode):
                if cliZipCode not in cliZipCodeList:
                    cliZipCodeList.append(cliZipCode)
            else:
                print('Error: Unexpected zipcode format: "' + cliZipCode + '"')
    if len(cliZipCodeList) > 0:
        return cliZipCodeList
    else:
        print('Warning: You did not provide any valid zip codes via CLI. You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList


def get_zip_codes_from_file(zipCodeFilePath):
    """ Returns a list of zip codes from specified file.
        :rtype: list
    """
    if not os.path.isfile(zipCodeFilePath):
        print('Warning: File (' + zipCodeFilePath + ') is not found. You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList

    print('Parsing zip codes from the zipCodeFile...')
    fileZipCodeList = []
    with open(zipCodeFilePath, 'r') as zipCodeFile:
        lineList = zipCodeFile.read().splitlines()
    for line in lineList:
        fileZipCodes = line.split(',')
        for string in fileZipCodes:
            # Remove leading and trailing spaces, if any
            fileZipCode = string.strip()
            if fileZipCode:
                if is_valid_zipcode(fileZipCode):
                    if fileZipCode not in fileZipCodeList:
                        fileZipCodeList.append(fileZipCode)
                else:
                    print('Error: Unexpected zipcode format: "' + fileZipCode + '"')

    if len(fileZipCodeList) > 0:
        return fileZipCodeList
    else:
        print('Warning: File (' + zipCodeFilePath + ') did not contain any valid zip codes. '
                                                    'You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList


def is_valid_zipcode(zipcode):
    """ Validate a zip code string.
        :rtype: bool
    """

    if not zipcode.isdigit():
        return False
    if len(zipcode) != 5:
        return False

    # All conditions met
    return True


def request_weather_by_zipcode(zipcode, source):
    """ Input zip code string and source. Return json weather dictionary.
        :rtype: dict
    """

    if source == 'WU':
        apiCallURLTemplate = 'http://api.wunderground.com/api/ad2e2aeab6b3e474/conditions/q/{}.json'
    elif source == 'OWM':
        apiCallURLTemplate = ('http://api.openweathermap.org/data/2.5/weather?zip={},'
                              'us&units=imperial&APPID=054e25024677f112bd568c62ca61d79c')
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
    """Check if weather dict contains expected data.
        :rtype: bool
    """

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
    """ Creates weather object for given zip code.
        :rtype: object
    """

    weatherObject = None
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
        :rtype: string
    """
    # ToDo: handle the case where there is only one object

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
    """ Compile a list of weather objects for same location where
        lastUpdatedEpoch is most recent.
        :rtype: list
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
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Weather Challenge')
    parser.add_argument('-zl', '--zipCodeList', help='Provide a list of comma separated zip codes', required=False, metavar='')
    parser.add_argument('-zf', '--zipCodeFile', help='Provide a file name containing a list of comma separated zip codes', required=False,
                        metavar='')
    args = vars(parser.parse_args())

    if args['zipCodeList'] and args['zipCodeFile']:
        return print('Error: Only one optional argument expected. Use -h for help.')
    if args['zipCodeList']:
        # zipCodeList was supplied on the command line

        zipCodeList = get_zip_codes_from_cli(args['zipCodeList'])
    elif args['zipCodeFile']:
        # zipCode list was supplied in a file
        zipCodeList = get_zip_codes_from_file(args['zipCodeFile'])
    else:
        # Get list of zip codes from input.
        zipCodeList = get_zip_codes_from_input()

    # Create weatherObject list and add WU and OWM objects.
    weatherObjectsList = []
    for zipCode in zipCodeList:
        weatherObject = create_weather_object(zipCode, source='WU')
        if weatherObject:
            weatherObjectsList.append(weatherObject)
        weatherObject = create_weather_object(zipCode, source='OWM')
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
