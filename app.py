import streamlit as st
import pandas as pd
from money_manage import *

# Read data
df = pd.read_html("Money Manager_2024-01-07.xls", header=0)[0]

# Clean data
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df = df.dropna(subset=['Date']) 
df = df.sort_values(by='Date')

end_date = df.Date.max()
start_date = df.Date.min()


st.set_page_config(layout = "wide")


# TITLE
st.markdown("<h1 style='text-align: center;'>💸AM I DOOMED?💸</h1>", unsafe_allow_html=True)


# SIDEBAR
library_option = st.sidebar.selectbox('Select Graph Type', ['Plotly', 'Seaborn'])
chart_type = st.sidebar.selectbox('Select Chart Type', ['Sunburst Chart', 'Bar Chart', 'Treemap'])
heatmap_type = st.sidebar.selectbox('Select Heatmap Period', ['daily', 'monthly'])

# Main content
st.title('Finance Dashboard')

if  library_option == 'Plotly':
    # Call the Plotly function
    plotly_fig = draw_monthly_expenses_income_line_plotly(df)
    st.plotly_chart(plotly_fig,use_container_width=True)


    
elif library_option == 'Seaborn':
    # Call the Seaborn function
    sns_fig = draw_monthly_expenses_income_line_sns(df)
    st.pyplot(sns_fig,use_container_width=True)

# Create a Streamlit sidebar

# Main content
st.title(f'Expense Distribution for {start_date.year} - {end_date.year}')

fig = draw_distribution(df, chart_type)
st.plotly_chart(fig, use_container_width=True)

###### Plot line charts for specific expense categories to observe trends over the years. 


# Filter only expenses
expenses_df = df[df['Income/Expense'] == 'Expense']

# Create a Streamlit sidebar
selected_category = st.sidebar.selectbox('Select Expense Category', expenses_df['Category'].unique())
time_period = st.sidebar.radio('Select Time Period', ['Month', 'Year'], index=0)  # Default to 'Month'

# Filter data for the selected category
selected_category_df = expenses_df[expenses_df['Category'] == selected_category]

# Extract month name and year from the 'Date' column
selected_category_df['Month'] = selected_category_df['Date'].dt.strftime('%B')  # Month name
selected_category_df['Year'] = selected_category_df['Date'].dt.year.astype(str)  # Convert to string
monthly_sum_df = selected_category_df.groupby(['Year', 'Month', 'Subcategory']).agg({'SEK': 'sum'}).reset_index()

month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
start_year, end_year = start_date.year, end_date.year
year_order = list(range(start_year, end_year + 1))


if time_period == 'Month':
    # Create a bar chart with facets for each month
    fig = px.bar(monthly_sum_df, x='Year', y='SEK', color='Subcategory',
                 title=f'Expense Trend Over the Years by Month for {selected_category}',
                 labels={'SEK': 'Expense (SEK)', 'Year': 'Year'},
                 facet_col='Month',
                 height=600,
                 category_orders={'Year': year_order, 'Month': month_order}
                 )
    fig.update_layout(xaxis_title='Year', yaxis_title='Expense (SEK)')

else:
    fig = px.bar(monthly_sum_df, x='Month', y='SEK', color='Subcategory',
                 title=f'Expense Trend Over the Months by {time_period} for {selected_category} ',
                 labels={'SEK': 'Expense (SEK)', 'Month': 'Month'},
                 facet_col='Year',
                 height=600,
                 category_orders={'Month': month_order},
                 )
    
    fig.update_layout(xaxis_title='Month', yaxis_title='Expense (SEK)')

# Display the chart
st.plotly_chart(fig, use_container_width=True)


#### Heatmap
