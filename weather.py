""" Program gets weather data from Weather Underground and Open Weather
    Map by given zip code. Also lists the hottest location.
"""

import requests
import os
import time
import itertools
import argparse
import sys
import logging

# Overriding server time zone to user time zone.
os.environ['TZ'] = 'US/Pacific'

# Specify Maximum zip codes allowed
MAX_ZIP_CODES_ALLOWED = 10


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
    logging.info('Requesting zip codes from input().')
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
                logging.error('Error: Unexpected zipcode format: "{}".'.format(inputZipcode))
                print('Error: Unexpected zipcode format: "' + inputZipcode + '"')

    return inputZipcodeList


def get_zip_codes_from_cli(cliZipCodeString):
    """ Returns a list of zip codes from command line interface.

    :rtype: list
    """
    logging.info('Parsing zip codes from the command line.')
    cliZipCodeList = []
    for string in cliZipCodeString.split(','):
        # Remove leading and trailing spaces, if any
        cliZipCode = string.strip()
        if cliZipCode:
            if is_valid_zipcode(cliZipCode):
                if cliZipCode not in cliZipCodeList:
                    cliZipCodeList.append(cliZipCode)
            else:
                logging.error('Unexpected zipcode format: "{}".'.format(cliZipCode))
                print('Error: Unexpected zipcode format: "' + cliZipCode + '"')
    if cliZipCodeList:
        return cliZipCodeList
    else:
        logging.warning('No valid zip codes provided via command line arguments. Falling back to input().')
        print('Warning: You did not provide any valid zip codes via CLI. You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList


def get_zip_codes_from_file(zipCodeFilePath):
    """ Returns a list of zip codes from specified file.

        :rtype: list
    """
    if not os.path.isfile(zipCodeFilePath):
        logging.warning('File ({}) is not found. Falling back to input().'.format(zipCodeFilePath))
        print('Warning: File (' + zipCodeFilePath + ') is not found. You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList
    
    logging.info('Parsing zip codes from the zipCodeFile.')
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
                    logging.error('Unexpected zipcode format: "{}".'.format(fileZipCode))
                    print('Error: Unexpected zipcode format: "' + fileZipCode + '"')

    if fileZipCodeList:
        return fileZipCodeList
    else:
        logging.warning('File ({}) did not contain any valid zip codes. '
                        'Falling back to input().'.format(zipCodeFilePath))
        print('Warning: File (' + zipCodeFilePath + ') did not contain any valid zip codes. '
                                                    'You can enter zip code(s) manually.')
        inputZipCodeList = get_zip_codes_from_input()
        return inputZipCodeList


def is_valid_zipcode(zipCode):
    """ Validate a zip code string.

        :rtype: bool
    """

    if not zipCode.isdigit():
        logging.debug('Zip code ({}) is not all digits.'.format(zipCode))
        return False
    if len(zipCode) != 5:
        logging.debug('Zip code ({}) is not 5 digits.'.format(zipCode))
        return False
    if zipCode < '00501' or zipCode > '99950':
        logging.debug('Zip code ({}) is not within expected range'.format(zipCode))
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
        logging.error('Only WU or OWM supported as API source. Provided:"{}"'.format(source))
        return None

    apiCallURL = apiCallURLTemplate.format(zipcode)
    logging.debug('Making API call: "{}"'.format(apiCallURL))
    results = requests.get(apiCallURL)
    # Checking http response code.
    if results.status_code == 200:
        resultsDict = results.json()
        return resultsDict
    else:
        logging.error('Unexpected http response status code:"{}"'.format(results.status_code))
        return None


def is_valid_weather_dict(jsonDict, source):
    """Check if weather dict contains expected data.

        :rtype: bool
    """
    # ToDo: Add debug logging to function
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
        if 'dt' not in jsonDict:
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
        logging.info('Fetching data for zip code {} from {}.'.format(zipcode, source))
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
        logging.error('weatherObjectsList is empty')
        return None
    
    logging.debug('Comparing Weather Objects to pick latest.')
    recentWeatherObjectList = []
    # Compare objects to each other without duplication.
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
        logging.error('recentWeatherObjectList is empty')
        return None


def parse_cli_args():
    """ Setup command line arguments.
    
        :rtype: dict
    """
     
    parser = argparse.ArgumentParser(description='Weather Challenge')
    parser.add_argument('-zl', '--zipCodeList',
                        help='Provide a list of comma separated zip codes.',
                        required=False, metavar='')
    parser.add_argument('-zf', '--zipCodeFile',
                        help='Provide a file name containing a list of comma separated zip codes.',
                        required=False, metavar='')
    parser.add_argument('-v', '--verbose',
                        help='Set flag to see verbose output in weather.log file.',
                        required=False, action='store_true')
    parser.add_argument('-d', '--debug',
                        help='Specify this flag to see verbose output.',
                        required=False, action='store_true')
    args = vars(parser.parse_args())

    return args


def create_zip_code_list(args):
    """ Create a list of zip codes based on command line arguments or input.
        
        :rtype: list
    """
    if args['zipCodeList'] and args['zipCodeFile']:
        logging.error('Both --zipCodeList and --zipCodeFile command line arguments provided.')
        sys.exit('Error: Only one optional argument expected. Use -h for help.')

    if args['zipCodeList']:
        # zipCodeList was supplied on the command line
        logging.debug('zipCodeList was supplied as command line argument')
        zipCodeList = get_zip_codes_from_cli(args['zipCodeList'])
    elif args['zipCodeFile']:
        # zipCode list was supplied in a file
        logging.debug('zipCodeList was supplied as a file on the command line.')
        zipCodeList = get_zip_codes_from_file(args['zipCodeFile'])
    else:
        # Get list of zip codes from input.
        logging.debug('zipCode list was not provided on the command line. Getting from input().')
        zipCodeList = get_zip_codes_from_input()

    if zipCodeList:
        restrictedZipCodeList = restrict_zip_code_list_to_max_len(zipCodeList)
        return restrictedZipCodeList
    else:
        logging.critical('zipCodeList is None. Exiting.')
        sys.exit('No valid zip codes have been provided.')


def restrict_zip_code_list_to_max_len(zipCodeList): 
    """ Check number of requested zip codes against maximum allowed.
        
        :rtype: list
    """
    numZipCodes = len(zipCodeList)
    if numZipCodes > MAX_ZIP_CODES_ALLOWED:
        # Zip Code List is over the allowed limit. Trim to conform.
        errorStringTemplate = ('Too many unique zip codes requested ({}). ' 
                               'Getting data for max allowed ({}).')
                               
        logging.error(errorStringTemplate.format(numZipCodes, MAX_ZIP_CODES_ALLOWED))
        allowedIndex = 0
        restrictedZipCodeList = []   
        
        while allowedIndex < MAX_ZIP_CODES_ALLOWED:
            restrictedZipCodeList.append(zipCodeList[allowedIndex])
            allowedIndex += 1 
        return restrictedZipCodeList
    else:
        # Zip Code List is under max allowed. No changes needed.
        return zipCodeList


def setup_logging(args):
    """ Setup logging and set level and options based on command line input.
    
        :rtype: None
    """
    
    if args['verbose'] and args['debug']:
        sys.exit('Error: Only one optional flag expected. Use -h for help.')
    
    # If -v flag is used: set logging level to DEBUG and write log to file.
    if args['verbose']:
        logging.basicConfig(format='%(asctime)s - %(funcName)s - %(levelname)s: %(message)s',
                            filename='weather.log', level=logging.DEBUG)
    
    # If -d flag is used: set logging level to DEBUG and write to output.
    if args['debug']:
        logging.basicConfig(format='%(asctime)s - %(funcName)s - %(levelname)s: %(message)s',
                            level=logging.DEBUG)                          

    # If no flags are used: set logging level to WARNING and write log to file.
    else:
        logging.basicConfig(format='%(asctime)s - %(funcName)s - %(levelname)s: %(message)s',
                            filename='weather.log', level=logging.WARNING)
    
    # Setting requests library specific logging level
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.debug('Logging is ready for use.')


def create_weather_object_list(zipCodeList, sourceList):
    """ Create weather object list based on zip code and source list.

    :rtype: list
    """

    weatherObjectsList = []
    for zipCode in zipCodeList:
        for source in sourceList:
            weatherObject = create_weather_object(zipCode, source)
            if weatherObject:
                weatherObjectsList.append(weatherObject)  
    
    if not weatherObjectsList:
        logging.critical('No valid weather objects in the weatherObjectsList')
        sys.exit('Error: No valid weather returned')
    
    return weatherObjectsList


def main():
    
    # Parse Command Line Arguments into a dictionary.
    args = parse_cli_args()
    
    # Set up logging
    setup_logging(args)

    # Compile zip code list 
    zipCodeList = create_zip_code_list(args)
    
    # Create weatherObject list and add WU and OWM objects.
    weatherObjectsList = create_weather_object_list(zipCodeList, ['WU', 'OWM'])
    print('')

    # Print most recent weather objects from weatherObjectsList.
    recentWeatherObjectList = get_recent_weather_objects(weatherObjectsList)
    for weatherObject in recentWeatherObjectList:
        print(weatherObject.print_weather())
    print('')

    # Print warmest weather
    print(get_warmest_weather_string_from_weather_objects(recentWeatherObjectList))
    
    # Log normal program finish
    logging.debug('Program execution finished')

main()
