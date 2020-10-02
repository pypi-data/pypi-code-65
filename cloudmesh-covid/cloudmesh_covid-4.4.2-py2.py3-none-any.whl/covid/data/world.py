#
# gets the data from the virustracker.com via a REST call
#

import requests
import pandas as pd

def get_covid_country_data():

  #download the data from he virustracker
  res = requests.get('https://api.thevirustracker.com/free-api?countryTotals=ALL')
  data = res.json()

  # prepare the country data as a dataframe
  country_data = data['countryitems'][0]
  df = pd.DataFrame(country_data).transpose()
  df = df.drop('stat') # remove the row 'stats'
  df.index.astype('int64') # make the index an integer
  df = df.drop(columns=['source', 'ourid']) # drop columns id, souurce, ourid
  # rename the countries for folium
  df.replace('USA', "United States of America", inplace = True)
  df.replace('Tanzania', "United Republic of Tanzania", inplace = True)
  df.replace('Democratic Republic of Congo', "Democratic Republic of the Congo", inplace = True)
  df.replace('Congo', "Republic of the Congo", inplace = True)
  df.replace('Lao', "Laos", inplace = True)
  df.replace('Syrian Arab Republic', "Syria", inplace = True)
  df.replace('Serbia', "Republic of Serbia", inplace = True)
  df.replace('Czechia', "Czech Republic", inplace = True)
  df.replace('UAE', "United Arab Emirates", inplace = True)
  # change title column to country column, so its easier to access when processing
  df = df.rename(columns={'title':'country'})
  return df
