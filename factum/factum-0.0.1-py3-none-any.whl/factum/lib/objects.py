class DataFact():
    '''
    basically a static function that has no inputs and no caching, it returns data.
    it might have code to first get that data from a database in it, but it
    does not have inputs passed to it.

    features:
        - no inputs (does not rely on other nodes)
        - no caching (runs it's computations everytime it's called)
    '''

    def __init__(
        self,
        transform: callable = None,
        name: str = None,
        **kwargs
    ):
        '''
        helpful kwargs may be:
            kind: str (for example: 'data', 'view', 'task', 'transform', etc.)
            meta: dict (a good place to store meta data)
        '''
        self.set_transform(transform)
        self.set_name(name)
        self.latest = None
        self.outsig = None
        self.__dict__.update({
            k: v for k, v in kwargs.items()
            if k not in dir(Fact)})

    @staticmethod
    def sha256(data):
        import hashlib
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def clear(self):
        self.latest = None
        self.outsig = None

    def set_name(self, name: str):

        def generate_random_name(length: int = 12):
            import random
            import string
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(length))

        self.name = name or (
            self.transform.__name__
            if self.transform.__name__ != 'transform'
            else (
                self.__repr__().split()[0].split('.')[-1]
                if self.__repr__().split()[0].split('.')[-1] not in ['Fact', 'DataFact', 'MindlessFact', 'Fact']
                else generate_random_name(12)))

    def set_transform(self, function: callable = None):
        if function is None:
            return
        if function.__code__.co_varnames[0] == 'self':
            self.transform = function.__get__(self)
        else:
            self.transform = function

    def add_method(self, function: callable):
        '''
        a way to add other methods to the instance for transform to call into...
        ideally they would start with _ and would not rely on self.
        merely for code management.
        '''
        if function.__code__.co_varnames[0] == 'self':
            exec(f'self.{function.__name__} = function.__get__(self)')
        else:
            exec(f'self.{function.__name__} = function')

    def run(self, *args, **kwargs):
        return self.function()

    def function(self):
        import collections
        output = self.transform()
        if isinstance(output, collections.Hashable):
            this_hash = DataFact.sha256(output)
            if this_hash != self.outsig:
                self.outsig == this_hash
                self.set_latest()
        else:
            self.set_latest()
        return output

    def set_latest(self):
        import datetime as dt
        self.latest = dt.datetime.utcnow().timestamp()

    def transform(self):
        ''' main '''
        return self.name

    def visualization(self):
        ''' merely return the data itself '''
        return self.transform()


class MindlessFact(DataFact):
    '''
    basically a function that is responsible for
    getting its own inputs, has no caching functionality.

    features:
        - has inputs (relies on other nodes for data)
        - no caching (must call inputs)
        - no caching (must computations)
    '''

    def __init__(
        self,
        transform: callable = None,
        inputs: dict = None,
        name: str = None,
        **kwargs
    ):
        '''
        helpful kwargs may be:
            kind: str (for example: 'data', 'view', 'task', 'transform', etc.)
            meta: dict (a good place to store meta data)
        '''
        self.set_inputs(inputs=inputs or {})
        super(MindlessFact, self).__init__(transform, name, **kwargs)

    def set_inputs(self, inputs: dict):
        self.inputs = inputs

    def run(self, *args, **kwargs):
        '''
        might use gas in kwargs. we always aquire because we have no cache
        we garbage collect the inputs by calling the function directly.
        '''
        if len(args) >= 1:
            args[0] -= 1
        if 'gas' in kwargs.keys() and kwargs.get('gas', 0) > 0:
            kwargs['gas'] -= 1
        return self.function(*args, **kwargs)

    def function(self, *args, **kwargs):
        import collections
        output = self.transform(**{
            name: function_object.run(*args, **kwargs)
            for name, function_object in self.inputs.items()})
        if isinstance(output, collections.Hashable):
            this_hash = MindlessFact.sha256(output)
            if this_hash != self.outsig:
                self.outsig == this_hash
                self.set_latest()
        else:
            self.set_latest()
        return output

    def transform(self, **kw):
        ''' main '''
        return self.name

    def visualize(self, size=(8,5)):
        '''
        minimal
        indications:
            color: root node, parent nodes, ancestor nodes
            size: cached
            (color shape and size should be attribute of object, not derived here that way
            you could ask a base type node to graph and it will ask ancestors for these details,
            you could have a coordinating node which holds the mapping that they will return to you...)
            shape: <not implemented, could be kind>
        missing:
            easthetics: uniformly layout
            functionality: save to file
            indicators: namespacing, kind, time cost, popularity, etc...
        '''

        def graph_heritage(current, seen):
            seen.append(current)
            parents = [v for v in current.inputs.values()]
            for parent in parents:
                if not graph.has_node(parent.name):
                    graph.add_node(parent.name)
                    sizes.append(1200 if parent.latest else 600)
                    colors.append(
                        '#d7a9e3'
                        if parent in [v for v in self.inputs.values()]
                        else '#8bbee8')
                ancestors.append((parent.name, current.name))
                if parent not in seen:
                    graph_heritage(current=parent, seen=seen)

        import networkx as nx
        import matplotlib.pyplot as plt
        graph = nx.DiGraph()
        colors = []
        sizes = []
        ancestors = []
        if not graph.has_node(self.name):
            graph.add_node(self.name)
            sizes.append(1200 if self.latest else 600)
            colors.append('#a8d5ba')
        graph_heritage(current=self, seen=[])
        graph.add_edges_from(ancestors, weight=1)
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_color=colors, node_size=sizes)

        # gives all nodes a border
        #ax= plt.gca()
        ##print(ax.collections[0])
        ##return ax.collections
        #ax.collections[0].set_edgecolor("#000000")
        #plt.axis('off')

        plt.rcParams["figure.figsize"] = size
        plt.show()


class Fact(MindlessFact):
    '''
    basically a function that is responsible for
    getting its own inputs and remembering its own outputs

    features:
        - has inputs (relies on other nodes for data)
        - has cached output
        - has timestamp of last time it ran
    '''

    def __init__(
        self,
        transform: callable = None,
        inputs: dict = None,
        name: str = None,
        **kwargs
    ):
        '''
        helpful kwargs may be:
            prefer_cache: bool (referenced in self.run)
            kind: str (for example: 'data', 'view', 'task', 'transform', etc.)
            meta: dict (a good place to store meta data)
        '''
        self.clear(memory=True)
        super(Fact, self).__init__(transform, inputs, name, **kwargs)


    def set_inputs(self, inputs: dict):
        self.inputs = inputs
        self.ranutc = {name: None for name in self.inputs.keys()}

    def clear(self, memory: bool = False):
        self.latest = None
        if memory:
            self.output = None

    def run(
        self,
        gas: int = 0,
        condition: str = None,
        force: bool = False,
        **kwargs
    ):
        '''
        if I have no timestamp - gather all inputs and run.

        condition

        gas = 0
            if do not I have a timestamp, indicating I have not cached data update my input for that thing and run.
            return cache
        gas >= 1
            if any of my inputs have a later run date than me, update my input for that thing and run.
            return cache

        gas can specify if we should pull from cache or not in this way:
        -1 - infinite gas (DAGs only!)
        0 - if cache: cache, else: get inputs, do function, save as cache
        1 - request cached inputs and run functionality (default)
        2 - request non-cached inputs and run functionality
        3 - request that inputs request non-cached inputs and recalculate...
        4+ - so on and so forth...

        condition is an override on gas and allows one to specify function
        execution according to the condition itself. for instance one may want
        the function to execute if the object provides up-to-date source data.
        this could be accomplished by providing the following keyword argument:
            `condition="self.kind == 'data'"`

        force means you want the function to run if it has gas to do so.
        '''
        if self.gather(gas) is None:
            gas = gas if gas <= 0 else gas -1
            self.function(**{
                name: amigo.run(gas=gas, condition=condition, force=force, **kwargs)
                for name, amigo in self.inputs.items()})
        elif condition is not None:
            try:
                evaluated = eval(condition)
            except Exception as e:
                evaluated = False
            if evaluated:
                gas = gas if gas <= 0 else gas -1
                self.function(**{
                    name: amigo.run(gas=gas, condition=condition, force=force, **kwargs)
                    for name, amigo in self.inputs.items()})
        elif gas == -1:
            self.function(**{
                name: amigo.run(gas=gas, condition=condition, force=force, **kwargs)
                for name, amigo in self.inputs.items()})
        elif gas > 0 and force:
            gas = gas if gas <= 0 else gas -1
            self.function(**{
                name: amigo.run(gas=gas, condition=condition, force=force, **kwargs)
                for name, amigo in self.inputs.items()})
        return self.get()

    def gather(self, gas: int = 0):
        ''' gets the latest timestamp out of everything '''
        if gas != 0 and self.latest is not None:
            gas = gas if gas <= 0 else gas -1
            for name, amigo in self.inputs.items():
                if hasattr(amigo, 'gather'):
                    value = amigo.gather(gas)
                else:
                    value = amigo.latest
                if value is None or value > self.latest:
                    return None
        return self.latest

    def get(self):
        return self.output

    def function(self, **kwargs):
        temp = self.output
        self.output = self.transform(**kwargs)
        if temp != self.output:
            self.set_latest()

    def transform(self, **kw):
        ''' main '''
        return self.output
