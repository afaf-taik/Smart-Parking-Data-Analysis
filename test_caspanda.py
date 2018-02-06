
import pandas as pd
from cassandra.cluster import Cluster
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


cl= Cluster()
session = cl.connect()
session.set_keyspace('smartparking')
select_histo = """select * from historique;"""
select_places = """ select * from places;"""
rs_histo=session.execute(select_histo, timeout=None)
rs_places=session.execute(select_places, timeout=None)
df_places = pd.DataFrame(list(rs_places))
df_histo= pd.DataFrame(list(rs_histo))
df_places.rename(columns={'id':'id_place','heure_fin':'heure_fin_actuelle'},inplace=True)
merged=pd.merge(df_histo,df_places,on='id_place',how="outer")
pd.to_numeric(merged["montant"])
merged.drop('heure_fin_actuelle', axis=1, inplace=True)
merged.drop('heure_fin', axis=1, inplace=True)
merged['heure_debut'] =  pd.to_datetime(merged['heure_debut'])
#print(merged.head(100))
moyenne=np.mean(merged["montant"])
#HPI_State_Correlation = merged.corr()
#print(HPI_State_Correlation)
#des= HPI_State_Correlation.describe()
#print(des)
print("la moyenne est",moyenne)
#merged.set_index('heure_debut')
#print (merged.reset_index().set_index('heure_debut').resample('1D').mean())
ohlc_dict = {
'montant':'sum'}
#'yellow':'sum',
#'handicaped':'sum'}
perday=merged.reset_index().set_index('heure_debut').resample('D').apply(ohlc_dict)
print(perday.head(10))
#alpha = pd.to_numeric(perday['heure_debut'])
perday=perday.astype(float)
perday.plot()
#plt.scatter(perday['yellow'], perday['montant'],label='skitscat', color='k', s=25, marker="o")
plt.show()








