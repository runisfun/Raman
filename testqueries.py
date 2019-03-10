from Archiv import pyDataHelper
from cassandra.cluster import Cluster
cluster = Cluster(['80.93.46.242'], port=3308)
columnheads = str(pyDataHelper.createColumnHeaders(2))[1:-1]
columnheads=columnheads.replace("'", "")
print(columnheads)
query = 'SELECT '+columnheads+' FROM "projectraman19"."data"'
query2 = 'SELECT * FROM "projectraman19"."trainData"'
data = pyDataHelper.getDataFromCass(query2)
data = data.sort_values(by=['time'], inplace=True, ascending=False)

print(data)
