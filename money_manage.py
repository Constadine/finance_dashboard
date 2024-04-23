import pandas as pd
from prophet import Prophet

def get_nlargest(df, n, category):
    
    res = df.loc[df[df['Income/Expense'] == category].SEK.nlargest(n).index[-1]]
    
    return res


def calculate_monthly_exp_inc(df):
    # Convert 'Date' column to datetime type
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    
    # Group by 'Income/Expense' and resample by 'M' (month)
    monthly_expenses = df[df['Income/Expense'] == 'Expense'].groupby(pd.Grouper(key='Date', freq='M')).agg({'SEK': 'sum'})
    monthly_income = df[df['Income/Expense'] == 'Income'].groupby(pd.Grouper(key='Date', freq='M')).agg({'SEK': 'sum'})
    
    # Combine monthly expenses and income into a single DataFrame
    monthly_combined_df = pd.merge(monthly_expenses, monthly_income, left_index=True, right_index=True, how='outer')
    
    # Rename the columns
    monthly_combined_df.columns = ['monthly_expenses', 'monthly_income']
    
    return monthly_combined_df

    
    
def calculate_accumulative_total(df, toggle_loan=False):
    if not toggle_loan:
        df = df[df['Subcategory'] != 'Loan']

    df = calculate_monthly_exp_inc(df)
    
    df['Cumulative_Expense'] = df['monthly_expenses'].cumsum()
    df['Cumulative_Income'] = df['monthly_income'].cumsum()
    
    df['Accumulative_Total'] = df['Cumulative_Income'] - df['Cumulative_Expense']  
    
    
    return df

####### Distribution of expenses accross different categories
def calculate_expenses_by_category(df):
    # Filter only expenses
    expenses_df = df[df['Income/Expense'] == 'Expense']

    # Extract Year from the 'Date' column
    expenses_df['Year'] = expenses_df['Date'].dt.year
    
    # Group by Category, Subcategory, and Year, and sum the expenses
    grouped_df = expenses_df.groupby(['Category', 'Subcategory', 'Year']).agg({'SEK': 'sum'}).reset_index()
    
    return grouped_df


# Function to filter DataFrame based on search query
def filter_dataframe(df, search_query):
    columns = ['Income/Expense', 'Category', 'Subcategory', 'Note', 'Description']
    # Convert search_query to lowercase for case-insensitive search
    search_query = search_query.lower()
    # Filter DataFrame based on search query and specified columns
    filtered_df = df[df[columns].apply(lambda x: any([search_query in str(x[col]).lower() for col in columns]), axis=1)]
    
    return filtered_df

# Function to generate suggestions based on DataFrame column
def generate_suggestions(df):
    from_columns = ['Category', 'Subcategory', 'Note','Note.1']
    suggestions = []
    for column in from_columns:
        suggestions.extend(df[column].unique().tolist())
        
    return list(set(suggestions)) 

def predict_subcategory_expenses(df, subcategory, year):
    # Filter data for the specified subcategory and year
    subcategory_expenses = df[(df['Subcategory'] == subcategory) & (df['Date'].dt.year == year)]

    # Prepare data for Prophet
    data = subcategory_expenses[['Date', 'SEK']]
    data.columns = ['ds', 'y']  # Prophet expects columns 'ds' for date and 'y' for the value
    
    # Train Prophet model
    model = Prophet()
    model.fit(data)
    
    # Make future predictions for the next 12 months
    future = model.make_future_dataframe(periods=12, freq='M')
    forecast = model.predict(future)
    
    return forecast
