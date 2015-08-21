''' Part 1: Use the weather underground api to display current 
    temperature for given zipcode. Zipcode needs to be a global
    variable. Create a function that takes zipcode as an argument
    and returns the json. Program should return temp in a user 
    friendly matter.
    
    Script needs to have basic error handling and on sucess print out
    'The current temperature in <City>, <State> is <temperature in fahrenheit>F'
    If it fails, it should print out 'There was an error. Try again later'
'''

from requests import get


def get_weather_by_zipcode(zipcode):
    '''Input zipcode int. Output json dic.'''
    apiKey = 'ad2e2aeab6b3e474'
    apiCallURLTemplate = 'http://api.wunderground.com/api/{}/conditions/q/{}.json'
    apiCallURL = apiCallURLTemplate.format(apiKey, zipcode)
    resultsDict = dict()
    
    # return error if non numeric input 
    if zipcode.isdigit() == False: 
        return print('Error: non digit zipcode entered')
         
    results = get(apiCallURL)
    resultsDict =  results.json()
    return resultsDict
    
def main():
    
    userZipcode = input('Enter a Zipcode: ')
    
    localWeatherDict = get_weather_by_zipcode(userZipcode)
    
    print(localWeatherDict['current_observation']['temp_f'])


main()
