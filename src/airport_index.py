import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from datetime import datetime
import mpu

def convert_airport_numbers(ap):
    ap.pax = int(ap.pax.replace(',', ''))
    ap.domestic = int(ap.domestic.replace(',', ''))
    ap.international = int(ap.international.replace(',', ''))
    return ap 

def extract_airports(fn="./data/Airports.csv"):
    df = pd.read_csv(fn)
    df = df.apply(convert_airport_numbers, axis=1)
    return df

def fix_state_abbr_geo(row):
    row['State'] = get_state(row['State'])
    return row

def fix_county_latlon(county):
    county['Lat'] = float(county['Lat'])
    county['Lon'] = float(county['Lon'].replace('–','-'))
    return county 

def extract_geography(fn="./data/County Physical.csv"):
    df = pd.read_csv(fn, sep='\t')
    df = df.apply(fix_state_abbr_geo, axis=1)
    df['sc'] = df['State'] + ':' + df['County']
    #df['fips'] = df['FIPS']
    return df

def calc_intl_arrivals_index(lat, lon, threshold, airports_df):
    domestic = 0
    intl = 0
    airports = []
    for i, airport in airports_df.iterrows():
        #print(airport)
        alat = airport['lat']
        alon = airport['lon']
        dist = mpu.haversine_distance((lat, lon), (alat, alon))
        #print('{} is {} km away'.format(airport['airport'], dist))
        if dist < threshold:
            divisor = 1 #(dist - 20)**2
            intl += int(airport['international'])/divisor
            domestic += int(airport['domestic'])/divisor
            airports.append(airport['airport'])
    return float(intl), float(domestic), airports

def calc_intl_arrivals_index2(lat, lon, threshold1, threshold2, airports_df):
    domestic = 1
    intl = 1
    airports = []
    for i, airport in airports_df.iterrows():
        #print(airport)
        alat = airport['lat']
        alon = airport['lon']
        dist = mpu.haversine_distance((lat, lon), (alat, alon))
        #print('{} is {} km away'.format(airport['airport'], dist))
        if dist < threshold2:
            if dist < threshold1:
                #print('here')
                intl += int(airport['international'])
                domestic += int(airport['domestic'])
            else:
                factor = (threshold2 - dist)/(threshold2-threshold1)
                intl += factor*int(airport['international'])
                domestic += factor*int(airport['domestic'])
                #print('dist: {}, t1: {}, t2: {}, factor: {}'.format(dist, threshold1, threshold2, factor))
                #print('n: {}, d: {}'.format(threshold2 - dist, threshold2 - threshold1))
            airports.append(airport['airport'])
    return float(intl), float(domestic), airports    
        
def build_intl_arrivals_index_df(counties_df, airports_df, threshold):
    res = pd.DataFrame(columns=['sc', 'international', 'domestic', 'airports'])
    for i, county in counties_df.iterrows():
        intl, domestic, airports = calc_intl_arrivals_index(county['Lat'], float(county['Lon']), threshold, airports_df)
        res.loc[i] = [county['sc'], intl, domestic, airports]
    return res
 
def build_intl_arrivals_index_df2(counties_df, airports_df, threshold1, threshold2):
    res = pd.DataFrame(columns=['sc', 'fips', 'international', 'domestic', 'airports'])
    for i, county in counties_df.iterrows():
        intl, domestic, airports = calc_intl_arrivals_index2(county['Lat'], float(county['Lon']), threshold1, threshold2, airports_df)
        res.loc[i] = [county['sc'], county['FIPS'], intl, domestic, airports]
    return res

def get_state(code):
    return states[code]

states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}

