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
        self.module = None
        self.set_transform(transform)
        self.set_name(name)
        self.latest = None
        self.outsig = None
        self.caller = None
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
        self.caller = None

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

    def nested_name(self):
        ''' nested import name '''
        if self.module is None:
            return self.name
        return f'{self.module}.{self.name}'

    def tree_name(self):
        ''' dag name '''
        if self.caller is None:
            return self.name
        return f'{self.caller}.{self.name}'

    def set_transform(self, function: callable = None):
        if function is None:
            return
        if (len(function.__code__.co_varnames) > 0 and
            function.__code__.co_varnames[0] == 'self'):
            self.transform = function.__get__(self)
        else:
            self.transform = function
        self.module = function.__module__

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
        ''' we need to do better at defining the protocol for this... '''
        if 'caller' in kwargs:
            self.caller = kwargs['caller']
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

    def __gt__(self, fact: DataFact):
        ''' adds it as an arg '''
        fact.add_input(fact=self)

    def __rshift__(self, fact: DataFact):
        ''' adds it as a kwarg '''
        fact.add_input(fact=self, name=self.name)

    def add_input(self, fact, name: str = None):
        ''' fact should be DataFact or callable '''
        if name:
            self.kwargs[name] = fact
        else:
            if self.args is None:
                self.args = []
            self.args.append(fact)

    def apply_context(self, fact: DataFact, name: str = 'context'):
        ''' adds it as a kwarg to the entire dag '''
        for input_fact in self.input_facts():
            if input_fact.name != name:
                input_fact.apply_context(fact, name)
        self.add_input(fact=fact, name=name)

    def set_inputs(self, inputs: dict):
        self.inputs = inputs
        self.match_inputs()

    def match_inputs(self):
        ''' figure out if we were handed args, kwargs, or args and kwargs '''
        self.args = None
        self.kwargs = None
        if isinstance(self.inputs, tuple):
            if (
                len(self.inputs) == 2 and
                isinstance(self.inputs[0], list) and
                isinstance(self.inputs[1], dict)
            ):
                self.args = self.inputs[0]
                self.kwargs = self.inputs[1]
            else:
                self.args = self.inputs
        elif isinstance(self.inputs, list):
            self.args = self.inputs
        else:
            self.kwargs = self.inputs
        if self.kwargs is None:
            self.kwargs = {}

    def run(self, *args, **kwargs):
        '''
        might use gas in kwargs. we always acquire because we have no cache
        we garbage collect the inputs by calling the function directly.
        '''
        if 'caller' in kwargs:
            self.caller = kwargs['caller']
            kwargs['caller'] = f"{kwargs['caller']}.{self.name}"
        else:
            kwargs['caller'] = self.name
        if len(args) >= 1:
            args[0] -= 1
        if 'gas' in kwargs.keys() and kwargs.get('gas', 0) > 0:
            kwargs['gas'] -= 1
        return self.function(*args, **kwargs)

    def function(self, *args, **kwargs):
        import collections
        input_args = self.acquire_args(*args, **kwargs)
        input_kwargs = self.acquire_kwargs(*args, **kwargs)
        if input_args is None:
            output = self.transform(**input_kwargs)
        else:
            output = self.transform(*input_args, **input_kwargs)
        if isinstance(output, collections.Hashable):
            this_hash = MindlessFact.sha256(output)
            if this_hash != self.outsig:
                self.outsig == this_hash
                self.set_latest()
        else:
            self.set_latest()
        return output

    def acquire_args(self, *args, **kwargs):
        '''
        acquire the ouputs all named inputs
        inputs can Fact objects or callable
        assumes this pattern denotes args and kwargs: ([], {})
        '''
        if self.args:
            return [(
                    function_object.run(*args, **kwargs)
                    if isinstance(function_object, DataFact)
                    else function_object())
                for function_object in self.args]

    def acquire_kwargs(self, *args, **kwargs):
        return {
            name: (
                function_object.run(*args, **kwargs)
                if isinstance(function_object, DataFact)
                else function_object())
            for name, function_object in self.kwargs.items()}

    def input_facts(self, fact: DataFact = None):
        fact = fact or self
        return (
            [a for a in fact.args if isinstance(a, DataFact)] +
            [v for v in fact.kwargs.values() if isinstance(v, DataFact)]
            if fact.args is not None
            else [v for v in fact.kwargs.values() if isinstance(v, DataFact)])

    def input_callables(self, fact: DataFact = None):
        fact = fact or self
        return (
            [a for a in fact.args if not isinstance(a, DataFact)] +
            [v for v in fact.kwargs.values() if not isinstance(v, DataFact)]
            if fact.args is not None
            else [v for v in fact.kwargs.values() if not isinstance(v, DataFact)])

    def transform(self, *args, **kwargs):
        ''' main '''
        return self.name

    def visualize(self, size: tuple = (8,5), name_kind: str = 'name', quick: bool = False):
        '''
        size - tuple of 2 integers
        name_kind = 'name' or 'tree_name' or 'nested_name'
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
            parents = self.input_facts(current) + self.input_callables(current)
            for parent in parents:
                parent_name = eval(f'parent.{name_kind}{"" if name_kind == "name" else "()"}')
                if not graph.has_node(parent_name):
                    graph.add_node(parent_name)
                    sizes.append(1200 if parent.latest else 600)
                    colors.append('#d7a9e3' if parent in self.input_facts() + self.input_callables() else '#8bbee8')
                current_name = eval(f'current.{name_kind}{"" if name_kind == "name" else "()"}')
                ancestors.append((parent_name, current_name))
                if parent not in seen:
                    graph_heritage(current=parent, seen=seen)

        import networkx as nx
        import matplotlib.pyplot as plt
        graph = nx.DiGraph()
        colors = []
        sizes = []
        ancestors = []
        self_name = eval(f'self.{name_kind}{"" if name_kind == "name" else "()"}')
        if not graph.has_node(self_name):
            graph.add_node(self_name)
            sizes.append(1200 if self.latest else 600)
            colors.append('#a8d5ba')
        graph_heritage(current=self, seen=[])
        graph.add_edges_from(ancestors, weight=1)
        pos = nx.spring_layout(graph, **({} if quick else {'iterations':100}))
        nx.draw(graph, pos, with_labels=True, node_color=colors, node_size=sizes)
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

    def clear(self, memory: bool = False):
        self.latest = None
        self.caller = None
        if memory:
            self.output = None

    def to_dag(self):
        '''
        exports all ancestors. loop through all inputs, ask for the map of their inputs
        since names must be unique, use the object names as keys wherever possible.
        example:
        a and b feed to c then c to d. d.to_dag() ->
        {
            d.nested_name: (d.run, [c.nested_name]),
            c.nested_name: (c.run, [a.nested_name, b.nested_name]),
            b.nested_name: (b.run, []),
            a.nested_name: (a.run, []),
        }
        d.name in the above dictionary might need to be the name of everything that came
        before it too, in order to guarantee uniqueness. doesn't handle non Facts yet.
        '''
        mine = self.input_facts()
        me = {self.nested_name(): (self.run, [m.nested_name() for m in mine])}
        if mine == []:
            return me
        below = {}
        for entity in mine:
            below = {**below, **entity.to_dag()}
        return {**me, **below}

    def save(self, folder: str = None):
        self.to_binary(folder)

    def restore(self, folder: str = None):
        self.from_binary(folder)

    def to_binary(self, folder: str = None):
        import os
        import pickle
        folder = folder or os.getcwd()
        os.makedirs(folder, mode=0o777, exist_ok=True)
        with open(os.path.join(folder, self.name, 'output'), mode='wb') as f:
            pickle.dump(self.output, f)
        with open(os.path.join(folder, self.name, 'inputs'), mode='wb') as f:
            pickle.dump(self.inputs, f)
        with open(os.path.join(folder, self.name, 'latest'), mode='wb') as f:
            pickle.dump(self.latest, f)

    def from_binary(self, folder: str = None):
        import os
        import pickle
        folder = folder or os.getcwd()
        os.makedirs(folder, mode=0o777, exist_ok=True)
        with open(os.path.join(folder, self.name, 'output'), mode='rb') as f:
            self.output = pickle.load(f)
        with open(os.path.join(folder, self.name, 'inputs'), mode='rb') as f:
            self.inputs = pickle.load(f)
        with open(os.path.join(folder, self.name, 'latest'), mode='rb') as f:
            self.latest = pickle.load(f)

    def run(
        self,
        gas: int = 0,
        condition: str = None,
        force: bool = False,
        **kwargs
    ):
        '''
        `run()` tells asks the Fact to return cache if the cache is available
        and up-to-date, or, if it isn't, gather the required inputs and execute
        the function defined as 'transform'.

        `gas` can specify how far back in the network we should look to verify
        that our cache is up-to-date. valid values range from -1 and up:
        -1 - infinite gas (DAGs only!) forces execution of all ancestors and self
        0 - if cache: cache, else: get inputs, do function, save as cache
        1 - request cached inputs and run functionality
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
        if 'caller' in kwargs:
            self.caller = kwargs['caller']
            kwargs['caller'] = f"{kwargs['caller']}.{self.name}"
        else:
            kwargs['caller'] = self.name

        kwargs['condition'] = condition
        kwargs['force'] = force
        if self.gather(gas) is None:
            kwargs['gas'] = gas if gas <= 0 else gas - 1
            self.function(**kwargs)
        elif condition is not None:
            try:
                evaluated = eval(condition)
            except Exception as e:
                evaluated = False
            if evaluated:
                kwargs['gas'] = gas if gas <= 0 else gas - 1
                self.function(**kwargs)
        elif gas == -1:
            self.function(**kwargs)
        elif gas > 0 and force:
            kwargs['gas'] = gas if gas <= 0 else gas - 1
            self.function(**kwargs)
        return self.get()

    def gather(self, gas: int = 0):
        ''' gets the latest timestamp out of everything '''
        if gas != 0 and self.latest is not None:
            gas = gas if gas <= 0 else gas - 1
            inputs = (
                [a for a in self.args] + [v for v in self.kwargs.values()]
                if self.args is not None
                else [v for v in self.kwargs.values()])
            for fact in inputs:
                if isinstance(fact, DataFact):
                    if hasattr(fact, 'gather'):
                        value = fact.gather(gas)
                    else:
                        value = fact.latest
                else:
                    value = ''
                if isinstance(value, str):
                    continue
                elif value is None or value > self.latest:
                    return None
        return self.latest

    def get(self):
        return self.output

    def function(self, *args, **kwargs):
        temp = self.output
        input_args = self.acquire_args(*args, **kwargs)
        input_kwargs = self.acquire_kwargs(*args, **kwargs)
        if input_args is None:
            self.output = self.transform(**input_kwargs)
        else:
            self.output = self.transform(*input_args, **input_kwargs)
        if temp != self.output:
            self.set_latest()

    def transform(self, **kw):
        ''' main '''
        return self.output
