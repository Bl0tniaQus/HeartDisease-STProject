import numpy as np
import joblib
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import normalize
data = np.loadtxt("processed.cleveland.data", delimiter=",", dtype='str')
data = np.delete(data, np.where(data=="?")[0],axis=0)

target = data[:,13].astype(float)
target = (target > 0).astype(float)
data = data[:,range(0,13)].astype(float)
datat = data.transpose()

norm_max = 1
norm_min = -1
temp = datat
for row in range(temp.shape[0]):
	maxv = max(temp[row])
	minv = min(temp[row])
	print([minv,maxv])
	vec = []
	for x in temp[row]:
		xnorm = (norm_max - norm_min) * (x - minv) / (maxv - minv) + norm_min
		vec.append(xnorm)
	datat[row] = vec
data = datat.transpose()
print(data[10])
network = MLPRegressor(hidden_layer_sizes=160, max_iter = 1000,activation = 'logistic')
network.fit(data, target)
#result = network.predict(data)
#result = network.predict([])
temp = result
result = []
for v in temp:
	vnorm = (1 - 0) * (v-min(temp)) / (max(temp) - min(temp)) + 0
	result.append(round(vnorm,3))
#for i in range(len(result)):
#	print ([target[i],result[i]])
joblib.dump(network, 'network_extended.ptk', compress=9)

















