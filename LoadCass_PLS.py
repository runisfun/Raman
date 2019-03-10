import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_squared_error, r2_score
from scipy.signal import savgol_filter
from sklearn.preprocessing import normalize
from sys import stdout
from Archiv import pyDataHelper
from cassandra.cluster import Cluster
import csv
import datetime as d
import pyCreatePDF as pdf
import os
def Regression():
    cluster = Cluster(['80.93.46.242'], port=3308)
    # formatierne der Columnheads
    columheads = str(pyDataHelper.createColumnHeaders(2))[1:-1]
    columheads=columheads.replace("'", "")
    # get x-variablen
    query_DQL1 = 'SELECT '+columheads+' FROM "projectraman19"."data"'

    data = pyDataHelper.getDataFromCass(query_DQL1)

    #print(data)
    data2 = data.sort_values(by=['datetime'], inplace=True, ascending=False)
    # data2.to_csv('raman.csv')
    #print('Sortierte Data')
    #print(data)


    # get y-variablen
    query_DQL2 = 'SELECT * FROM "projectraman19"."trainData"'
    y_a = pyDataHelper.getDataFromCass(query_DQL2)

    y_a2 = y_a.sort_values(by=['btch', 'time'])
    #y_a2.to_csv('y_a.csv')
    #print(y_a2)
    y_a2 = y_a2.drop('lzh', 1)


    # Vergleichstabelle zur Kontrolle
    vergl = pd.read_csv("_717_722.txt")
    richtig = vergl['3425']
    #print(richtig)
    neu = pd.DataFrame()
    #raman = pd.read_csv("raman.csv")
    for i in richtig:
        ind = data[data['a3325'] == i]
        #print(ind)
        neu = pd.concat([neu,ind], axis=0)

    #print(neu['a3325'])
    data = neu

    '''  # Vergleichstabelle zur Kontrolle
    vergl = pd.read_csv("_717_722.txt")
    print(vergl)
    vergl = vergl.drop('name', 1)
    vergl = vergl.drop('ID', 1)
    vergl = vergl.drop('btch', 1)
    data = vergl

    y_a = pd.read_csv("y_a.csv")
    y_a2 = y_a.sort_values(by=['btch','time'])
    
    '''
    #datenzeile mit PrimaryID, datetime und NaNs deleted
    #data = pd.read_csv("raman.csv")
    data = data.drop('primaryid', 1)
    data = data.drop('datetime', 1)
    data = data.dropna()

    # letzten 300 Wellenlängen nur Noise, werden gelöscht
    for z in range(100, 401):
        querystring = 'a'+str(z)
        data = data.drop(str(querystring), 1)
    # Kontrolle der Werte
    #print([i[1] for i in data['a3325']])

    # für die PLS wird eine y-Variable ausgewählt
    y_param = y_a2['phosphat']
    #print('Yallold:')
    #print(y_param)

    X = data

    # Savitzky Golay: polynom 2. Grades fitting über 25 Spalten und 1. Ableitung
    X2 = savgol_filter(X, 25, polyorder=2, deriv=1)
    # Normalisierung der Daten: Subtraktion Mittelwert und Division durch sd
    X3 = normalize(X2)
    print("SavGolSNV")
    #print(X3)

    #Plot spectra
    plt.figure(figsize=(8, 4.5))
    with plt.style.context(('ggplot')):
        plt.plot(X3.T) # wl
        plt.xlabel('Index')
        plt.ylabel('Smoothed Spectra')
        plt.title('Spectra')
    plt.savefig('spectraSGSNV.png')
    plt.show(block=False) #block=False
    plt.close()


    # Spaltung der Datensätze in Trainings - und Testdatensatz (je 45 Zeilen)
    Y = y_param
    X_train = X3[:90 // 2]
    Y_train = Y[:90 // 2]
    X_test = X3[90 // 2:]
    Y_test = Y[90 // 2:]

    # Standard Partial Least Squares Funktion prediction
    def prediction(X_calib, Y_calib, X_valid, Y_valid, plot_components=False):
        # Run PLS including a variable number of components, up to 40,  and calculate MSE
        mse = []
        component = np.arange(1, 40)
        for i in component:
            pls = PLSRegression(n_components=i)
            # Fit
            pls.fit(X_calib, Y_calib)
            # Prediction
            Y_pred = pls.predict(X_valid)

            mse_p = mean_squared_error(Y_valid, Y_pred)
            mse.append(mse_p)

            comp = 100 * (i + 1) / 40
            # Trick to update status on the same line
            stdout.write("\r%d%% completed" % comp)
            stdout.flush()
        stdout.write("\n")

        # Calculate and print the position of minimum in MSE
        msemin = np.argmin(mse)
        print("Suggested number of components: ", msemin + 1)
        stdout.write("\n")
        #Anzahl der Konponenten der PLS wird gedruckt
        if plot_components is True:
            with plt.style.context(('ggplot')):
                plt.plot(component, np.array(mse), '-v', color='blue', mfc='blue')
                plt.plot(component[msemin], np.array(mse)[msemin], 'P', ms=10, mfc='red')
                plt.xlabel('Number of PLS components')
                plt.ylabel('MSE')
                plt.title('PLS')
                plt.xlim(left=-1)
            # speichern als pdf
            plt.savefig('oofComp.png')
            plt.show(block=False)
            plt.close()


        # Run PLS mit erhaltener Anzahl an Komponenten mit minimiertem MSE
        pls = PLSRegression(n_components=msemin + 1)
        pls.fit(X_calib, Y_calib)
        Y_pred = pls.predict(X_valid)

        # Berechnung der Kennzahlen
        score_p = r2_score(Y_valid, Y_pred)
        mse_p = mean_squared_error(Y_valid, Y_pred)
        sep = np.std(Y_pred[:, 0] - Y_valid)
        rpd = np.std(Y_valid) / sep
        bias = np.mean(Y_pred[:, 0] - Y_valid)

        print('R2: %5.3f' % score_p)
        print('MSE: %5.3f' % mse_p)
        print('SEP: %5.3f' % sep)
        print('RPD: %5.3f' % rpd)
        print('Bias: %5.3f' % bias)
        values = [d.datetime.now(),score_p, mse_p, sep, rpd, bias]
        with open('values.csv', 'a', newline='') as myfile:
            wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
            wr.writerow(values)
        #print(Y_valid)
        #print(Y_pred)

        # Ausgabe der Obs_vs_Pred für Test-Datensatz Phosphat
        if plot_components is True:
            with plt.style.context(('ggplot')):
                tl = np.arange(1, 46)
                plt.plot(tl, Y_valid, 'P', color='blue', mfc='blue')
                plt.plot(tl,Y_pred, 'P', color='red', mfc='red')
                plt.xlabel('')
                plt.ylabel('PHOSPHAT conc')
                plt.title('Red:Observed vs Blue:Predicted')

            plt.savefig('OvsP.png')
            plt.show(block=False)
            plt.close()
        # 2. Plot
        rangey = max(Y_valid) - min(Y_valid)
        rangex = max(Y_pred) - min(Y_pred)

        z = np.polyfit(Y_valid, Y_pred, 1)
        with plt.style.context(('ggplot')):
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.scatter(Y_pred, Y_valid, c='red', edgecolors='k')
            ax.plot(z[1] + z[0] * Y_valid, Y_valid, c='blue', linewidth=1)
            ax.plot(Y_valid, Y_valid, color='green', linewidth=1)
            plt.xlabel('Predicted')
            plt.ylabel('Measured')
            plt.title('Prediction')

            # Kennzahlen auf dem Plot
            plt.text(min(Y_pred) + 0.05 * rangex, max(Y_valid) - 0.1 * rangey, 'R$^{2}=$ %5.3f' % score_p)
            plt.text(min(Y_pred) + 0.05 * rangex, max(Y_valid) - 0.15 * rangey, 'MSE: %5.3f' % mse_p)
            plt.text(min(Y_pred) + 0.05 * rangex, max(Y_valid) - 0.2 * rangey, 'SEP: %5.3f' % sep)
            plt.text(min(Y_pred) + 0.05 * rangex, max(Y_valid) - 0.25 * rangey, 'RPD: %5.3f' % rpd)
            plt.text(min(Y_pred) + 0.05 * rangex, max(Y_valid) - 0.3 * rangey, 'Bias: %5.3f' % bias)
            plt.savefig('OvsP2.png')
            plt.show(block=False)
            plt.close()

    prediction(X_train, Y_train, X_test, Y_test, plot_components=True)
    now = d.datetime.now().strftime("%Y%m%d%H%M%S")
    outputFilename=os.getcwd()+'\Reports\Raman_PLS'+str(now)+'.pdf'
    sourceHtml=pdf.createHTML()
    pdf.convertHtmlToPdf(sourceHtml,outputFilename)

