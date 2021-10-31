from collections import Counter,defaultdict
from utils.super_heap import SuperHeap
from utils.neighborhoods import knn_and_rnn
from sklearn.metrics import accuracy_score
from utils.helper_functions import key_with_max_val

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
        self.label_set = None
        self.X_ = None  # input array
        self.classes_ = None  # The distinct labels used in classifying instances
        self.label_distributions_ = None  # Categorical distribution for each item
        self.transduction_ = []  # n_d array with labels assigned to each item during transduction
        self.n_iter = 0 
        self.transduced = False 
        self.kdtree = None
        self.max_heap = None  


    def fit(self, X, y):
        """
        Fit a semi-supervised label propagation model based on both labelled and unlabelled data. 
        All input is provided in the X matrix, and the label for each point is provided in the y array. 
        The label -1 indicates that the point in X associated with that label in y is unlabelled. 
        """
        self.X = X
        self.y = y
        self.label_set = set(y)
        self.max_heap = SuperHeap(len(y)) 
        self.classes_ = list(self.label_set)
        self.label_distributions_ = [{label:1} for label in y]
        self._transduce()

    def _transduce(self):
        knn_list, rnn_list,self.kdtree = knn_and_rnn(self.X, self.n_neighbors)
        U_indices = [index for index, label in enumerate(self.y) if label == -1]
        
        for index in U_indices: 
            label_distribution = self.calculate_instance_label_probability_distribution(knn_list[index])
            node = kNN_LDP_Node(label_distribution=label_distribution, knn=knn_list[index], rnn=rnn_list[index],index=index)
            heap_node = {'key': self.probability_certainty(label_distribution), 'node': node}
            self.max_heap.insert(heap_node)


        
        while self.max_heap.size > 0:
            x = self.max_heap.extractMax() 
            if x['key'] > 0: 
                self.label_distributions_[x['node'].index] = self.calculate_instance_label_probability_distribution(knn_list[x['node'].index])
                for r_neighbor in x['node'].rnn: 
                    if self.y[r_neighbor] == -1 and self.max_heap.index_dict[r_neighbor] != -2: # Meaning if the point has not yet been labelled
                        probability = self.calculate_instance_label_probability_distribution(knn_list[r_neighbor])
                        new_key = self.probability_certainty(probability)
                        self.max_heap.increaseKey(self.max_heap.index_dict[r_neighbor],new_key)
        self.set_transduction()
        self.transduced = True

    def  calculate_instance_label_probability_distribution(self, nearest_neighbors):
        label_distribution = {} 
        for key in self.label_set: 
            label_distribution[key] = sum([self.label_distributions_[index][key] if key in self.label_distributions_[index] else 0 for index in nearest_neighbors])/len(nearest_neighbors)

        return label_distribution

    def probability_certainty(self, label_distribution):
        """
        Is an interpretation of probability density with respect to kNN without using the volume, so not directly a density.
        """
        return sum([value for key, value in label_distribution.items() if key != -1])

    def set_transduction(self):
        for index in range(len(self.y)):
            if self.y[index] == -1:
                decision_dict = self.label_distributions_[index]
                self.transduction_.append(self._maximum_likelihood_prediction(decision_dict))
            else:
                self.transduction_.append(self.y[index])

    def _maximum_likelihood_prediction(self,decision_dict):
        l = {k:v for k,v in decision_dict.items() if k != -1}
        if l == {}: 
            return -1  # Abstain from making a decision
        label = key_with_max_val(l)                 
        if label != -1 and l[label] > 0.0: 
            return label
        else :  
            return -1
        

    def get_params(self):
        return {'n_neighbors' : self.n_neighbors, 'n_iter' : self.n_iter}

    
    def predict(self,X):
        assert self.transduced, "No basis for prediction, fit data to model"
        decision_dicts = self.predict_proba(X)
        predictions = [self._maximum_likelihood_prediction(decision_dict) for decision_dict in decision_dicts]
        return predictions


    def predict_proba(self,X):
        assert self.transduced, "No basis for prediction, fit data to model"
        neighbors_list = [self.kdtree.query(query_point,self.n_neighbors + 1)[1] for query_point in X]
        probabilities = [self.calculate_instance_label_probability_distribution(neighbors) for neighbors in neighbors_list]
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

 