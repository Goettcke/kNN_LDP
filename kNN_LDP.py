from math import isclose
from collections import Counter,defaultdict
from utils.super_heap import SuperHeap
from utils.neighborhoods import knn_and_rnn
from sklearn.metrics import accuracy_score

class kNN_LDP_Node:
    def __init__(self, label_distribution, knn, index, rnn=None):
        self.label_distribution = label_distribution
        self.knn = knn
        self.rnn = rnn  # Reverse nearest neighbors are none from the beginning
        self.index = index  # Index in the original data array
        self.heap_index = -1  # -1 as long as the point is not in the heap.

    def __str__(self):
        return f"({self.index},{self.label_distribution},{self.heap_index},{self.knn},{self.rnn})"

    def __repr__(self):
        return self.__str__()


class kNN_LDP:
    def __init__(self, n_neighbors=10):
        self.n_neighbors = n_neighbors
        self.X = None  # self.X and self.y are set in the fit method
        self.y = None
        self.data_list = []
        self.label_set = None
        self.X_ = None  # input array
        self.classes_ = None  # The distinct labels used in classifying instances
        self.label_distributions_ = None  # Categorical distribution for each item
        self.transduction_ = []  # n_d array with labels assigned to each item during transduction
        self.n_iter = 0 
        self.transduced = False 
        self.kdtree = None


    def fit(self, X, y):
        """
        Fit a semi-supervised label propagation model based on both labelled and unlabelled data. 
        All input is provided in the X matrix, and the label for each point is provided in the y array. 
        The label -1 indicates that the point in X associated with that label in y is unlabelled. 
        """
        self.X = X
        self.y = y
        self.label_set = set(y)
        self.classes_ = list(self.label_set)
        self._transduce()

    def _transduce(self):
        max_heap = SuperHeap(len(self.y))  
        knn_list, rnn_list,self.kdtree = knn_and_rnn(self.X, self.n_neighbors)
        unlabelled_points = []
        
        for index, label in enumerate(self.y):
            label_distribution = self.calculate_instance_label_probability_distribution(knn_list[index])
            node = kNN_LDP_Node(label_distribution=label_distribution, knn=knn_list[index], rnn=rnn_list[index],index=index)
            self.data_list.append(node)

            if label == -1:
                heap_node = {'key': self.probability_certainty(label_distribution), 'node': node}
                max_heap.insert(heap_node)
                unlabelled_points.append(index)

        counter = 1

        while max_heap.size > 0:
        
            x = max_heap.extractMax()  # The label distribution should already be updated by update
            rnns = x['node'].rnn
            # Update the rnn's label certainty with this new label information and call max_heapify on these
            for rnn_index in rnns:
                self.data_list[rnn_index].label_distribution = self.calculate_instance_label_probability_using_label_distributions(knn_list[rnn_index])  # This won't work here anyway cause we need to calculate it using the label distribution
                
                if self.data_list[rnn_index].heap_index != -1 and self.data_list[rnn_index].heap_index != -2:  # If the point is inserted (and still in the heap), we update it.
                    max_heap.maxHeapify(self.data_list[rnn_index].heap_index)
            counter += 1 
        self.n_iter += 1  
        self.set_transduction()
        self.transduced = True 

    def calculate_instance_label_probability_distribution(self, indices):
        labels = [self.y[index] for index in indices]
        label_frequencies = Counter(labels)
        label_distribution = {key: value / self.n_neighbors for key, value in label_frequencies.items()}
        return label_distribution

    def calculate_instance_label_probability_using_label_distributions(self, nearest_neighbors):
        label_distribution = {key: sum([self.data_list[index].label_distribution[key] if key in self.data_list[index].label_distribution else 0 for index in nearest_neighbors]) / len(nearest_neighbors) for key in self.label_set}  # Uff probably to complex
        return label_distribution

    def probability_certainty(self, label_distribution):
        """
        Is an interpretation of probability density with respect to kNN without using the volume, so not directly a density.
        """
        return sum([value for key, value in label_distribution.items() if key != -1])

    def set_transduction(self):
        for index in range(len(self.y)):
            if self.y[index] == -1:
                decision_dict = self.data_list[index].label_distribution
                v = list(decision_dict.values())
                k = list(decision_dict.keys())
                maximal_value = k[v.index(max(v))]
                if maximal_value == -1 :
                    if isclose(v.index(max(v)),1,abs_tol=10e-9):
                        self.transduction_.append(-1)  # Abstain from making a decision
                    else :  # In the case we are far out in the propagation, and it is most probable, that the point is unlabelled
                        decision_dict
                        decision_dict.pop(-1)
                        v = list(decision_dict.values())
                        k = list(decision_dict.keys())
                        self.transduction_.append(k[v.index(max(v))])
                else:
                    self.transduction_.append(maximal_value)
                    # return the key with the maximal element. #If it is most likely, that the point is unlabelled, the point will remain unlabelled.
            else:
                self.transduction_.append(self.y[index])

    def _maximum_likelihood_prediction(self,decision_dict):
        v = list(decision_dict.values())
        k = list(decision_dict.keys())
        
        maximal_value = k[v.index(max(v))]
        if maximal_value == -1 :
            if isclose(v.index(max(v)),1,abs_tol=10e-9):
                return -1 
            else :  # In the case we are far out in the propagation, and it is most probable, that the point is unlabelled
                decision_dict
                decision_dict.pop(-1)
                v = list(decision_dict.values())
                k = list(decision_dict.keys())
                return k[v.index(max(v))]
        else:
            return maximal_value
        

    def get_params(self):
        return {'n_neighbors' : self.n_neighbors, 'n_iter' : self.n_iter}

    
    def predict(self,X):
        assert self.transduced == True, "No basis for prediction, fit data to model"
        decision_dicts = self.predict_proba(X)
        predictions = [self._maximum_likelihood_prediction(decision_dict) for decision_dict in decision_dicts]
        return predictions


    def predict_proba(self,X):
        assert self.transduced == True, "No basis for prediction, fit data to model"
        neighbors_list = [self.kdtree.query(query_point,self.n_neighbors + 1)[1] for query_point in X]
        probabilities = [self.calculate_instance_label_probability_using_label_distributions(neighbors) for neighbors in neighbors_list]
        return probabilities

        
    def score(self,X,y,sample_weigth = None):
        assert self.transduced, "The model has not yet been build, please fit before inductive predictions"
        return accuracy_score(y,self.predict(X),sample_weight=sample_weigth)

    def set_params(self, **params):
        """
        This is the regular set params function used in Scikit-Learn
        """
        if not params:
            # Simple optimization to gain speed (inspect is slow)
            return self
        valid_params = self.get_params()

        nested_params = defaultdict(dict)
        for key, value in params.items():
            key, delim, sub_key = key.partition('__')
            if key not in valid_params:
                raise ValueError('Invalid parameter %s for estimator %s. '
                                 'Check the list of available parameters '
                                 'with `estimator.get_params().keys()`.' %
                                 (key, self))

            if delim:
                nested_params[key][sub_key] = value
            else:
                setattr(self, key, value)
                valid_params[key] = value

        for key, sub_params in nested_params.items():
            valid_params[key].set_params(**sub_params)

        return self

   