import pandas as pd
from time_series_forecasting import train_time_series_model
from visualization import plot_time_series
import streamlit as st

df = pd.read_excel('Money Manager_2024-01-07.xlsx')


df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']) 
df = df.sort_values(by='Date')

end_date = df.Date.max()
start_date = df.Date.min()

expenses_df = df[df['Income/Expense'] == 'Expense']
income_df = df[df['Income/Expense'] == 'Income']



result = train_time_series_model(expenses_df, freq='D')

st.plotly_chart(plot_time_series(expenses_df, result)[0])
st.plotly_chart(plot_time_series(expenses_df, result)[1])