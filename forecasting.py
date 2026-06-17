import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error


def load_dataset(path):

    df = pd.read_csv("")

    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)

    return df


def prepare_daily_sales(df):

    daily_sales = df.groupby('Date')['Revenue_inr'].sum().reset_index()

    df['Holiday_Flag'] = np.where(df['Holiday'].notnull(), 1, 0)

    holiday_flags = df[['Date', 'Holiday_Flag']].drop_duplicates()

    prod_df = daily_sales.merge(holiday_flags, on='Date', how='left')

    prod_df['Holiday_Flag'] = prod_df['Holiday_Flag'].fillna(0)

    prod_df = prod_df.set_index('Date').asfreq('D').fillna(0).reset_index()

    return prod_df


def prophet_forecast(prod_df):

    prophet_df = prod_df.rename(columns={'Date': 'ds', 'Revenue_inr': 'y'})

    model = Prophet()

    model.add_regressor('Holiday_Flag')

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=30)

    future = future.merge(prod_df[['Date', 'Holiday_Flag']],
                          left_on='ds', right_on='Date',
                          how='left').drop(columns=['Date'])

    future['Holiday_Flag'] = future['Holiday_Flag'].fillna(0)

    forecast = model.predict(future)

    future_30 = forecast.tail(30)

    return future_30[['ds', 'yhat']]
