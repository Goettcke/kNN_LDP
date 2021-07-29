import math
import numpy as np  
from scipy.spatial import cKDTree
from sklearn.datasets import load_iris

def knn_and_rnn(X, k=7,get_distances=False):
    # TODO make a version handling ties. 
    """
    Method to return knn's and rnn's for all elements
    :param X numpy array containing data:
    :param k number of nearest neighbors to use:
    :return tuple ([][]) containing a list of nearest neighbors and a list of reverse nearest neighbors:
    """

    # This is also easier to modify for handling ties further down the road.
    ckdtree = cKDTree(X, leafsize=k+1)
    knn_array = [0] * len(X)  # Initializing the array like this, is done because of runtime concerns.
    rnn_array = [[] for _ in range(len(X))]  # There is reasoning behind why the arrays are initialized, the first is faster, the other is to ensure new pointers for each list
    distance_array = [0]*len(X)
    
    for index in range(len(X)):
        distances, neighbors = ckdtree.query(X[index],k=k + 1)  # Lookup the unlabelled points, k nearest neighbors. The first nearest k+1 because the first nearest neighbor is the point itself)
        neighbors = neighbors.tolist()  # Here we remove the query point from the neighbors
        distances.tolist()
        try : 
            neighbors.remove(index) # with a small k, and a dataset with many points on top of each other it's not guaranteed, that the query point is in its own set of  nearest neighbors
        except: 
            pass
        knn_array[index] = neighbors  # Update the knn array
        distance_array[index] = distances # Update the knn array
        # Update the rnn array during queries, to minimize runtime
        for neighbor in neighbors:
            rnn_array[neighbor].append(index)
    if get_distances == False : 
        output_tuple = (knn_array, rnn_array,ckdtree)
    else : 
        output_tuple = (knn_array, rnn_array,ckdtree,distance_array)
    return output_tuple

def get_symmetry_favored_graph(X,sigma,k=7) : 
    """
    Generates the symmetry favored graph, as defined in Robust Multi-Class Transductive Learning with Graphs by Wei Liu and Shih-Fu Chang

    Keyword arguments:
    X -- A 2d-numpy array containing the data. 
    
    Returns: 
    A numpy matrix, representing the symmetry favored knn graph.
    """

    n = len(X)
    A = np.zeros((n,n))
    W = np.zeros((n,n))
    
    knn_array,rnn_array,_,distance_array = knn_and_rnn(X,k=k,get_distances=True)
    for i in range(n): 
        for j in range(n): 
            # if j in ni else 0 
            if j in knn_array[i]: 
                A[i,j] = math.exp(-(np.linalg.norm(X[i]-X[j])/sigma**2))
            else : 
                A[i,j] = 0 

    #This for loop (mess) is the same as equation 2 in the paper. Which yieds the same solution as.
    # for i in range(n): 
    #     for j in range(n): 
    #         if j in knn_array[i] and i in knn_array[j]: 
    #             W[i,j] = A[i,j] + A[j,i]
    #         elif not (j in knn_array[i]) and i in knn_array[j]: 
    #             W[i,j] = A[j,i]
    #         else : 
    #             W[i,j] = A[i,j]

    W = A + A.transpose() 
    return W 

if __name__=='__main__': 
    print("test 1 ok")
    iris = load_iris()
    knn_array,rnn_array,ckdtree = knn_and_rnn(iris.data)
    #print(knn_array)
    print("test 2 ok")
    knn_array,rnn_array,ckdtree,distance_array = knn_and_rnn(iris.data,k=7,get_distances=True)
    get_symmetry_favored_graph(iris.data,0.48) #Just because I know that is the Sigma value