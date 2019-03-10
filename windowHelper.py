import LoadCass_PLS as reg
import pyDataHelper as pdh
import pandas as pd
import os
import datetime
now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#Messwerte aus CSV File lesen (Die letzten 5)
def readCSV():
    valuesCSV = pd.read_csv('values.csv')
    return valuesCSV.tail()
#Prüfen ob neue Importfiles vorliegen
def readImportDir(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".spc") and filename != 'loaded' and filename != 'converted':
            print('Datei '+filename+' zum Import bereit.')
        if filename.startswith('y_') and filename.endswith('.csv'):
            print('Datei '+filename+' zum Import bereit.')
#Import ausführen
def importCSVfromForm():
    print('test')
    #Fuinktion zum Massenimport aus Pydatahelper aufrufen
    pdh.importCSVfromFolder('spc/')
    pdh.importTrainCSVfromFolder('yvalues/')
    print('Import abgeschlossen.')
    #Erfolgsmeldung ausgeben
#Regression ausführen
def doRegression():
    reg.Regression()
    #Funktion Regression() aus LoadCass_PLS ausführen
    #Anschließend Messungen im Formular aktualisieren
    readCSV()
#X und Y Werte in CSV Exportieren um Sie in Excel Analysierbar zu machen
def exportX():
    #Query aus Datahelper ausführen und in CSV Umwandeln
    columheads = str(pdh.createColumnHeaders(2))[1:-1]
    columheads=columheads.replace("'", "")
    filename = 'xdata'+now+'.csv'
    path = os.path.abspath('export/'+filename)
    print(path)
    export = pdh.getDataFromCass('SELECT '+columheads+' FROM "projectraman19"."data"')
    export.to_csv(path, sep='\t', encoding='utf-8')
    print('Datei erfolgreich exportiert nach. export/xdata'+now+'.csv')
def exportY():
    #Query aus Datahelper ausführen und in CSV Umwandeln
    filename = 'ydata'+now+'.csv'
    path = os.path.abspath('export/'+filename)
    export = pdh.getDataFromCass('Select * from"projectraman19"."trainData"')
    export.to_csv(path, sep='\t', encoding='utf-8')
    print('Datei erfolgreich exportiert nach. export/xdata'+now+'.csv')

