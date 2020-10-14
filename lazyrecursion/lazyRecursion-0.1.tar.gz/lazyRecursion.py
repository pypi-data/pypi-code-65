from collections.abc import Sequence
import json

class RecursiveSequence(Sequence):
    def __init__(self, induction_start, relative_indices, recursion_function, cache_file=''):
        """ create lazy cached recursive sequence starting at 0 and defined for all positive indices
        params:
            induction_start: Mapping with initial indices needed for recursion (must include 0)
            relative_indices: the indices [n+index for index in relative_indices]
                which are needed to plug into the recursion_function
            recursion_function: recursion_function(*[n+index for index in relative_indices]) 
                should calculate the index n
            cache_file: json file where to cache the sequence (from during construction)
                (to during destruction). Does not use file cache if not provided
        
        returns:
            a lazy list which behaves like the recursive list specified by
            the recursion_function
        
        Example:
            fibonacci = RecursiveSequence(
                induction_start={0: 1, 1:1},
                relative_indices=[-2,-1], 
                recursion_function=lambda x1,x2: x1+x2
            )
            print(fibonacci[:10])
        """
        self.rec_fun = recursion_function
        self.rel_indices = relative_indices
        self.cached = induction_start 
        self.cache_file = cache_file
        try:        
             with open(cache_file, 'r') as f:
                 self.cached.update(json.load(f))
        except FileNotFoundError:
            pass

    def __del__(self):
        try:
             with open(self.cache_file, 'w') as f:
                 json.dump(self.cached, f)
        except FileNotFoundError:
            pass

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.stop and key.stop >= 0:
                return [self[idx] for idx in range(key.stop)[key]]
            raise IndexError(key)
        if isinstance(key, int):
            if key< 0: 
                raise IndexError(key)
            try:
                return self.cached[key]
            except KeyError:
                self.cached[key] = self.rec_fun(
                    *[self[key+idx] for idx in self.rel_indices]
                )
                return self.cached[key]
        raise TypeError(key)

    def __len__(self):
        """ returns the length of the current cache """
        return len(self.cached)

if __name__ == "__main__":
    fibonacci = RecursiveSequence(
        induction_start={0: 1, 1:1},
        relative_indices=[-2,-1], 
        recursion_function=lambda x1,x2: x1+x2,
    )
    fibonacci[:10]