

class ScenarioBuilder:
    
    def __init__(self):
        pass

    def withGrid(self, x, y):
        return self
    
    def withRobot(self, name):
        return RobotBuilder(self)



class RobotBuilder:
    
    def __init__(self, parentBuilder):
        self.parentBuilder = parentBuilder
        pass
    
    def done(self):
        return self.parentBuilder

class GoalBuilder():
    def __init__(self, name):
        self.parentBuilder = parentBuilder
        self.refinementType = None
        self.refinements = []
        pass

    def done(self):
        return self.parentBuilder

    def refinedBy(refinementType, refinements):
        pass

    def withGoal(name):
        self.name = name
    
    




