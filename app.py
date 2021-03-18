import requests
import json
from flask import Flask, render_template, request, jsonify
from coinbase.wallet.client import Client

app = Flask(__name__)

client = Client('https://api.coinbase.com/v2/currencies', '0')

def get_currency_name(cod):
    ''' 
    Obtiene el nombre completo del JSON de la divisa
    
    '''
    try:
        codCurrency = cod.upper()
        url_list = str('https://api.coinbase.com/v2/currencies')
        req = requests.get(url_list)
        if req.json()['data']:
            currencyList = req.json()['data']
            for cod in currencyList:
                if codCurrency == cod['id']:
                    currencyName = cod['name']        
            return currencyName        
    except KeyError:
        return print('Error function') # mensaje de error cuando la moneda es invalida

def get_flag(cod):
    ''' 
    Obtiene el nombre del archivo de la bandera segun la divisa
    
    '''
    routeFlag = './static/flags.json'
    with open(routeFlag) as content:
        flags = json.load(content)
        for flag in flags:            
            if flag.get('code') == cod:                
                return flag.get('file')

def get_price():
    ''' 
    Obtiene el valor de la criptomoneda y la divisa
    
    '''
    _url_api_currency = str('https://api.coinbase.com/v2/prices/spot?currency=USD')            
    # Make the request        
    r = requests.get(_url_api_currency)
    _currencyUSD = get_currency_name('USD')
    _priceUSD = float(r.json()['data']['amount'])   # string amount se convierte a float    
    _priceFormatUSD = f'{_priceUSD:.2f}' # se da formato de 2 decimales al precio     
    return _currencyUSD, _priceFormatUSD

def get_cripto_price(crypto_name = 'BTC', id_currency = 'USD'):
    ''' 
    Obtiene el valor de la criptomoneda y la divisa

    '''
    cripto_pair = crypto_name +'-'+ id_currency    
    cripto_price = client.get_spot_price(currency_pair = cripto_pair)    
    return cripto_price
def get_crypto_icon(base):
    ''' 
    Obtiene el nombre del archivo del icono segun la criptomoneda
    
    '''
    routeIcon = './static/icons.json'
    with open(routeIcon) as content:
        icons = json.load(content)
        for icon in icons:            
            if icon.get('base') == base:                
                return icon.get('file')


@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/currencies', methods=['GET','POST'])
def get_currencies():
    try:   
        _USD = []
        _USD = get_price()
        
        if request.method == 'POST':
            currencyName = ''
            currencyCode = request.form['currency'].upper()           
            # can also use EUR, CAD, etc.        
            _apiKey = str('https://api.coinbase.com/v2/prices/spot?currency=') + currencyCode            
            # Make the request        
            r = requests.get(_apiKey)
            
            if r.json()['data']:
                currencyName = get_currency_name(currencyCode) 
                flagName = get_flag(currencyCode)         
                price = float(r.json()['data']['amount'])   # string amount se convierte a float          
                currencyCode = currencyCode.upper()
                priceFormat = f'{price:.2f}' # se da formato de 2 decimales al precio
                return render_template('currency.html', currencyName = currencyName, price = priceFormat, currencyCode = currencyCode, flagName = flagName)            
    except KeyError:
        currencyNot = r.json()['errors'][0]['message'] # mensaje de error cuando la moneda es invalida
        return render_template('currency.html', currencyName = currencyNot)
    return render_template('currency.html', _USD_curr = _USD[0], _USD_price = _USD[1])

@app.route('/prices')
def prices():
    ''' 
    Obtiene los valores de la criptomoneda para compra, venta y spot en divisa USD
    
    '''
    _resultBuy = client.get_buy_price()
    _resultSell = client.get_sell_price()
    _resultSpot = client.get_spot_price()  
    file_icon = get_crypto_icon('BTC')
     
    return render_template('prices.html', _resultBuy = _resultBuy, _resultSell = _resultSell, _resultSpot = _resultSpot, file_icon = file_icon)
    
@app.route('/criptos', methods = ['GET','POST'])
def criptos():
    ''' 
    Obtiene el precio de la criptomoneda y la divisa
    
    '''
    try:
        # if request.method == 'GET':
        crypto_name = 'BTC'
        id_currency = 'USD'
        pair = []
        pair = get_cripto_price(crypto_name, id_currency)
        file_icon = get_crypto_icon(crypto_name)

        if request.method == 'POST':
            crypto_name = request.form['coin']            
            id_currency = request.form['opc_currency']
            name_currency = get_currency_name(id_currency)
            file_icon = get_crypto_icon(crypto_name)
            pair = []
            pair = get_cripto_price(crypto_name, id_currency)
            flagName = get_flag(id_currency)
            return render_template('criptos.html', pair = pair, name_currency = name_currency, flagName = flagName, file_icon = file_icon)
    except KeyError:
        print('Error')
    return render_template('criptos.html', pair = pair, file_icon = file_icon)


if __name__ == "__main__":
    app.run(debug=True)


