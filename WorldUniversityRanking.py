import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv

#api_url = "http://universities.hipolabs.com/search"

#response = requests.get(api_url)

#data = response.json()

#df = pd.DataFrame(data, columns=['country','web_pages','alpha_two_code','domains','state-province','name'])


#print(df)


url = "https://www.timeshighereducation.com/world-university-rankings/2024/world-ranking#!/length/-1/sort_by/rank/sort_order/asc/cols/stats"  

# Send a GET request to the webpage
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Find the table containing the rankings
table = soup.find('table')  # Adjust the selector if necessary

# If table is not found, print an error message and exit
if table is None:
    print("Error: No table found on the page.")