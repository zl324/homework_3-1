import dash
import plotly.graph_objects as go
from dash import dcc, dash_table
from dash import html
from dash.dependencies import Input, Output, State
from ibapi.contract import Contract
from ibapi.order import Order
from fintech_ibkr import *
import pandas as pd

# Make a Dash app!
app = dash.Dash(__name__)
server = app.server
# Define the layout.
df = pd.read_csv('submitted_orders.csv')
app.layout = html.Div([

    # Section title
    html.H3("Section 1: Fetch & Display exchange rate historical data"),
    html.H4("Select value for whatToShow:"),
    html.Div(
        dcc.Dropdown(
            ["TRADES", "MIDPOINT", "BID", "ASK", "BID_ASK", "ADJUSTED_LAST",
             "HISTORICAL_VOLATILITY", "OPTION_IMPLIED_VOLATILITY", 'REBATE_RATE',
             'FEE_RATE', "YIELD_BID", "YIELD_ASK", 'YIELD_BID_ASK', 'YIELD_LAST',
             "SCHEDULE"],
            "MIDPOINT",
            id='what-to-show'
        ),
        style = {'width': '365px'}
    ),
    html.H4("Select value for endDateTime:"),
    html.Div(
        children = [
            html.P("You may select a specific endDateTime for the call to " + \
                   "fetch_historical_data. If any of the below is left empty, " + \
                   "the current present moment will be used.")
        ],
        style = {'width': '365px'}
    ),
    html.Div(
        children = [
            html.Div(
                children = [
                    html.Label('Date:'),
                    dcc.DatePickerSingle(id='edt-date')
                ],
                style = {
                    'display': 'inline-block',
                    'margin-right': '20px',
                }
            ),
            html.Div(
                children = [
                    html.Label('Hour:'),
                    dcc.Dropdown(list(range(24)), id='edt-hour'),
                ],
                style = {
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children = [
                    html.Label('Minute:'),
                    dcc.Dropdown(list(range(60)), id='edt-minute'),
                ],
                style = {
                    'display': 'inline-block',
                    'padding-right': '5px'
                }
            ),
            html.Div(
                children = [
                    html.Label('Second:'),
                    dcc.Dropdown(list(range(60)), id='edt-second'),
                ],
                style = {'display': 'inline-block'}
            )
        ]
    ),

    ############################################################################
    ############################################################################
    html.H4("Input durationStr:"),
    html.Div(
        dcc.Input(
            id='duration-str', value='30 D'
        ),
        style={'width': '365px'}
    ),
    html.H4("Select value for barSizeSetting:"),
    html.Div(
        dcc.Dropdown(
            ["1 sec", "5 secs", "15 secs", "30 secs",
             "1 min", "2 mins", "3 mins", "5 mins", "15 mins",
             "30 mins", "1 hour", "1 day"],
            "1 hour",
            id='bar-size-setting'
        ),
        style={'width': '365px'}
    ),
    html.H4("Select value for useRTH:"),
    html.Div(
        dcc.Dropdown(
            ["1", "0"],
            "1",
            id='use-RTH'
        ),
        style={'width': '365px'}
    ),
    ############################################################################
    ############################################################################

    html.H4("Enter a currency pair:"),
    html.P(
        children=[
            "See the various currency pairs here: ",
            html.A(
                "currency pairs",
                href='https://www.interactivebrokers.com/en/index.php?f=2222&exch=ibfxpro&showcategories=FX'
            )
        ]
    ),
    # Currency pair text input, within its own div.
    html.Div(
        # The input object itself
        ["Input Currency: ", dcc.Input(
            id='currency-input', value='AUD.CAD', type='text'
        )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    # Submit button
    html.Button('Submit', id='submit-button', n_clicks=0),
    # Line break
    html.Br(),
    # Div to hold the initial instructions and the updated info once submit is pressed
    html.Div(id='currency-output', children='Enter a currency code and press submit'),
    # Div to hold the candlestick graph
    html.Div(
        dcc.Loading(
            id='loading-1',
            type='default',
            children=dcc.Graph(id='candlestick-graph')
        )
    ),
    # Another line break
    html.Br(),
    html.H3("Section 2: Trading"),
    html.H4("Contract Inputs"),
    html.Div(
        # The input object itself
        children=["Contract Symbol: ", dcc.Input(
        id='symbol-input', value='AUD', type='text'
    )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        children=["secType ", dcc.Input(
                 id='secType-input', value='CASH', type='text'
             )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        children=["Currency ", dcc.Input(
                 id='contract-currency-input', value='USD', type='text'
             )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        children=["Exchange ", dcc.Input(
                 id='contract-exchange-input', value='IDEALPRO', type='text'
             )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),
    html.Div(
        # The input object itself
        children=["Primary Exchange ", dcc.Input(
                 id='primary-exchange-input', type='text'
             )],
        # Style it so that the submit button appears beside the input.
        style={'display': 'inline-block', 'padding-top': '5px'}
    ),

    html.H4("Order Inputs"),
    # Section title
    #html.H6("Make a Trade"),
    # Div to confirm what trade was made
    html.Div(id='trade-output'),
    # Radio items to select buy or sell
    dcc.RadioItems(
        id='buy-or-sell',
        options=[
            {'label': 'BUY', 'value': 'BUY'},
            {'label': 'SELL', 'value': 'SELL'}
        ],
        value='BUY'
    ),
    html.Br(),
    dcc.RadioItems(
        id='mkt-or-lmt',
        options=[
            {'label': 'Market', 'value': 'MKT'},
            {'label': 'Limit', 'value': 'LMT'}
        ],
        value='MKT'
    ),
    html.Br(),
    html.Label("Limit Price"),
    dcc.Input(id='lmt-price-input', type='number'),
    html.Br(),
    # Text input for the currency pair to be traded
    #dcc.Input(id='trade-currency', value='AUDCAD', type='text'),
    # Numeric input for the trade amount
    #dcc.Input(id='trade-amt', value='20000', type='number'),
    html.Br(),
    html.Label('Total Quantity'),
    dcc.Input(id='trade-amt', value='200', type='number'),
    html.Br(),
    # Submit button for the trade
    html.Button('Trade', id='trade-button', n_clicks=0),
    dcc.ConfirmDialog(
        id='confirm-alert',
        message='',
    ),
    dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], id='table')
])

# Callback for what to do when submit-button is pressed
@app.callback(
    [ # there's more than one output here, so you have to use square brackets to pass it in as an array.
        Output(component_id='currency-output', component_property='children'),
        Output(component_id='candlestick-graph', component_property='figure')
    ],
    Input('submit-button', 'n_clicks'),
    # The callback function will
    # fire when the submit button's n_clicks changes
    # The currency input's value is passed in as a "State" because if the user is typing and the value changes, then
    #   the callback function won't run. But the callback does run because the submit button was pressed, then the value
    #   of 'currency-input' at the time the button was pressed DOES get passed in.
    [State('currency-input', 'value'), State('what-to-show', 'value'),
     State('edt-date', 'date'), State('edt-hour', 'value'),
     State('edt-minute', 'value'), State('edt-second', 'value'),
     State('duration-str', 'value'),
     State('bar-size-setting', 'value'), State('use-RTH', 'value')]
)
def update_candlestick_graph(n_clicks, currency_string, what_to_show,
                             edt_date, edt_hour, edt_minute, edt_second,
                             duration_str, bar_size_setting, use_RTH):
    # n_clicks doesn't
    # get used, we only include it for the dependency.

    if any([i is None for i in [edt_date, edt_hour, edt_minute, edt_second]]):
        endDateTime = ''
    else:
        print(edt_date, edt_hour, edt_minute, edt_second)

    # First things first -- what currency pair history do you want to fetch?
    # Define it as a contract object!
    contract = Contract()
    contract.symbol   = currency_string.split(".")[0]
    contract.secType  = 'CASH'
    contract.exchange = 'IDEALPRO' # 'IDEALPRO' is the currency exchange.
    contract.currency = currency_string.split(".")[1]
    contract_detail = fetch_contract_details(contract)
    if type(contract_detail) == str:
        return ("Error: wrong currency pairs (" + currency_string + "), please check your input"), go.Figure()
    else:
        s = str(contract_detail).split(",")[10]
        if s != currency_string:
            return ("The system currency pairs " + s + " does not match your input " + currency_string), go.Figure()
    ############################################################################
    ############################################################################
    # This block is the one you'll need to work on. UN-comment the code in this
    #   section and alter it to fetch & display your currency data!
    # Make the historical data request.
    # Where indicated below, you need to make a REACTIVE INPUT for each one of
    #   the required inputs for req_historical_data().
    # This resource should help a lot: https://dash.plotly.com/dash-core-components

    # Some default values are provided below to help with your testing.
    # Don't forget -- you'll need to update the signature in this callback
    #   function to include your new vars!
    # cph = fetch_historical_data(
    #     contract=contract,
    #     endDateTime='',
    #     durationStr='30 D',       # <-- make a reactive input
    #     barSizeSetting='1 hour',  # <-- make a reactive input
    #     whatToShow=what_to_show,
    #     useRTH=True               # <-- make a reactive input
    # )
    # # # Make the candlestick figure
    # fig = go.Figure(
    #     data=[
    #         go.Candlestick(
    #             x=cph['date'],
    #             open=cph['open'],
    #             high=cph['high'],
    #             low=cph['low'],
    #             close=cph['close']
    #         )
    #     ]
    # )
    # # # Give the candlestick figure a title
    # fig.update_layout(title=('Exchange Rate: ' + currency_string))
    cph = fetch_historical_data(
        contract=contract,
        endDateTime='',
        durationStr=duration_str,  # <-- make a reactive input
        barSizeSetting=bar_size_setting,  # <-- make a reactive input
        whatToShow=what_to_show,
        useRTH=use_RTH  # <-- make a reactive input
    )
    # # Make the candlestick figure
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=cph['date'],
                open=cph['open'],
                high=cph['high'],
                low=cph['low'],
                close=cph['close']
            )
        ]
    )
    # # Give the candlestick figure a title
    fig.update_layout(title=('Exchange Rate: ' + currency_string))
    print(errmsg)
    return ('Submitted query for ' + currency_string), fig, True, 'Error: ' + errmsg
    ############################################################################
    ############################################################################

    ############################################################################
    ############################################################################
    # This block returns a candlestick plot of apple stock prices. You'll need
    # to delete or comment out this block and use your currency prices instead.
    #df = pd.read_csv(
    #    'https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv'
    #)
    #fig = go.Figure(
    #    data=[
    #        go.Candlestick(
    #            x=df['Date'],
    #            open=df['AAPL.Open'],
    #            high=df['AAPL.High'],
    #            low=df['AAPL.Low'],
    #            close=df['AAPL.Close']
    #        )
    #    ]
    #)
    #
    #currency_string = 'default Apple price data fetch'
    ############################################################################
    ############################################################################

    # Return your updated text to currency-output, and the figure to candlestick-graph outputs
    return ('Submitted query for ' + currency_string), fig

# Callback for what to do when trade-button is pressed
@app.callback(
    # We're going to output the result to trade-output
    Output(component_id='trade-output', component_property='children'),
    Output(component_id='table', component_property='data'),
    # We only want to run this callback function when the trade-button is pressed
    Input('trade-button', 'n_clicks'),
    # We DON'T want to run this function whenever buy-or-sell, trade-currency, or trade-amt is updated, so we pass those
    #   in as States, not Inputs:
    #[State('buy-or-sell', 'value'), State('trade-currency', 'value'), State('trade-amt', 'value')],
    [State('buy-or-sell', 'value'), State('contract-currency-input','value'), State('trade-amt', 'value'), State('mkt-or-lmt', 'value'),
     State('secType-input', 'value'), State('symbol-input', 'value'), State('contract-exchange-input', 'value'),
     State('primary-exchange-input', 'value'),
     State('lmt-price-input', 'value'), ],
    # We DON'T want to start executing trades just because n_clicks was initialized to 0!!!
    prevent_initial_call=True
)
#def trade(n_clicks, action, trade_currency, trade_amt): # Still don't use n_clicks, but we need the dependency
def trade(n_clicks, action, trade_currency, trade_amt, order_type,
          sec_type, symbol, exchange,
          primary_exchange,
          limit_price):
    # Make the message that we want to send back to trade-output
    msg = action + ' ' + trade_amt + ' ' + trade_currency
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exchange  # 'IDEALPRO' is the currency exchange.
    # contract.currency = value.split(".")[1]
    contract.currency = trade_currency
    if primary_exchange is not None:
        contract.primaryExchange = primary_exchange
    order = Order()
    order.action = action
    order.orderType = order_type
    order.totalQuantity = trade_amt
    if order_type == 'LMT':
        if limit_price is None:
            return 'Limit price must have a value!'
        order.lmtPrice = limit_price
    fetch_contract_details_new(contract)
    # file_path = 'submitted_orders.csv'
    file_path = 'submitted_orders.csv'
    info = place_order(contract, order)
    # data = pd.read_csv(file_path)
    # data = pd.concat([data, new_line], axis=1)
    # data.to_csv(file_path)
    order_id = info['order_id'][0]
    client_id = info['client_id'][0]
    perm_id = info['perm_id'][0]
    con_id = contract.conId
    timestamp = info['timestamp'][0]
    new_data = {'timestamp': [''],
                'order_id': [order_id],
                'client_id': [client_id],
                'perm_id': [perm_id],
                'con_id': [con_id],
                'symbol': [symbol],
                'action': [action],
                'size': [trade_amt],
                'order_type': [order_type],
                'lmt_price': [limit_price]}
    new_line = pd.DataFrame(new_data)
    new_line.to_csv(file_path, mode='a', header=False, index=False)
    df = pd.read_csv(file_path)
    # df.columns = ['timestamp', 'order_id', 'client_id', 'perm_id', 'con_id', 'symbol', 'action','size', 'order_type', 'lmt_price']
    print(11111111111111111111111111111111)
    # print(new_line)
    return msg, df.to_dict('records')
    # Make our trade_order object -- a DICTIONARY.
    #trade_order = {
    #    "action": action,
    #   "trade_currency": trade_currency,
    #   "trade_amt": trade_amt
    #}

    # Return the message, which goes to the trade-output div's "children" attribute.
    #return msg

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)
