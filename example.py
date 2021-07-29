from sklearn.utils import shuffle
from kNN_LDP import kNN_LDP
from sklearn.datasets import load_iris

iris = load_iris()
"""
Notice that the label -1 indicates that a point belongs to  U in TR = in L u U  
in the regular transductive semi-supervised learning setting. 
""" 
X, y = shuffle(iris.data, iris.target) 
y_unlabelled = [x if i < 15 else -1 for i, x in enumerate(y)]

clf = kNN_LDP(n_neighbors=7)
clf.fit(X, y_unlabelled)

# To derive a crisp decision from the label distribution propagation over U 
print(clf.transduction_)

# From this point the semi-supervised model can be used further for induction: 

# For two new and unseen Iris flowers
x1 = [5,3,1.5,0.3] 
x2 = [6.5,3,5,2.2] 
print(clf.predict([x1,x2]))
