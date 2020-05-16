import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from datetime import datetime
import mpu
import re


def strip_state(row):
    row['state'] = row['state'].strip()
    row['county'] = row['county'].strip()
    return row

def fix_nyt(row):
    row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
    row['fips'] = int(row['fips'])
    return row

def extract_nyt(fn="./data/covid-19-data/us-counties.csv"):
    df = pd.read_csv(fn)
    #df['sc'] = df['state'] + ':' + df['county']
    df = df[df['cases'] > 0]
    df = df[df['fips'] > 0]
    df['fips'].fillna(0, inplace=True)
    df = df.apply(fix_nyt, axis=1)
    df = df.apply(strip_state, axis=1)
    return df[['fips', 'date', 'deaths', 'cases']]

def extract_full_nyt(fn="./data/covid-19-data/us-counties.csv"):
    df = pd.read_csv(fn)
    #df['sc'] = df['state'] + ':' + df['county']
    df = df[df['cases'] > 0]
    df = df[df['fips'] > 0]
    df['fips'].fillna(0, inplace=True)
    df = df.apply(fix_nyt, axis=1)
    df = df.apply(strip_state, axis=1)
    return df # [['fips', 'date', 'deaths', 'cases']]

def fix_geo(row):
    row['State'] = get_state(row['State'])
    regex = re.compile("[^a-zA-Z .']")
    row['County'] = regex.sub('', row['County'] )
    return row

def extract_geography(fn="./data/County Physical.csv"):
    df = pd.read_csv(fn, sep='\t')
    df = df.apply(fix_geo, axis=1)
    df['sc'] = df['State'] + ':' + df['County']
    ret = df[[
        'sc',
        'FIPS',
        'State',
        'County',
        'Pop',
        'Land area km'
    
    ]]
    ret.fillna(0)
    ret.columns = [
        'sc',
        'fips',
        'state',
        'county',
        'population', 
        'area-km'
    ] 
    return ret

def build_per_100k(counties, nyt_df):
    per100k = pd.merge(counties, nyt_df, how='inner', left_on=['fips'], right_on=['fips'])
    per100k = per100k[['fips', 'population', 'date', 'cases', 'deaths']]
    per100k['deaths_per'] = per100k.apply(lambda row: (row['deaths']/row['population'])*100000, axis=1)
    per100k['cases_per'] = per100k.apply(lambda row: (row['cases']/row['population'])*100000, axis=1)
    return per100k

def get_county(row):
    working = row['Geographic Area Name'].split(",")[0].split(' ')
    working = working[:len(working)-1]
    row['county'] = ' '.join(working)
    return row

def get_fips(row):
    fips = row['id'].split('US')[1]
    row['fips'] = int(fips)
    return row

def extract_hhi(fn="./data/Census/HH_income.csv"):
    df = pd.read_csv(fn)
    df = df.apply(get_fips, axis=1)
    ret = df[[
        'fips',
        'Estimate!!Households!!Total',
        'Estimate!!Households!!Median income (dollars)',
        'Estimate!!Households!!Mean income (dollars)'
    ]]
    ret.columns = ['fips', 'households', 'mean_hhi', 'median_hhi']
    return ret

def fix_pubtrans(row):
    pc = row['percent_commuter']
    if pc == 'N':
        row['percent_commuter'] = 0.0
    else:
        row['percent_commuter'] = float(pc)
    return row

def extract_public_transport(fn="./data/Census/lots_of_census_data.csv"):
    df = pd.read_csv(fn)
    df = df.apply(get_fips, axis=1)
    ret = df[[
        'fips',
        'Estimate!!Total!!Workers 16 years and over!!MEANS OF TRANSPORTATION TO WORK!!Public transportation (excluding taxicab)'
    ]]
    ret.columns = ['fips', 'percent_commuter']
    ret = ret.apply(fix_pubtrans, axis=1)
    return ret

def extract_edu(fn="./data/Census/edu.csv"):
    df = pd.read_csv(fn)
    df = df.apply(get_fips, axis=1)
    ret = df[[
        'fips',
        'Estimate!!Total!!Population 25 years and over',
        #'Estimate!!Male!!Population 25 years and over',
        'Estimate!!Percent!!Population 25 years and over!!High school graduate (includes equivalency)',
        #'Estimate!!Percent!!Population 25 years and over!!Some college, no degree',
        #'Estimate!!Percent!!Population 25 years and over!!Associate\'s degree',
        'Estimate!!Percent!!Population 25 years and over!!Bachelor\'s degree',
        'Estimate!!Percent!!Population 25 years and over!!Graduate or professional degree',
        'Estimate!!Total!!Population 25 years and over!!Population 65 years and over',
        #'Estimate!!Total!!Population 25 years and over!!Population 65 years and over!!Bachelor\'s degree or higher',
        #'Estimate!!Percent!!Population 25 years and over!!Population 65 years and over!!Bachelor\'s degree or higher',
        #'Estimate!!Total!!RACE AND HISPANIC OR LATINO ORIGIN BY EDUCATIONAL ATTAINMENT!!White alone',
        #'Estimate!!Total!!RACE AND HISPANIC OR LATINO ORIGIN BY EDUCATIONAL ATTAINMENT!!White alone!!Bachelor\'s degree or higher',
        #'Estimate!!Percent!!RACE AND HISPANIC OR LATINO ORIGIN BY EDUCATIONAL ATTAINMENT!!White alone!!Bachelor\'s degree or higher',
        #'Estimate!!Percent!!RACE AND HISPANIC OR LATINO ORIGIN BY EDUCATIONAL ATTAINMENT!!White alone, not Hispanic or Latino!!Bachelor\'s degree or higher'     
    ]]
    ret.columns = [
        'fips',
        'pop_over_25', 
        'hs', 
        'ba_plus',
        'ma_plus',
        'pop_over_65'
    ]
    ret['hs'] = ret['hs']/100
    ret['ba_plus'] = ret['ba_plus']/100
    ret['ma_plus'] = ret['ma_plus']/100
    return ret

def make_float(row):
    if(row['percent_big_buildings'] == 'N'):
        row['percent_big_buildings'] = 0.0
    val = float(row['percent_big_buildings'])/100
    row['percent_big_buildings'] = val
    return row

def extract_housing(fn="./data/Census/housing.csv"):
    df = pd.read_csv(fn)
    df = df.apply(get_fips, axis=1)
    ret = df[[
        'fips',
        'Estimate!!VALUE!!Owner-occupied units!!Median (dollars)',
        'Estimate!!GROSS RENT!!Occupied units paying rent!!Median (dollars)',
        #'Percent Estimate!!HOUSING OCCUPANCY!!Total housing units',
        #'Estimate!!HOUSING OCCUPANCY!!Total housing units!!Occupied housing units',
        #'Percent Estimate!!HOUSING OCCUPANCY!!Total housing units!!Occupied housing units',
        #'Percent Estimate!!UNITS IN STRUCTURE!!Total housing units!!1-unit, detached',
        #'Percent Estimate!!UNITS IN STRUCTURE!!Total housing units!!5 to 9 units',
        #'Percent Estimate!!UNITS IN STRUCTURE!!Total housing units!!10 to 19 units',
        'Percent Estimate!!UNITS IN STRUCTURE!!Total housing units!!20 or more units'
    ]]
    ret.fillna(0)
    ret.columns = [
        'fips',
        'median_house_price', 
        'median_rent', 
        'percent_big_buildings'
    ]
    ret = ret.apply(make_float, axis=1)
    return ret

def extract_election(fn="./data/2016_US_County_Level_Presidential_Results.csv"):
    df = pd.read_csv(fn)
    ret = df[[
        'combined_fips',
        'per_dem',
        'per_gop'
    ]]
    ret.columns = [
        'fips',
        'per_dem',
        'per_gop'
    ]
    return ret

def fix_sip_dates(row):
    row['SIP'] = datetime.strptime(row['SIP'], '%m/%d/%Y')
    row['lifted'] = datetime.strptime(row['lifted'], '%m/%d/%Y')
    return row

def extract_sip(fn="./data/SIP.csv"):
    df = pd.read_csv(fn)
    df['SIP'].fillna('5/15/2020', inplace=True)
    df['lifted'].fillna('5/15/2020', inplace=True)
    df = df.apply(fix_sip_dates, axis=1)
    print(type(df['SIP']))
    ret = df[['state', 'SIP', 'lifted']]
    ret.columns = [
        'state',
        'sip',
        'sip_lifted'
    ]
    return ret


## AIRPORT STUFF

def fix_county_latlon(county):
    county['Lat'] = float(county['Lat'])
    county['Lon'] = float(county['Lon'].replace('–','-'))
    return county 

 


###### Supposed to be in util.py :( 


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

