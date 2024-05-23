import requests
import pandas as pd



# ------University master data (API)--------

api_url = "http://universities.hipolabs.com/search"

response = requests.get(api_url)

data = response.json()

df = pd.DataFrame(data, columns=['country','web_pages','alpha_two_code','domains','state-province','name'])


print(df)