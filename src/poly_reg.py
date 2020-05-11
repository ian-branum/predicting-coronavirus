import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import PolynomialFeatures 
from sklearn.linear_model import LinearRegression 


def days_since_1jan(dt):
    return (dt - datetime(2020,1,1)).days

def model_county(df, county, state, degree=2): 
    try:
        county_df = df[df['state'] == state]
        county_df = df[df['county'] == county]
        county_df = county_df[county_df['cases'] > 10]
        grouped = county_df.groupby('date')
        cases = grouped['cases'].agg([np.sum])['sum'].reset_index()
        deaths = grouped['deaths'].agg([np.sum])['sum'].reset_index()
        y = cases.iloc[:,1]
        X = cases.iloc[:,0].apply(days_since_1jan)
        X = X[:, np.newaxis]
        y = y[:, np.newaxis]
        #print("{} : {}".format(county, X))
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        poly.fit(X_poly, y)
        lin = LinearRegression()
        lin.fit(X_poly, y)
        return X, X_poly, y, lin 
    except Exception:
        return None, None, None, None

def model_state(df, state, degree=2): 
    county_df = df[df['state'] == state]
    county_df = county_df[county_df['cases'] > 10]
    grouped = county_df.groupby('date')
    cases = grouped['cases'].agg([np.sum])['sum'].reset_index()
    deaths = grouped['deaths'].agg([np.sum])['sum'].reset_index()
    y = cases.iloc[:,1]
    X = cases.iloc[:,0].apply(days_since_1jan)
    X = X[:, np.newaxis]
    y = y[:, np.newaxis]
    try:
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        poly.fit(X_poly, y)
        lin = LinearRegression()
        lin.fit(X_poly, y)
        return X, X_poly, y, lin 
    except Exception:
        print("failed on {}, X= {}".format(state, X))
        return 'failed'