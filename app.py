import streamlit as st
import pandas as pd
from money_manage import *
from visualization import plot_time_series
import plotly.express as px
import os

st.set_page_config(
    page_title="Dzikonomy",
    page_icon="🐗",  # You can use an emoji or the URL of an image
    layout="wide",  # You can choose "wide" or "centered"
)

st.markdown("<h1 style='text-align: center;'>🐗 Dzikonomy Board 🐗</h1>", unsafe_allow_html=True)

# Allow user to upload a file
uploaded_file = st.file_uploader("Upload a CSV file", type=["xlsx"])

if uploaded_file:
    filename, file_extension = os.path.splitext(uploaded_file.name)

    if  file_extension == '.xlsx':
        df = pd.read_excel(uploaded_file.read(), engine='openpyxl')

    else:
        raise Exception("File not supported")

    # Clean data
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['Date']) 
    df = df.sort_values(by='Date')
    
    end_date = df.Date.max()
    start_date = df.Date.min()
    

    # TITLE
    st.markdown("<h3 style='text-align: center;'>💸AM I <i>DOOMED</i>?💸</h1>", unsafe_allow_html=True)
    
    
    # SIDEBAR
    st.sidebar.subheader("PSST DZIK. Play with parameters here")
    
    # Search bar for entering the search query
    search_query = st.sidebar.text_input('Enter search query:')

    # Toggle the dataframe table view
    toggle_table = st.sidebar.toggle("See Data Table")
    
    # Choose if you want to include the loan money as income
    toggle_loan_choice = st.sidebar.toggle('Include Loan Money')
    
    # Choose between interactive (plotly) or static (seaborn) line chart
    library_option = st.sidebar.selectbox('Select Graph Type', ['Plotly', 'Seaborn'])
    
    # Choose the type of chart for the distribution graph
    chart_type = st.sidebar.selectbox('Select Chart Type', ['Sunburst Chart', 'Bar Chart', 'Treemap'])
    # heatmap_type = st.sidebar.selectbox('Select Heatmap Period', ['daily', 'monthly'])
        
    if toggle_table:
        if search_query:
            filtered_df = filter_dataframe(df, search_query)
            st.dataframe(filtered_df, use_container_width=True)

        else:
            st.dataframe(df, use_container_width=True)
    
    
    if  library_option == 'Plotly':
        # Call the Plotly function
        plotly_fig = draw_monthly_expenses_income_line_plotly(df, toggle_loan_choice)
        st.plotly_chart(plotly_fig,use_container_width=True)
    
    elif library_option == 'Seaborn':
        # Call the Seaborn function
        sns_fig = draw_monthly_expenses_income_line_sns(df)
        st.pyplot(sns_fig,use_container_width=True)

    
    # Main content
    st.title(f'Expense Distribution for {start_date.year} - {end_date.year}')
    
    fig = draw_distribution(df, chart_type)
    st.plotly_chart(fig, use_container_width=True)
    
    ###### Plot line charts for specific expense categories to observe trends over the years. 
    
    
    # Filter only expenses
    expenses_df = df[df['Income/Expense'] == 'Expense']
    
    # Create a Streamlit sidebar
    selected_category = st.sidebar.selectbox('Select Expense Category', expenses_df['Category'].unique())
    time_period = st.sidebar.radio('Select Time Period', ['Year', 'Month'], index=0)  # Default to 'Month'
    
    # Filter data for the selected category
    selected_category_df = expenses_df[expenses_df['Category'] == selected_category]
    
    # Extract month name and year from the 'Date' column
    selected_category_df['Month'] = selected_category_df['Date'].dt.strftime('%B')  # Month name
    selected_category_df['Year'] = selected_category_df['Date'].dt.year.astype(str)  # Convert to string
    monthly_sum_df = selected_category_df.groupby(['Year', 'Month', 'Subcategory']).agg({'SEK': 'sum'}).reset_index()
    
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    start_year, end_year = start_date.year, end_date.year
    year_order = list(range(start_year, end_year + 1))
    
    
    if time_period == 'Year':
        fig = px.bar(monthly_sum_df, x='Month', y='SEK', color='Subcategory',
                     title=f'Expense Trend Over the Months by {time_period} for {selected_category} ',
                     labels={'SEK': 'Expense (SEK)', 'Month': 'Month'},
                     facet_col='Year',
                     height=600,
                     category_orders={'Month': month_order},
                     )
        
        fig.update_layout(xaxis_title='Month', yaxis_title='Expense (SEK)')
    
    else:

        # Create a bar chart with facets for each month
        fig = px.bar(monthly_sum_df, x='Year', y='SEK', color='Subcategory',
                     title=f'Expense Trend Over the Years by Month for {selected_category}',
                     labels={'SEK': 'Expense (SEK)', 'Year': 'Year'},
                     facet_col='Month',
                     height=600,
                     category_orders={'Year': year_order, 'Month': month_order}
                     )
        fig.update_layout(xaxis_title='Year', yaxis_title='Expense (SEK)')
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    monthly_combined_df = calculate_monthly_exp_inc(df)
    st.plotly_chart(generate_expense_income_ratio_plot(monthly_combined_df), use_container_width= True)
        
    
    
    ##### CREATE A TABLE WITH THE MOST IMPORT STATITSTICS
    #### Predictions

else:
    st.warning("Please upload a XLSX file. IF you do not see your file, open your spreadsheet and save as type '.xlsx'")
