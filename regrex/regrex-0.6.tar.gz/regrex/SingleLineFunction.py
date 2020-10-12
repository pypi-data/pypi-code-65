def SLF(args, onrun):
    function = eval("lambda {}: {}".format(args, onrun))
    return function