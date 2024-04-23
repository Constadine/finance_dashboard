import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime 
import pandas as pd
from money_manage import calculate_monthly_exp_inc, calculate_accumulative_total, calculate_expenses_by_category

def plot_time_series(df, result):
    # Time series visualization with Plotly
    fig = px.line(df, x=df.index, y='SEK', title='Expense Time Series')
    fig.update_xaxes(title_text='Date')
    fig.update_yaxes(title_text='Expenses (SEK)')

    # Time series decomposition using Plotly
    fig_decomposition = go.Figure()

    fig_decomposition.add_trace(go.Scatter(x=result.trend.index, y=result.trend, mode='lines', name='Trend'))
    fig_decomposition.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal, mode='lines', name='Seasonal'))
    fig_decomposition.add_trace(go.Scatter(x=result.resid.index, y=result.resid, mode='lines', name='Residual'))

    fig_decomposition.update_layout(title='Time Series Decomposition')
    fig_decomposition.update_xaxes(title_text='Date')
    fig_decomposition.update_yaxes(title_text='Components')

    return fig, fig_decomposition

def generate_expense_income_ratio_plot(monthly_combined_df):
    # Calculate the expense-to-income ratio for each month, handling division by zero
    monthly_combined_df['expense_income_ratio'] = monthly_combined_df['monthly_expenses'] / monthly_combined_df['monthly_income']
    monthly_combined_df['expense_income_ratio'] = monthly_combined_df['expense_income_ratio'].replace([np.inf, -np.inf], np.nan)

    # Define hover text with final number (income - expense)
    hover_text = [f"Date: {date}<br>Outcome: {income - expenses:.2f}<br>Expense-to-Income Ratio: {ratio:.2f}" 
                  for date, income, expenses, ratio in zip(monthly_combined_df.index.date,
                                                      monthly_combined_df['monthly_income'], 
                                                      monthly_combined_df['monthly_expenses'],
                                                      monthly_combined_df['expense_income_ratio'])]

    # Define colors based on expense-to-income ratio
    colors = ['red' if ratio > 1 else 'green' for ratio in monthly_combined_df['expense_income_ratio']]

    # Create a Plotly figure with a single line trace
    fig = go.Figure()

    # Add a line trace for expense-to-income ratio over time with color coded points
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, 
                             y=monthly_combined_df['expense_income_ratio'],
                             mode='lines+markers',
                             line=dict(color='lightblue'),  # Set line color to black
                             marker=dict(color=colors),  # Set marker color based on expense-to-income ratio
                             name='Expense-to-Income Ratio',
                             hoverinfo='text',  # Show hover text
                             hovertext=hover_text))  # Set hover text

    # Update layout
    fig.update_layout(title='Expense-to-Income Ratio Over Time',
                       xaxis_title='Date',
                       yaxis_title='Expense-to-Income Ratio',
                       yaxis=dict(range=[0, 5]))  # Set y-axis range from 0 to 5

    return fig


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
    
    sns.lineplot(x='Date', y='monthly_expenses', data=monthly_combined_df, marker='v', color='r', label='Expense Trend')
    sns.lineplot(x='Date', y='monthly_income', data=monthly_combined_df, marker='^', color='g', label='Income Trend')
    sns.lineplot(x='Date', y='Accumulative_Total', data=monthly_combined_df, marker='', linestyle='-', color='b', label='Total')

    # Draw a vertical line at the x-value of the first occurrence of 'SEK'
    plt.axvline(x=se_index, color='black', linestyle='--', label='Moved to Sweden')
    
    # Add text annotation before the line
    xaxis_greece_text = monthly_combined_df.index[0].date() + (se_index - monthly_combined_df.index[0])/2
    plt.text(xaxis_greece_text, monthly_combined_df['monthly_expenses'].max()/2 , 'Greece', ha='right', va='bottom')
    
    # Add text annotation after the line
    xaxis_sweden_text = se_index.date() + (monthly_combined_df.index[-1] - se_index)/2
    plt.text(xaxis_sweden_text, monthly_combined_df['monthly_expenses'].max()/1.5, 'Sweden', ha='left', va='bottom')
    
    
    plt.xticks(rotation=45)
    
    # Set plot labels and title
    plt.xlabel('Date')
    plt.ylabel('SEK')
    plt.title('Expense/Income Trend over Time')
    
    # Show legend
    plt.legend()
    
    # Show the plot
    return plt

def draw_monthly_expenses_income_line_plotly(df, toggle_loan_choice=False):
    # Calculate monthly and accumulative values
    # monthly_combined_df = calculate_monthly_exp_inc(df)
    monthly_combined_df = calculate_accumulative_total(df, toggle_loan=toggle_loan_choice)
    
    # Create a line chart using Plotly graph objects
    fig = go.Figure()
    
    # Add lines for Monthly_Income, Monthly_Expense, and Accumulative_Total
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, y=monthly_combined_df['monthly_income'],
                             mode='lines+markers', name='Monthly Income', marker=dict(symbol='triangle-up')))
    
    fig.add_trace(go.Scatter(x=monthly_combined_df.index, y=monthly_combined_df['monthly_expenses'],
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
