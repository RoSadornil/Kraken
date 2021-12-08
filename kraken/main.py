import krakenex
import pandas as pd
from datetime import datetime, timedelta
import time
import streamlit as st
import plotly.graph_objects as go

# Función que llama a la API con dos argumentos, la moneda y el tiempo (1semana)


def get_data(tradepair, since):
    kraken = krakenex.API()
    timestamp = datetime.timestamp(datetime.now() - timedelta(hours=1))
    timestamp = int(timestamp)
    timetoiterate = since
    data = pd.DataFrame()
    while timetoiterate < timestamp:
        try:
            recentrades = kraken.query_public('Trades', {'pair': tradepair, 'since': timetoiterate})
            timetoiterate = recentrades['result']['last'][0:10]
            timetoiterate = int(timetoiterate)
            data = data.append(recentrades['result'][tradepair])
            # Al hacer muchas request a la api da error
            time.sleep(2)
        except:
            print('Ha habido un problema al conectar con la API')
            break

    # Construir el dataframe, renombrar columnas e indice el tiempo
    head = ['Price', 'Volumen', 'Timestamp', 'Operacion', 'Market/limit', 'miscellaneous']
    data.columns = head
    data.sort_values(by=['Timestamp'], inplace=True)
    data['Timestamp2'] = pd.to_datetime(data['Timestamp'], unit='s')
    data.index = data.Timestamp
    data.sort_index()
    data["Price"] = data["Price"].astype(float)
    data["Volumen"] = data["Volumen"].astype(float)
    return data

# Función que grafica el precio y vwap en función del tiempo


def graph_plotly(data, tradepair):
    fig = go.Figure()
    fig.add_trace(go.Scatter(mode="lines", x=data["Timestamp2"], y=data["Price"], name="Price",
                             line=dict(color='mediumpurple', width=2),
                             fill='tozeroy', fillcolor='#eeecfb'))
    fig.add_trace(go.Scatter(mode="lines", x=data["Timestamp2"], y=data["VWAP"], name="VWAP",
                             line=dict(color='rebeccapurple', width=0.5)))
    fig.update_yaxes(range=[data['Price'].min()-0.5, data['Price'].max()+0.5])
    fig.update_layout(title='Cotización de la criptomoneda ' + str(tradepair),
                      xaxis_title='Time',
                      yaxis_title='Price',
                      plot_bgcolor="white"
                      )
    st.plotly_chart(fig, use_container_width=True)

# Función que calcula el VWAP


def calculo_WPA(data):
    data['Pricexvol'] = data['Price'] * data['Volumen']
    data2 = data[['Timestamp2','Volumen', 'Pricexvol']].rolling(window='1h', on='Timestamp2').sum()
    data2['VWAP'] = data2['Pricexvol'] / data2['Volumen']
    data['VWAP'] = data2['VWAP']
    return data

# MENU


def menu():
    option = st.selectbox(
        '¿De qué moneda quieres visualizar la cotización?',
        ('SUSHIEUR', 'XTZEUR', 'KAVAEUR', 'SRMEUR'))

    st.write('Has seleccionado:', option)
    return option

# imprime el menú para elegir la moneda, por defecto carga SUSHI - EUR


tradepair = menu()

# Utiliza los datos de hace una semana
since = datetime.timestamp(datetime.now() - timedelta(days=7))

# Llama a las funciones para obtener la data y graficarlo
data = get_data(tradepair, since)
calculo_WPA(data)
graph_plotly(data, tradepair)
