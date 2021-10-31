import sys


class SuperHeap :
    """
    The best heap ever created. Insert a list of dictionaries, where each node is a entry in dictionary in the list.
    The heap will be sorted by the 'key' entry in the dictionary.   

    Code stolen and modified from https://www.geeksforgeeks.org/max-heap-in-python/
   """
    def __init__(self, maxsize): 
        """
        Initialize a Superheap object 

        Keyword arguments : 

        maxsize -- The maximal size the heap can take.

        Notes: 
        * Initialized elements will get the heap-index -1 until inserted in the heap.
        * Extracted elements will obtain the heap index -2 
        """
        self.maxsize = maxsize 
        self.size = 0  
        self.Heap = [{'key':0,'node' : None} for _ in range(self.maxsize)]
        self.index_dict = {}
  
    def root(self):
        return self.Heap[0] 


    def parent(self, pos): 
        """Function to return the position of parent for the node currently  at 

        Keyword arguments : 
       
        pos - integer position 
        """ 
        return (pos-1)//2
  
    def leftChild(self, pos): 
        """
        Function to return the position of the left child for the node currently at pos 
        """
        return 2 * pos + 1
  
    def rightChild(self, pos): 
        """
        Function to return the position of the right child for the node currently at pos 
        """
        return (2 * pos) + 2
  
    def isLeaf(self, pos): 
        """
        Function that returns true if the passed
        node is a leaf node 
        """ 
        if pos >= (self.size//2) and pos <= self.size: 
            return True
        return False
  
    def swap(self, fpos, spos): 
        """
        Function to swap two nodes of the heap
        """
        self.Heap[fpos]['node'].heap_index = spos
        self.Heap[spos]['node'].heap_index = fpos
        
        self.index_dict[self.Heap[fpos]['node'].index] = spos
        self.index_dict[self.Heap[spos]['node'].index] = fpos
        
        self.Heap[fpos], self.Heap[spos] = self.Heap[spos], self.Heap[fpos]

    def increaseKey(self, pos, key): 
        assert key > self.Heap[pos]['key'], "New key must be larger than current key"
        self.Heap[pos]['key'] = key
        while pos > 0 and self.Heap[self.parent(pos)]['key'] < self.Heap[pos]['key']: 
            self.swap(pos,self.parent(pos))
            pos = self.parent(pos)
        


    def maxHeapify(self, pos): 
        """
        Function to heapify the node at pos.
        """
        
        if not self.isLeaf(pos): 
            if (self.Heap[pos]['key'] < self.Heap[self.leftChild(pos)]['key'] or self.Heap[pos]['key'] < self.Heap[self.rightChild(pos)]['key']):
  
                # Swap with the left child and heapify 
                # the left child 
                if self.Heap[self.leftChild(pos)]['key'] > self.Heap[self.rightChild(pos)]['key']: 
                    self.swap(pos, self.leftChild(pos)) 
                    self.maxHeapify(self.leftChild(pos)) 
  
                # Swap with the right child and heapify 
                # the right child 
                else: 
                    self.swap(pos, self.rightChild(pos)) 
                    self.maxHeapify(self.rightChild(pos)) 
  
    def insert(self, element): 
        """
        Function to insert a node into the heap
        """
        if self.size >= self.maxsize : 
            print(f"size: {self.size} >= max: {self.maxsize}")
            raise Exception(IndexError)
        self.Heap[self.size] = element
        current = self.size
        element['node'].heap_index = current
        self.size += 1
        self.index_dict[element['node'].index] = current

        while self.Heap[current]['key'] > self.Heap[self.parent(current)]['key']:
            if current == 0 :  # Cause the root has no parent!
                break  
            self.swap(current, self.parent(current)) 
            current = self.parent(current)

    def print(self, print_all=False):
        """
        Function to print the contents of the heap 
        """
        if print_all : 
            for i in range(self.size//2):
                if 2 * i + 2 < self.size : 
                    output_string =  f"PARENT : {self.Heap[i]} LEFT CHILD : {self.Heap[2 * i + 1]} RIGHT CHILD : {self.Heap[2 * i + 2]}\n" 
                else : 
                    output_string =  f"PARENT : {self.Heap[i]}  LEFT CHILD : {self.Heap[2 * i + 1]} No Right Child\n"       
                print(output_string)
        else : 
            print(self.__repr__())
    
    
    
    
    def __repr__(self): 
        output_string = ""
        for i in range(self.size//2): 
            if 2 * i + 2 < self.size : 
                output_string +=  f"PARENT : {self.Heap[i]['key']}  LEFT CHILD : {self.Heap[2 * i + 1]['key']} RIGHT CHILD : {self.Heap[2 * i + 2]['key']}\n" 
            else : 
                output_string +=  f"PARENT : {self.Heap[i]['key']}  LEFT CHILD : {self.Heap[2 * i + 1]['key']} No Right Child\n"       
        output_string += "----------------------------" 
        return output_string 

    def __str__(self): 
        return self.__repr__()
 

    # Function to remove and return the maximum 
    # element from the heap 
    def extractMax(self): 
        popped = self.Heap[0]
        self.Heap[0]['node'].heap_index = -2  # Update the index to the outside
        self.index_dict[self.Heap[0]['node'].index] = -2
        # print(f"putting element at position {self.size} to the front")
        self.Heap[0] = self.Heap[self.size-1] # -1 because we are zero indexed!
        self.index_dict[self.Heap[self.size-1]['node'].index] = 0
        
        self.size -= 1
        self.maxHeapify(0)
        return popped 

    def check_for_duplicates(self): 
        for i in range(1,self.size): 
            for j in range(i+1,self.size): 
                if self.Heap[i] == self.Heap[j]: 
                    print(self.Heap[i])
                    return True
        return False 

    def check_heap_index_correctness(self): 
        for i in range(self.size): 
            if self.Heap[i]['node'].heap_index != i : 
                print(f"ERROR : index {i} has heap index {self.Heap[i]['node'].heap_index}")
                return False
        return True 
    
    def print_all_objects(self,only_heap_index=False):
        if only_heap_index : 
            return [self.Heap[i]['node'].heap_index for i in range(self.size)]
        else :  
            for i in range(self.size):
                print(f"index:{i}, key:{self.Heap[i]['key']}, {self.Heap[i]['node']}")
        print("\n")
            