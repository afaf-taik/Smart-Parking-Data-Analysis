import pandas as pd
from cassandra.cluster import Cluster
import numpy as np
class Datahandler:
	def __init__(self):
		self.cluster= Cluster()
		self.session = self.cluster.connect()
		self.session.set_keyspace('smartparking')
		self.df=self.db_to_df()

	def db_to_df(self):
		select_histo = """select * from historique;"""
		select_places = """ select * from places;"""
		rs_histo=self.session.execute(select_histo, timeout=None)
		rs_places=self.session.execute(select_places, timeout=None)
		df_places = pd.DataFrame(list(rs_places))
		df_histo= pd.DataFrame(list(rs_histo))
		df_places.rename(columns={'id':'id_place','heure_fin':'heure_fin_actuelle'},inplace=True)
		merged=pd.merge(df_histo,df_places,on='id_place',how="outer")
		pd.to_numeric(merged["montant"])
		merged.drop('heure_fin_actuelle', axis=1, inplace=True)
		merged.drop('heure_fin', axis=1, inplace=True)
		merged['heure_debut'] =  pd.to_datetime(merged['heure_debut'])
		return merged
	

	def resampling(self,dictionnary,frequency):
		return self.df.reset_index().set_index('heure_debut').resample(frequency).apply(dictionnary)

	def plot(self,df):
		df.astype(float)
		df.plot()
		#df.show()
	def statistics(self,frequency):
		df1=self.resampling({'montant':'sum'},frequency) #totaux des sommes payées
		moyenne=np.mean(df1['montant']) #moyenne totale
		df2=self.resampling({'montant':'mean'},frequency) #Moyennes des sommes payées
		df3=self.resampling({'yellow':'sum'},frequency)  #Nbr d'utilisation des parking jaunes
		df4=self.resampling({'handicaped':'sum'},frequency)  #Nbr d'utilisation des espaces pour handicapés

def main():
	datahandler=Datahandler()
	df1=datahandler.df
	df1["montant"].astype(float)
	df1.drop('occupied', axis=1, inplace=True)
	df1.drop('id', axis=1, inplace=True)
	df1.drop('id_place', axis=1, inplace=True)
	table= pd.pivot_table(df1,index=["heure_debut","yellow","handicaped","close_to"],values=["montant"],aggfunc=[np.sum])
	print(table.head(50))

main()