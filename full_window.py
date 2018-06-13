#from __future__ import print_function
import sys
from parkingwindow import Ui_MainWindow
from cassandra.cluster import Cluster
import gestiondonnees
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QCursor
from PyQt5.QtCore import QSize, Qt
import pandas as pd
#from pandas.tseries.offsets import MonthBegin, YearEnd , Week
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
import numpy as np
import scipy.spatial as spatial
#import pdfkit as pdf
#from jinja2 import Environment, FileSystemLoader
import datetime
import time


class Visualizer(QMainWindow,Ui_MainWindow):
	def __init__(self,datahandler):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self._datahandling=datahandler

		self._set_table_entries_df(self.tableWidgetHistorique,self._load_data(4))
		self._setup_signals()

	#Configuring the signals for buttons
	def _setup_signals(self):		
		self.optAffchgBtn.clicked.connect(self.handlebutton)
		self.rappHebdoBtn.clicked.connect(self._datahandling._pdf_generator_week)
		self.rapMensuelBtn.clicked.connect(self._datahandling._pdf_generator_month)
		self.rapAnnuelBtn.clicked.connect(self._datahandling._pdf_generator_year)
		self.rapGlobalBtn.clicked.connect(self._datahandling._pdf_generator_all)
		#self.freqAffichList.currentIndexChanged.connect(self.create_numbers_overview)
		canvas=self.create_numbers_overview()
		self.horizontalLayout.addWidget(canvas)
		canvas2=self.create_amount_overview()
		self.horizontalLayout_2.addWidget(canvas2)
		canvas3=self.create_places_overview()
		self.horizontalLayout_3.addWidget(canvas3)
		self.canvas4=self.create_places_overview()
		self.calcul_layout_graph.addWidget(self.canvas4)
		self.AddPlace.clicked.connect(self.add_category)
		self.DelPlace.clicked.connect(self.delete_category)
		self.ImportPlaces.clicked.connect(self.get_file_places)
		self.Calculer.clicked.connect(self.result_calculs)


	#bouton d'affichage des donnees brutes 
	def handlebutton(self):
		a=self.checkboxes_case_finder()
		self._set_table_entries_df(self.tableWidgetHistorique,self._load_data(a))




##################################################################################################################
#
##Filtering and showing data
#
##################################################################################################################

#voir l'etat des checkboxes du 1er tab
	def checkboxes_case_finder(self):
		if (self.jaune.isChecked() and 	self.horodateur.isChecked() and self.handicaped.isChecked()):
			return 0
		elif(self.jaune.isChecked() and self.horodateur.isChecked()):
			return 1
		elif(self.jaune.isChecked() and self.handicaped.isChecked()):
			return 2
		elif(self.handicaped.isChecked() and self.horodateur.isChecked()):
			return 3
		elif(self.handicaped.isChecked()):
			return 4
		elif(self.horodateur.isChecked()):
			return 5
		elif(self.jaune.isChecked()):
			return 6
#check_boxes du tab calcul
	def checkboxes_case_finder_2(self):
		if (self.jaune_2.isChecked() and self.horodateur_2.isChecked() and self.handicaped_2.isChecked()):
			return 0
		elif(self.jaune_2.isChecked() and self.horodateur_2.isChecked()):
			return 1
		elif(self.jaune_2.isChecked() and self.handicaped_2.isChecked()):
			return 2
		elif(self.handicaped_2.isChecked() and self.horodateur_2.isChecked()):
			return 3
		elif(self.handicaped_2.isChecked()):
			return 4
		elif(self.horodateur_2.isChecked()):
			return 5
		elif(self.jaune_2.isChecked()):
			return 6
		

	def _set_table_entries(self, table, data):
		"""
			Set table data from list
		"""
		if data:
			table.setRowCount(len(data))
			table.setColumnCount(len(data[0]))

			for i in range(len(data)):
				for j in range(len(data[0])):
					table.setItem(i, j, QTableWidgetItem(str(data[i][j])))
		else:
			table.setRowCount(0)

	def _set_table_entries_df(self, table, df):
		"""
			Set table data from dataframe
		"""
		# table.setRowCount(0)
		col_count = len(df.columns) - 1
		row_count = len(df.index)

		table.setSelectionBehavior(QAbstractItemView.SelectRows)
		table.setColumnCount(col_count)
		table.setHorizontalHeaderLabels(list(df.columns)[1:])
		table.setRowCount(row_count)

		for i in range(row_count):
			for j in range(col_count):
				table.setItem(i, j, QTableWidgetItem(str(df.iloc[i][j+1])))

#returns masked dataframe depending on which checkboxes the user has chosen ( yellow , handicaped and )
	def _load_data(self,case):
		#all data
		#this seems to fix an error I don't understand for now 
		global mask
		if(case==0 or case==4):
			return self._datahandling.df
		#yellow+horodateur, non handicaped-spaces
		elif(case==1):
			mask= self._datahandling.df['handicaped'].values==0
		#yellow+handicaped
		elif(case==2):
			mask= self._datahandling.df['yellow'].values!=0
		#horodateur+handicaped
		elif(case==3):
			mask= self._datahandling.df['yellow'].values==0
		elif(case==5):
			mask= (self._datahandling.df['yellow'].values==0) & (self._datahandling.df['handicaped'].values==0)
		elif(case==6):
			mask= (self._datahandling.df['yellow'].values!=0) & (self._datahandling.df['handicaped'].values==0)
		return self._datahandling.df[mask]

	def load_data_date_mask(self,df,d1,d2):
		global mask
		df.set_index('heure_debut')
		mask = (df['heure_debut']<d2) & (df['heure_debut']>d1) 
		return df[mask]


##################################################################################################################
#
##Toolbox
#
##################################################################################################################
	def calculs_custom(self,df):
		matrix=[['','Utilisations','Montants']]
		if(df.empty):
			matrix.extend([['Total',0,0],['Maximum',0,0],['Minimum',0,0],['Moyenne',0,0],['Variance',0,0],['Etendue',0,0]])
		else:
			if self.Somme.isChecked():	
				matrix.append(['Total',df.shape[0],df['montant'].sum()])
			if self.Moyenne.isChecked():
				matrix.append(['Moyenne',np.mean(df.groupby(['close_to']).size()),np.mean(df.groupby(['close_to'])['montant'].sum())])
			if self.Maximum.isChecked():
				matrix.append(['Maximum',np.max(df.groupby(['close_to']).size()),np.max(df.groupby(['close_to'])['montant'].sum())])
			if self.Minimum.isChecked():
				matrix.append(['Minimum',np.min(df.groupby(['close_to']).size()),np.min(df.groupby(['close_to'])['montant'].sum())])
			if self.Variance.isChecked():
				matrix.append(['Variance',np.var(df.groupby(['close_to']).size()),np.var(df.groupby(['close_to'])['montant'].sum())])
			if self.Variance.isChecked():
				matrix.append(['Etendue',np.std(df.groupby(['close_to']).size()),np.std(df.groupby(['close_to'])['montant'].sum())])				
		return matrix

	def result_calculs(self):
		a=self.checkboxes_case_finder_2()
		df=self.load_data_date_mask(self._load_data(a),self.datemin.date().toPyDate(),self.datemax.date().toPyDate())
		matrix=self.calculs_custom(df)
		self._set_table_entries(self.calculsTable,matrix)
		self.calcul_layout_graph.removeWidget(self.canvas4)
		self.canvas4.close()	
		self.canvas4=self.create_places_overview_c(df)
		self.calcul_layout_graph.addWidget(self.canvas4)
		self.calcul_layout_graph.update()

##################################################################################################################
#
##Plots
#
##################################################################################################################

	def reset_plots(self):
		#Delete all plots for redrawing
		plt.close("all")

	
	def _create_overall_counts(self,fig):			
		ax = fig.add_subplot(111)
		ax.set_title('Total utilisations', fontweight='bold', fontsize=12)
		frequence='M'
		df1,df2=self._datahandling.statistics_usage(frequence)		
		df1.plot(ax=ax,kind='line') 
		df2.plot(ax=ax,kind='line')

	def create_numbers_overview(self):
		fig = plt.figure(figsize=(1, 3))
		self._create_overall_counts(fig)
		canvas = FigureCanvas(fig)
		return canvas	

	
	def _create_overall_amounts(self,fig):			
		ax = fig.add_subplot(111)
		ax.set_title('Montants payés', fontweight='bold', fontsize=12)
		frequence='M'
		df1,df2=self._datahandling.statistics_payments(frequence)		
		df1.plot(ax=ax,kind='line') 
		df2.plot(ax=ax,kind='line')

	def create_amount_overview(self):
		fig = plt.figure(figsize=(1, 3))
		self._create_overall_amounts(fig)
		canvas = FigureCanvas(fig)
		return canvas	


#stats_for_placement
	def _create_stats_places(self,fig):			
		ax = fig.add_subplot(111)
		ax.set_title('Montants payés par emplacement', fontweight='bold', fontsize=12)
		df1=self._datahandling.stats_for_placement()	
		df1.plot(ax=ax,kind='barh') 
		#df2.plot(ax=ax,kind='bar')

	def create_places_overview(self):
		fig = plt.figure(figsize=(1, 3))
		self._create_stats_places(fig)
		canvas = FigureCanvas(fig)
		return canvas	
#Stats for placement that goes with the toolbox
	def stats_for_placement(self,df):
		return df.groupby(['close_to'])['montant'].agg(['sum']) 

	def stats_for_placement_use(self,df):
		return df.groupby(['close_to']).size()

	def _create_stats_places_c(self,fig,df):
		ax = fig.add_subplot(111)
		if(str(self.Use_Montants.currentText())=='Utilisations'):
			ax.set_title('Nombre d\'utilisations par emplacement', fontweight='bold', fontsize=12)
			df1=self.stats_for_placement_use(df)
		else:
			ax.set_title('Montants payés par emplacement', fontweight='bold', fontsize=12)
			df1=self.stats_for_placement(df)
		if(df1.empty==False):	
			df1.plot(ax=ax,kind='barh') 
			


	def create_places_overview_c(self,df):
		plt.close("all")
		fig = plt.figure(figsize=(1, 3))
		self._create_stats_places_c(fig,df)
		canvas = FigureCanvas(fig)
		return canvas	



##################################################################################################################
#
##DataBaseHandling
#
##################################################################################################################

#Functions that help taking care of the categories
	def get_file_places(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', )
		if fname:
			query = "COPY places from " + fname + " WITH HEADER=TRUE;"
			self._datahandling.session.execute(query)  		

	def add_category(self):
		categorie=self.lineEdit.text()
		exists=0
		for c in self.categories:
			if(c==categorie):
				exists=1
		if exists==0 and categorie!='':
			query= "ALTER TABLE places ADD" + categorie + "int;"
			self._datahandling.session.execute(query)
			self.categories.append(categorie)
			self.updateCategories()
		belong_to=0
		if self.checkBox.isChecked():
			belong_to=1
		query2="UPDATE places SET "+categorie+"="+belong_to+";"
		self._datahandling.session.execute(query2)

	def delete_category(self):
		categorie= str(self.select_categorie.currentText())
		query= "ALTER TABLE places drop " + categorie + ";"
		self._datahandling.session.execute(query)
		self.categories.append(categorie)
		self.updateCategories()


##################################################################################################################
#
##Main Call
#
##################################################################################################################
def main():
	app = QApplication(sys.argv)
	datahandler=gestiondonnees.Datahandler()
	v=Visualizer(datahandler)
	v.show()
	app.exec_()

if __name__ == '__main__':
	main()


	


