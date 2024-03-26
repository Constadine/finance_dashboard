import plotly.express as px
import plotly.graph_objects as go

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
