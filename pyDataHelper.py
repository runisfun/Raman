# coding=utf-8
import pandas as pd
from cassandra.cluster import Cluster
import os
from spcmaster import spc

#cluster = Cluster(['127.0.0.1'])
cluster = Cluster(['80.93.46.242'], port=3308)

filename = ''

def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)


def createColumnHeaders(switch):
	i = 1
	#columnames in Liste schreiben switch 1 für create statement switch 2 für insert oder select
	if switch == 1:
		lst = ["PrimaryID INT PRIMARY KEY", "Datetime TIMESTAMP"]
		for i in range(3326):
			lst.append('A'+str(i) +" "+"FLOAT")
		return lst
	if switch == 2:
		lst = ["PrimaryID","Datetime"]
		for i in range(3326):
			lst.append('A'+str(i))
		return lst
		
def getlastID():
	query = "Select MAX(PrimaryID) from projectraman19.data"
	connection = cluster.connect()
	result = connection.execute(query)
	row = result[0]
	return int(row.system_max_primaryid) +1
	connection.shutdown
	
def createTable(query, headers):
	#headers = createColumnHeaders(1)
	connection = cluster.connect()
	query = query +'(' + ','.join((str(n) for n in headers)) + ')'
	print(query)
	connection.execute(query)
	connection.shutdown()
	return "true"
	
def getDataFromCass(query):
	connection = cluster.connect()
	connection.set_keyspace('projectraman19')
	connection.row_factory = pandas_factory
	connection.default_fetch_size = 1000000000 #needed for large queries, otherwise driver will do pagination. Default is 50000.
	#rows = session.execute("""select * from my_table""")
	rows = connection.execute(query)
	df = rows._current_rows
	connection.shutdown()
	return df
	
def formatFileName(filename):
	#es wird datum und Uhrzeit aus dem Filename extrahiert, sollten diese einmal seperat benötigt werden
	#datum = filename[:10].replace("-",".")
	datum = filename[:10]
	zeit = filename[10:18].replace("-",":")
	DateTime = [datum,zeit]
	return DateTime

def convertSPC(directory):
	#Verwendet das Projekt rohanisaac/spc um die SPC Files in CSV zu Convertieren anschließend werden die spc daten in den Ordner 'converted' verschoben
	delim = ','
	for filename in os.listdir(directory):
		fullpath = directory + filename
		loadedpath = directory +'converted/'+filename
		foutp = fullpath[:-4] + '.csv'
		if filename.endswith(".spc") and filename != 'loaded' and filename != 'converted':
			f = spc.File(fullpath)
			f.write_file(foutp, delimiter=delim)
			os.rename(fullpath,loadedpath)
			print(filename +' ins SPC Format konvertiert.')

def importcsv(filepath):
	#csv einlesen
	df = pd.read_csv(filepath, names = ['1','2'], header = None)
	#csv pivotieren
	df = pd.pivot_table(df, values = '2', columns='1')
	#datum aus Dateinamen auselesen
	filename = filepath[-31:]
	print(filename)
	date =formatFileName(filename)
	datetimestr = str("'"+date[0] + " " + date[1]+"'")
	#fortlaufende ID zum Tupel hinzufügen
	df.insert(0, 'PrimaryID', getlastID())
	print(getlastID())
	#Datum hinzufügen
	df.insert(1, 'datetime', datetimestr)
	#Spaltennamen erzeugen
	headers = createColumnHeaders(2)
	#Spaltenwerte erzeugen
	columns = df.values.tolist()
	connection = cluster.connect()
	query = 'INSERT INTO projectraman19.data (' + ','.join((str(n) for n in headers)) + ') VALUES(' + ','.join((str(n) for n in columns[0])) + ')'
	connection.execute(query)
	connection.shutdown()

def importCSVfromFolder(directory):
	#importiert alle zuvor Konvertierten csv Dateien und verschiebt sie anschließend in den Ordner loaded
	convertSPC(directory)
	for filename in os.listdir(directory):
		if filename.endswith(".csv") and filename != 'loaded' and filename != 'converted':
			print('Importiere ' +filename)
			filepath = directory+filename
			loadedpath = directory +'loaded/'+filename
			importcsv(filepath)
			os.rename(filepath,loadedpath)
			print(filename+' wurde erfolgreich in die Datenbank Importiert.')

def importTrainCSVfromFolder(directory):
	#importiert alle zuvor convertierten csv Dateien in die Trainingstabelle
	for filename in os.listdir(directory):
		if filename.endswith(".csv") and filename != 'loaded' and filename != 'converted':
			print('Importiere ' + filename)
			filepath = directory+filename
			loadedpath = directory +'loaded/'+filename
			importcsv(filepath)
			os.rename(filepath,loadedpath)
			print(filename+' wurde erfolgreich in die Datenbank importiert.')

def importTrainData(headers, filepath):
	#csv einlesen
	df = pd.read_csv(filepath)
	df = df.fillna(0)
	#df.time.str.replace('.','-')
	df['time'] = pd.to_datetime(df['time'])
	df[["time"]] = df[["time"]].astype(str) 
	columns = df.values.tolist()
	#print columns
	connection = cluster.connect()
	i = 0
	query = 'truncate "projectraman19"."trainData"'
	connection.execute(query)
	for sublist in columns:
		columns[i][0] = "'"+columns[i][0]+"'"
		columns[i][1] = "'"+columns[i][1]+"'"
		newcol = ', '.join(map(str, columns[i]))
		newcol = newcol.replace("[", "(")
		newcol = newcol.replace("]", ")")
		connection.execute(query)
		query = 'INSERT INTO "projectraman19"."trainData" (' + ','.join((str(n) for n in headers)) + ') VALUES(' + newcol + ')'
		#print(query)
		connection.execute(query)
		i = i+1
	connection.shutdown()
	
def initialidData():
	connection = cluster.connect()
	query = 'INSERT INTO "projectraman19"."data" (PrimaryID) VALUES(1)'
	#print(query)
	connection.execute(query)
	connection.shutdown()
	
def keystore():
	connection = cluster.connect()
	query = "CREATE KEYSPACE projectraman19 WITH replication = {'class':'SimpleStrategy', 'replication_factor':3};"
	connection.execute(query)
	connection.shutdown()
'''
#keystore anlegen
keystore()
#Trainingstabelle erstellen
headersTrain = ['Time TIMESTAMP PRIMARY KEY','Btch TEXT','LZh FLOAT','ACETAT FLOAT','GLUKOSE FLOAT','NH3N FLOAT','PHOSPHAT FLOAT','OD600 FLOAT','Glu FLOAT','Met FLOAT']
queryHeaders = 'CREATE TABLE "projectraman19"."trainData"'
createTable(queryHeaders, headersTrain)

#Trainingsdaten laden
headersTrain = ['Time','Btch','LZh','ACETAT','GLUKOSE','NH3N','PHOSPHAT','OD600','Glu','Met']
importTrainData(headersTrain,"yvalues/y_717_722.txt")

#Datentabelle erstellen
headersData = createColumnHeaders(1)
query='CREATE TABLE "projectraman19"."data1"'
createTable(query,headersData)
'''
#initialidData()
#print(getDataFromCass('Select * from "projectraman19"."trainData"'))
#importCSVfromFolder('spc/')

#print(getDataFromCass('select * from "projectraman19"."data"'))
#print(getDataFromCass('DESC projectraman19.data'))
#convertSPC('/home/pyadmin/sambashare/Raman/spc/')
#importCSVfromFolder('/home/pyadmin/sambashare/Raman/spc/')

