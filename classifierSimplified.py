import numpy as np
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import normalize

#przygotowanie danych
data = np.loadtxt("processed.cleveland.data", delimiter=",", dtype='str')
data = np.delete(data, np.where(data=="?")[0],axis=0)

target = data[:,13].astype(float)
target = (target > 0).astype(float)
data = data[:,[0,1,2,3,4,5,7,8]].astype(float)
datat = data.transpose()

#normalizacja danych
norm_max = 1
norm_min = -1
temp = datat
for row in range(temp.shape[0]):
	minv = min(temp[row])
	maxv = max(temp[row])
	if row==0:
		minv = 18
		maxv = 80
	elif row==3:
		minv = 90
	elif row == 4:
		minv = 120
		maxv = 600
	elif row == 7:
		minv = 70
		maxv = 210
	vec = []
	for x in temp[row]:
		xnorm = (norm_max - norm_min) * (x - minv) / (maxv - minv) + norm_min
		vec.append(xnorm)
	datat[row] = vec
data = datat.transpose()

#sieć neuronowa
network = MLPRegressor()
network._old_initialize=network._initialize
def _initialize(self, y, layer_units, dtype):
    self._old_initialize(y, layer_units, dtype)
    self.out_activation_="logistic" 
network._initialize = _initialize.__get__(network)
network.hidden_layer_sizes=155
network.max_iter = 300
network.activation = 'logistic'
network.learning_rate = 'adaptive'
network.solver = "adam"
network.fit(data, target)
result = network.predict(data)




#diagnostyka modelu	
confusion_matrix = [[0,0,0,0],[0,0,0,0]]
for i in range(len(result)):
	if result[i]>=0 and result[i]<0.25:
		level = 0
	elif result[i]>=0.25 and result[i]<0.50:
		level = 1
	elif result[i]>=0.50 and result[i]<0.75:
		level=2
	elif result[i]>=0.76 and result[i]<=1:
		level=3
	if target[i] == 0:
		confusion_matrix[0][level] = confusion_matrix[0][level] + 1
	elif target[i] == 1:
		confusion_matrix[1][level] = confusion_matrix[1][level] + 1
print(confusion_matrix[0])
print(confusion_matrix[1])

#eksport modelu
joblib.dump(network, './static/network_simplified.ptk', compress=9)


















