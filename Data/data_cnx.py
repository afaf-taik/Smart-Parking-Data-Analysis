import matplotlib.pyplot as plt
from cassandra.cluster import Cluster
import numpy

cluster= Cluster()
session= cluster.connect()
session.set_keyspace('Parking')
x=[]
y=[]
#historique (id int,
#				id_place int,
#				heure_debut timestamp,
#				heure_fin timestamp,
#			montant double,
#                PRIMARY KEY (id)
#              );
rows = session.execute("select id_place,montant from historique;")
for row in rows:
	x.append(int(row.id_place))
	y.append(float(row.id_place))

unique, counts = numpy.unique(x, return_counts=True)
plt.bar(unique,counts, label='testing!')
plt.xlabel('parking spots')
plt.ylabel('number of uses')
plt.show()
