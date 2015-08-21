''' Challenge 4.
    Expand the weather tool to take in a comma-separated list of zip codes as user input. 
    Validate that each user inputted item is a zip code and if it is, fetch the weather for
    that zip and print it out the same way as before. Handle some obvious bad user input 
    conditions. Once all the weather conditions have been displayed to the user, print out 
    a line telling the user which of the inputed zip codes currently has the warmest weather.

    The data set that should be accounted for includes this '94110,12345,80123,99999,abcde, 90040,4321'
    
    Output example:
    Enter a comma separated list of zipcodes 23123,123123,123123
    Feathing data for zipcode x....
    The temperature in <city>, <State> (zip) is <temp_f>F
    ...
    invalid weather data for zipcode...
    ....
    invalid zipcode
    ....
    City, State (zip) has the warmest weather of temp
'''

from requests import get, codes

def get_weather_by_zipcode(zipcode):
    '''Input zipcode int. Output json dict.'''
    
    apiKey = 'ad2e2aeab6b3e474'
    apiCallURLTemplate = 'http://api.wunderground.com/api/{}/conditions/q/{}.json'
    apiCallURL = apiCallURLTemplate.format(apiKey, zipcode)
    resultsDict = dict()
         
    results = get(apiCallURL)
    # ToDo: Need to handle a bad URL/Server down. Causes ugly error right now.
    
    resultsDict =  results.json()
    return resultsDict

def is_valid_weather(jsonDict):
    '''original function written was Mark P.'''
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
    
    if zipcode.isdigit() == False:
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
    for str in userZipcodeString.split(','):
        userZipcode = str.strip()
        if userZipcode: userZipcodeList.append(userZipcode)
     
    for userZipcode in userZipcodeList:
        
        # return error if unexpected format
        if is_valid_zipcode(userZipcode) == False: 
            print('Error: Unexpected zipcode fomrat: "' + userZipcode +'"')
        else:
            localWeatherDict = get_weather_by_zipcode(userZipcode)
            
            # return error if dict contents are unexpected 
            if is_valid_weather(localWeatherDict) == False:
                print('Error: Unexpected localWeatherDict contents for zipcode: "' + userZipcode + '"') 
            else:       
                temperature =  localWeatherDict['current_observation']['temp_f']
                city = localWeatherDict['current_observation']['display_location']['city']
                state = localWeatherDict['current_observation']['display_location']['state'] 
                if temperature > highestTemp:
                    highestTemp = temperature
                    highestDisplayString = '{}, {} {} has the highest temperature of {}F'.format(city, state, userZipcode, temperature)
                displayString = 'The current temperature in {}, {} {} is {}F'.format(city, state, userZipcode, temperature)
                print(displayString)
    if highestDisplayString: print('\n' + highestDisplayString)   
    
        
main()
