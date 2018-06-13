from __future__ import print_function
import pandas as pd
from cassandra.cluster import Cluster
import numpy as np
import pdfkit as pdf
from jinja2 import Environment, FileSystemLoader
import datetime
import time
from pandas.tseries.offsets import MonthBegin, YearEnd , Week
class Datahandler:
	def __init__(self):
		self.cluster= Cluster()
		self.session = self.cluster.connect()
		self.session.set_keyspace('smartparking')
		self.df=self.db_to_df()
	#Getting data from the database and returning a merged dataframe	
	def db_to_df(self):
		#queries
		select_histo = """select * from historique;"""
		select_places = """ select * from places;"""
		#executing the queries
		rs_histo=self.session.execute(select_histo, timeout=None)
		rs_places=self.session.execute(select_places, timeout=None)
		#transforming the data into dataframes
		df_places = pd.DataFrame(list(rs_places))
		df_histo= pd.DataFrame(list(rs_histo))
		#fixing what should be fixed and removing useless information
		df_places.rename(columns={'id':'id_place','heure_fin':'heure_fin_actuelle'},inplace=True)
		merged=pd.merge(df_histo,df_places,on='id_place',how="outer")
		pd.to_numeric(merged["montant"])
		merged.drop('heure_fin_actuelle', axis=1, inplace=True)
		merged.drop('heure_fin', axis=1, inplace=True)
		merged['heure_debut'] =  pd.to_datetime(merged['heure_debut'])
		return merged
	

	def statistics_usage(self,frequency):
	
		#Nbr d'utilisation des parking jaunes
		df_total_jaune= self.df.reset_index().set_index('heure_debut').resample(frequency).apply({'yellow':'sum'})
		#Nbr d'utilisation des espaces pour handicapés
		df_total_handicape=self.df.reset_index().set_index('heure_debut').resample(frequency).apply({'handicaped':'sum'})
  
		return df_total_jaune , df_total_handicape

	def statistics_payments(self,frequency):
		self.df["montant"]=self.df["montant"].astype(float)
		return self.df.reset_index().set_index('heure_debut').resample(frequency).apply({'montant':'sum'}), self.df.reset_index().set_index('heure_debut').resample(frequency).apply({'montant':'mean'})

	def stats_for_placement(self):
		#return self.df.groupby(['close_to',pd.Grouper(key='heure_debut',freq='A')])['montant'].sum() 
		return self.df.groupby(['close_to'])['montant'].sum() 

	def stats_for_placement_use(self):
		return self.df.groupby(['close_to']).count()			


	#Applying Date - Time mask on the data to return only what we need ( This week's , this month , this year )
	def load_data_frequency(self,frequence):
		global mask
		global start_date
		end_date=datetime.datetime.now()
		#Semaine
		if(frequence=='W'):
			start_date= end_date- Week()
		#Mois
		elif(frequence=='M'):
			start_date= end_date- MonthBegin(n=1)
		#Année
		elif(frequence=='A'):
			start_date=end_date -  YearEnd()
		
		self.df.set_index('heure_debut')
		#self._datahandling.df[self._datahandling.df['heure_debut'].isin(pd.date_range(start_date, end_date))]
		mask = (self.df['heure_debut']<end_date) & (self.df['heure_debut']>start_date) 
		return start_date,self.df[mask]




	def _pdf_generator_week(self):
		#t = time.time()
		now = datetime.datetime.now()
		#d = now - datetime+.timedelta(days=7)
		#importing data and creating pivot table
		frequence='W'
		start_date,df1=self.load_data_frequency(frequence)
		df1.is_copy=False
		#print(df1.head(10))
		df1["montant"].astype(float)
		df1.drop('occupied', axis=1, inplace=True)
		df1.drop('id', axis=1, inplace=True)
		df1.drop('id_place', axis=1, inplace=True)	
		table= pd.pivot_table(df1,index=["close_to","yellow","handicaped"],values=["montant"],aggfunc=[np.sum])
	
		#variables to put in the html
		total_use=len(df1)
		nbr_use_yellow=np.sum(df1["yellow"])
		nbr_use_horodateur=total_use-nbr_use_yellow
		nbr_use_handicaped=np.sum(df1["handicaped"])
		total_wins=np.sum(df1["montant"])
		mean_wins=np.mean(df1["montant"])

		template_vars = {"title" : "Rapport",
				 "global_pivot_table": table.to_html(),
				 "montant_total" : str(total_wins), 
				 "montant_moyen":str(mean_wins) ,
				  "use_jaune": str(nbr_use_yellow) ,
				  "total_use":str(total_use),
				  "use_handicaped": str(nbr_use_handicaped),
				  "use_horodateur":str(nbr_use_horodateur)}
	
		#stuff for jinja
		env = Environment(loader=FileSystemLoader('.'))
		template = env.get_template("template.html")

		#configuration for pdfkit
		path_wkthmltopdf ='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
		config = pdf.configuration(wkhtmltopdf=path_wkthmltopdf)

		#rendering the html and converting it to pdf
		html_out = template.render(template_vars)
		pdfreport='Reports\\rapport_hebdomadaire_'+now.strftime("%Y-%m-%d_%H_%M")+'.pdf'
		pdf.from_string(html_out,pdfreport,configuration=config,css='style.css')		

	def _pdf_generator_month(self):
		#t = time.time()
		now = datetime.datetime.now()
		#d = now - datetime+.timedelta(days=7)
		#importing data and creating pivot table
		frequence='M'
		start_date,df1=self.load_data_frequency(frequence)
		df1.is_copy=False
		#print(df1.head(10))
		df1["montant"].astype(float)
		df1.drop('occupied', axis=1, inplace=True)
		df1.drop('id', axis=1, inplace=True)
		df1.drop('id_place', axis=1, inplace=True)	
		table= pd.pivot_table(df1,index=["close_to","yellow","handicaped"],values=["montant"],aggfunc=[np.sum])
	
		#variables to put in the html
		total_use=len(df1)
		nbr_use_yellow=np.sum(df1["yellow"])
		nbr_use_horodateur=total_use-nbr_use_yellow
		nbr_use_handicaped=np.sum(df1["handicaped"])
		total_wins=np.sum(df1["montant"])
		mean_wins=np.mean(df1["montant"])

		template_vars = {"title" : "Rapport",
				 "global_pivot_table": table.to_html(),
				 "montant_total" : str(total_wins), 
				 "montant_moyen":str(mean_wins) ,
				  "use_jaune": str(nbr_use_yellow) ,
				  "total_use":str(total_use),
				  "use_handicaped": str(nbr_use_handicaped),
				  "use_horodateur":str(nbr_use_horodateur)}
	
		#stuff for jinja
		env = Environment(loader=FileSystemLoader('.'))
		template = env.get_template("template.html")

		#configuration for pdfkit
		path_wkthmltopdf ='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
		config = pdf.configuration(wkhtmltopdf=path_wkthmltopdf)

		#rendering the html and converting it to pdf
		html_out = template.render(template_vars)
		pdfreport='Reports\\rapport_mensuel_'+now.strftime("%Y-%m-%d_%H_%M")+'.pdf'
		pdf.from_string(html_out,pdfreport,configuration=config,css='style.css')	
	

	def _pdf_generator_year(self):
		now = datetime.datetime.now()
		frequence='A'
		start_date,df1=self.load_data_frequency(frequence)
		df1.is_copy=False
		#print(df1.head(10))
		df1["montant"].astype(float)
		df1.drop('occupied', axis=1, inplace=True)
		df1.drop('id', axis=1, inplace=True)
		df1.drop('id_place', axis=1, inplace=True)	
		table= pd.pivot_table(df1,index=["close_to","yellow","handicaped"],values=["montant"],aggfunc=[np.sum])
	
		#variables to put in the html
		total_use=len(df1)
		nbr_use_yellow=np.sum(df1["yellow"])
		nbr_use_horodateur=total_use-nbr_use_yellow
		nbr_use_handicaped=np.sum(df1["handicaped"])
		total_wins=np.sum(df1["montant"])
		mean_wins=np.mean(df1["montant"])

		template_vars = {"title" : "Rapport",
				 "global_pivot_table": table.to_html(),
				 "montant_total" : str(total_wins), 
				 "montant_moyen":str(mean_wins) ,
				  "use_jaune": str(nbr_use_yellow) ,
				  "total_use":str(total_use),
				  "use_handicaped": str(nbr_use_handicaped),
				  "use_horodateur":str(nbr_use_horodateur)}
	
		#stuff for jinja
		env = Environment(loader=FileSystemLoader('.'))
		template = env.get_template("template.html")

		#configuration for pdfkit
		path_wkthmltopdf ='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
		config = pdf.configuration(wkhtmltopdf=path_wkthmltopdf)

		#rendering the html and converting it to pdf
		html_out = template.render(template_vars)
		pdfreport='Reports\\rapport_annuel_'+now.strftime("%Y-%m-%d_%H_%M")+'.pdf'
		pdf.from_string(html_out,pdfreport,configuration=config,css='style.css')	

	def _pdf_generator_all(self):
		now = datetime.datetime.now()
		df1=self.df
		df1.is_copy=False
		#print(df1.head(10))
		df1["montant"].astype(float)
		df1.drop('occupied', axis=1, inplace=True)
		df1.drop('id', axis=1, inplace=True)
		df1.drop('id_place', axis=1, inplace=True)	
		table= pd.pivot_table(df1,index=["close_to","yellow","handicaped"],values=["montant"],aggfunc=[np.sum])
	
		#variables to put in the html
		total_use=len(df1)
		nbr_use_yellow=np.sum(df1["yellow"])
		nbr_use_horodateur=total_use-nbr_use_yellow
		nbr_use_handicaped=np.sum(df1["handicaped"])
		total_wins=np.sum(df1["montant"])
		mean_wins=np.mean(df1["montant"])

		template_vars = {"title" : "Rapport",
				 "global_pivot_table": table.to_html(),
				 "montant_total" : str(total_wins), 
				 "montant_moyen":str(mean_wins) ,
				  "use_jaune": str(nbr_use_yellow) ,
				  "total_use":str(total_use),
				  "use_handicaped": str(nbr_use_handicaped),
				  "use_horodateur":str(nbr_use_horodateur)}
	
		#stuff for jinja
		env = Environment(loader=FileSystemLoader('.'))
		template = env.get_template("template.html")

		#configuration for pdfkit
		path_wkthmltopdf ='C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
		config = pdf.configuration(wkhtmltopdf=path_wkthmltopdf)

		#rendering the html and converting it to pdf
		html_out = template.render(template_vars)
		pdfreport='Reports\\rapport_global_'+now.strftime("%Y-%m-%d_%H_%M")+'.pdf'
		pdf.from_string(html_out,pdfreport,configuration=config,css='style.css')	

