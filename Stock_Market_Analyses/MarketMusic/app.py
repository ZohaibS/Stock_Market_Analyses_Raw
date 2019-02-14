from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import pymongo
import json
import pandas as pd
import os
from bson.json_util import dumps
import numpy as np
from pandas_datareader import data as wb

app = Flask(__name__)

connection = pymongo.MongoClient('ds221155.mlab.com', 21155)
db = connection['stock_eod_data']
db.authenticate('Test', 'Testing1')

client = db

#Home
@app.route('/')
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route('/DJIA')
def Stocks():
    return render_template("DJIA.html")

# @app.route('/indices')
# def indices():
#     """Return the Indices Page."""
#     return render_template("indices.html")

@app.route('/TDA')
def TDA():
    return render_template("TDA.html")
    
@app.route('/RNN')
def RNN():
    return render_template("RNN.html")

@app.route('/DSP')
def DSP():
    return render_template("DSP.html")

@app.route('/DSP_Data')
def DSP_Data():
    cursor = client.DSP
    data1 = cursor.find()
    data3 = dumps(data1)
    return data3

@app.route('/TickTock')
def TickTock():
    cursor = client.TickTock
    data4 = cursor.find()
    data5 = dumps(data4)
    return(data5)

@app.route('/RNN_1')
def RNN_10():
    cursor = client.LSTM_1
    data50 = cursor.find()
    data100 = dumps(data50)
    return data100

@app.route('/RNN_2')
def RNN_20():
    cursor = client.LSTM_2
    data51 = cursor.find()
    data102 = dumps(data51)
    return(data102)

@app.route('/RNN_3')
def RNN_30():
    cursor = client.LSTM_3
    data24 = cursor.find()
    data48 = dumps(data24)
    return data48

@app.route('/RNN_4')
def RNN_40():
    cursor = client.LSTM_4
    data57 = cursor.find()
    data114 = dumps(data57)
    return(data114)

@app.route('/RMS/<TICKER>')
def Signal(TICKER):
    data = pd.DataFrame()
    data[TICKER] = wb.DataReader(TICKER, data_source='yahoo', start='2000-1-1')['Adj Close']
    df = data[TICKER].to_frame()
    data['Delta'] = np.append(np.array([0]), np.diff(data[TICKER].values))
    superposition = np.fft.fft(data['Delta'].values)
    data['Theta'] = np.arctan(superposition.imag/superposition.real)
    data['Frequency'] = np.fft.fftfreq(superposition.size, d=1)
    ValueCount = len(data)
    CountHalf = ValueCount / 2
    data['Amplitude'] = np.sqrt(superposition.real**2 + superposition.imag**2)/CountHalf
    AverageAmplitude = data['Amplitude'].mean()
    StandardDevAmplitude = data['Amplitude'].std()
    ThreeSigmasOverMean = data['Amplitude'] > (3*StandardDevAmplitude + AverageAmplitude) 
    PositiveFrequencies = data['Frequency'] > 0
    Amp = data[ThreeSigmasOverMean & PositiveFrequencies]['Amplitude']
    Freq = data[ThreeSigmasOverMean & PositiveFrequencies]['Frequency']
    Thet = data[ThreeSigmasOverMean & PositiveFrequencies]['Theta']
    DeltaSequence = 0
    for i in range(len(Thet)):
        drift = Thet[i]
        DeltaSequence += Amp[i] * np.cos(i * np.array(range(len(data))) + drift)
    Start = data[TICKER][0]
    Regress = Start + np.cumsum(DeltaSequence)
    Regress_df = pd.DataFrame(data=Regress.flatten())
    Regress_df['Date'] = data.index
    Regression_df = Regress_df.set_index('Date')
    RMS = np.sqrt(np.mean((data[TICKER].values - Regress)**2))
    def Optimizer(std_value):
    
        #Getting dominant values based on std_value
        MuAmp = data['Amplitude'].mean()
        StDevAmp = data['Amplitude'].std()
        AmpFilter = data['Amplitude'] > (std_value*StDevAmp + MuAmp) 
        PositivityFreq = data['Frequency'] > 0
        Amps = data[AmpFilter & PositivityFreq]['Amplitude']
        Freqs = data[AmpFilter & PositivityFreq]['Frequency']
        Thets = data[AmpFilter & PositivityFreq]['Theta']
    
        #Calculating Regression Delta
        RegressionDeltas = 0
        for i in range(len(Thets)):
            Shift = Thets[i]
            RegressionDeltas += Amps[i] * np.cos(i * np.array(range(len(data))) + Shift)



        #Converting Delta Time to Time at start value of real data    
        StartValue = data[TICKER][0]
        Regressor = StartValue - np.cumsum(RegressionDeltas)

        #Calculating RMSE
        RMS = np.sqrt(np.mean((data[TICKER].values - Regressor)**2))
        if np.isnan(RMS):
            RMS = 10000000000000
        return RMS

    #Standard Deviation Optimizer
    StandardDevValues = []
    RMSValues = [] 
    for i in np.linspace(0,2,20):
        StandardDevValues.append(i)
        RMSValues.append(Optimizer(i))

    Epsilon = np.array(RMSValues).argmin()
    MinStDev = StandardDevValues[Epsilon]
    MinRMS = RMSValues[Epsilon]

    #Getting dominant values based on std_value
    MeanAmp = data['Amplitude'].mean()
    StDAmp = data['Amplitude'].std()

    AmpFiltered = data['Amplitude'] > (MinStDev*StDAmp + MeanAmp) 
    FreqPositive = data['Frequency'] > 0
    Ampz = data[AmpFiltered & FreqPositive]['Amplitude']
    Freqz = data[AmpFiltered & FreqPositive]['Frequency']
    Thetz = data[AmpFiltered & FreqPositive]['Theta']

    #Calculating Regression Delta
    RegressedDeltas = 0
    for i in range(len(Thetz)):
        Shift = Thetz[i]
        RegressedDeltas += Ampz[i] * np.cos(i * np.array(range(len(data))) + Shift)

    #Converting Delta Time to Time at start value of real data    
    Starter = data[TICKER][0]
    Regresss = Starter + np.cumsum(RegressedDeltas)
    Regresss_df = pd.DataFrame(data=Regresss.flatten())

    Regresss_df['Date'] = data.index
    Regressed_df = Regresss_df.set_index('Date')
    df=Regressed_df.rename(columns = {'Date':'Days'})
    dff=df.reset_index()

    dff = dff.rename(columns = {0 : 'Predicted','Date':'Days'})

    DF=data.rename(columns = {TICKER : 'Real Values'})
    df_c = pd.concat([DF.reset_index(drop=True), dff['Days']], axis=1)
    df_d=df_c.drop(['Delta', 'Theta', 'Frequency', 'Amplitude'], axis=1)
    df_e=df_d.dropna(axis='columns')
    dff.Days = dff.Days.astype(str)
    df_e.Days = df_e.Days.astype(str)
    records = json.loads(dff.to_json(orient='records'))
    records2 = json.loads(df_e.to_json(orient='records'))



    client.DSP.drop()
    client.DSP.insert(records)

    client.TickTock.drop()
    client.TickTock.insert(records2)

    RootMeanSquare = str(np.sqrt(np.mean((data[TICKER].values - Regresss)**2)))

    #return jsonify(records)
    #return jsonify(records2)
    #return str(RootMeanSquare)
    return redirect('https://market-music.herokuapp.com/DSP')


if __name__ == "__main__":
    app.run(debug=True)
