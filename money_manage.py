import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import datetime 
import xarray as xr

def get_nlargest(df, n, category):
    
    res = df.loc[df[df['Income/Expense'] == category].SEK.nlargest(n).index[-1]]
    
    return res



def calculate_monthly_exp_inc(df):
    expense_df = df[df['Income/Expense'] == 'Expense']
    income_df = df[df['Income/Expense'] == 'Income']
    
    # Set 'Date' as the index
    expense_df.set_index('Date', inplace=True)
    
    monthly_expenses = expense_df.resample('M').agg({'SEK': 'sum'})
    
    # Set 'Date' as the index
    income_df.set_index('Date', inplace=True)
    
    monthly_income = income_df.resample('M').agg({'SEK': 'sum'})
    
    monthly_combined_df = pd.merge(monthly_expenses, monthly_income, left_index=True, right_index=True, how='outer')

    # Rename the columns
    monthly_combined_df.columns = ['Monthly_Expense', 'Monthly_Income']
    
    return monthly_combined_df
    
    
def calculate_accumulative_total(df):
    df = calculate_monthly_exp_inc(df)
    
    df['Cumulative_Expense'] = df['Monthly_Expense'].cumsum()
    df['Cumulative_Income'] = df['Monthly_Income'].cumsum()
    
    df['Accumulative_Total'] = df['Cumulative_Income'] - df['Cumulative_Expense']  
    
    return df

####### Linechart of all my expenses
def draw_monthly_expenses_income_line_sns(df):
    
    monthly_combined_df = calculate_monthly_exp_inc(df)
    
    #Calculate cumulative sum for Expense and Income
    monthly_combined_df = calculate_accumulative_total(df)
    
    sns.set(style="whitegrid")
    
    plt.figure(figsize=(12, 6))
      
    # Find the index of the first occurrence of 'SEK' in the 'Currency' column
    # se_index = monthly_expenses_df.index[monthly_expenses_df['Currency'] == 'SEK'].min()

    # Hardcode the date I came to Sweden
    se_index = datetime.datetime(2022, 8, 21, 20, 50, 17)
    
    sns.lineplot(x='Date', y='Monthly_Expense', data=monthly_combined_df, marker='v', color='r', label='Expense Trend')
    sns.lineplot(x='Date', y='Monthly_Income', data=monthly_combined_df, marker='^', color='g', label='Income Trend')
    sns.lineplot(x='Date', y='Accumulative_Total', data=monthly_combined_df, marker='', linestyle='-', color='b', label='Total')

    # Draw a vertical line at the x-value of the first occurrence of 'SEK'
    plt.axvline(x=se_index, color='black', linestyle='--', label='Moved to Sweden')
    
    # Add text annotation before the line
    xaxis_greece_text = monthly_combined_df.index[0].date() + (se_index - monthly_combined_df.index[0])/2
    plt.text(xaxis_greece_text, monthly_combined_df['Monthly_Expense'].max()/2 , 'Greece', ha='right', va='bottom')
    
    # Add text annotation after the line
    xaxis_sweden_text = se_index.date() + (monthly_combined_df.index[-1] - se_index)/2
    plt.text(xaxis_sweden_text, monthly_combined_df['Monthly_Expense'].max()/1.5, 'Sweden', ha='left', va='bottom')
    
    
    plt.xticks(rotation=45)
    
    # Set plot labels and title
    plt.xlabel('Date')
    plt.ylabel('SEK')
    plt.title('Expense/Income Trend over Time')
    
    # Show legend
    plt.legend()
    
    # Show the plot
    return plt

def draw_monthly_expenses_income_line_plotly(df):
    # Calculate monthly and accumulative values
    monthly_combined_df = calculate_monthly_exp_inc(df)
    monthly_combined_df = calculate_accumulative_total(df)
    
    # Create a line chart using Plotly graph objects
    fig = go.Figure()
    
    # Add lines for Monthly_Income, Monthly_Expense, and Accumulative_Total
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, y=monthly_combined_df['Monthly_Income'],
                             mode='lines+markers', name='Monthly Income', marker=dict(symbol='triangle-up')))
    
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, y=monthly_combined_df['Monthly_Expense'],
                             mode='lines+markers', name='Monthly Expense', marker=dict(symbol='triangle-down')))
    
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, y=monthly_combined_df['Accumulative_Total'],
                             mode='lines+markers', name='Accumulative Total', marker=dict(symbol='line-ns-open')))
    
    # Draw a vertical line at the x-value of the first occurrence of 'SEK'
    se_index = pd.to_datetime('2022-08-21')
    fig.add_shape(
        go.layout.Shape(
            type="line",
            x0=se_index,
            x1=se_index,
            y0=0,
            y1=monthly_combined_df['Accumulative_Total'].max(),
            line=dict(color="white", dash="dash"),
        )
    )
    
    # Add text annotation before the line
    fig.add_annotation(
        x=se_index - pd.to_timedelta(45, unit='D'),
        y=monthly_combined_df['Accumulative_Total'].max() / 2,
        text='Greece',
        font=dict(size=10),
        showarrow=False,
    )
    
    # Add text annotation after the line
    fig.add_annotation(
        x=se_index + pd.to_timedelta(50, unit='D'),
        y=monthly_combined_df['Accumulative_Total'].max() / 2,
        text='Sweden',
        font=dict(size=10),
        showarrow=False,
    )
    
    # Customize layout
    fig.update_layout(xaxis=dict(tickangle=45),
                      xaxis_title='Date',
                      yaxis_title='SEK',
                      legend_title='Trend',
                      legend=dict(x=0, y=1),
                      margin=dict(l=0, r=0, t=50, b=0))
    
    fig.update_traces(line_color='darkgreen', selector=dict(name='Monthly Income'))
    fig.update_traces(line_color='darkred', selector=dict(name='Monthly Expense'))
    fig.update_traces(line_color='lightblue', selector=dict(name='Accumulative Total'))

    return fig


####### Distribution of expenses accross different categories
def calculate_expenses_by_category(df):
    # Filter only expenses
    expenses_df = df[df['Income/Expense'] == 'Expense']

    # Extract Year from the 'Date' column
    expenses_df['Year'] = expenses_df['Date'].dt.year
    
    # Group by Category, Subcategory, and Year, and sum the expenses
    grouped_df = expenses_df.groupby(['Category', 'Subcategory', 'Year']).agg({'SEK': 'sum'}).reset_index()
    
    return grouped_df

def draw_distribution(df, graph_type):
    df = calculate_expenses_by_category(df)

    if graph_type == 'Sunburst Chart':
        fig = px.sunburst(df, path=['Category', 'Subcategory', 'Year'], values='SEK',
                          title='Expense Distribution by Category, Subcategory, and Year',
                          height=600)
    elif graph_type == 'Treemap':
        fig = px.treemap(df, path=['Category', 'Subcategory', 'Year'], values='SEK',
                         title='Expense Distribution by Category, Subcategory, and Year',
                         height=600)
    else:
        fig = px.bar(df, x='Category', y='SEK', color='Subcategory',
                     title='Expense Distribution by Category with Subcategories',
                     height=600)
        
    return fig
