import pickle

#enregistrement des categories disponibles
l=['yellow','handicaped']

output_file = open("categories.pickle", "wb")

pickle.dump(l, output_file)

 
output_file.close()
#pickle_in = open("categories.pickle","rb")
#example_dict = pickle.load(pickle_in)
#print(example_dict)
#pickle_in.close()