import unittest

from enum import Enum

from gmrs.model.context import Context
from gmrs.model.task import LeafTask
from gmrs.model.robot import Robot
from gmrs.model.factory import capability, property
from gmrs.model.world_map import create_map

from gmrs.skill.skill_base import SkillPlannerBase
from gmrs.planner.evaluation import Evaluation
from gmrs.util.physics import estimate_dt

from gmrs.planner.outcome import Outcome, Result as r

from .move_capability import MoveCapability


class VisitWithMoveBase(SkillPlannerBase):

    provides = 'Visit [destination]'

    pre_conditions = {
        'has_capabilities': [MoveCapability]
    }

    parameters = {
        'destination': 'location',
    }

    origin, detination, world_map, paths_generator = None


    def __init__(self, logger, robot, task_parameters, world_model, context):
        super().__init__()
        # safe init
        self.name = self.format_name(provides)
        self.logger = logger
        # check achievability, raise error if something wrong
        #self.init(robot, task_parameters, world_model, context)


    def bind(self, robot, task_parameters, world_model, 
             context, task_code=None):
        ''' 
        bind from robot (state, capabilities), task parameters, world map 
        '''
        origin = self._get_required('location', context,
                                    default=robot.initial_location)
        detination = self._get_required('destination', task_parameters)
        paths_generator = self.world_model.map.get_paths(origin, detination)

        # TODO pass an heuristic function
        world_map = self._get_required('map', self.world_model)

        # robot capabilities
        move = get_capability(robot, MoveCapability)

        # configuration options
        self.add_config('paths', paths_generator)  # TODO should name a path?
        self.add_config('move_configs', move.configs)

    def get_post_condition(self):
        # post condition
        post_conditions = {
            'location': detination
        }
        return post_conditions
    
    def init_configurations(self, paths, move_configurations):
        pass

    def config_iterator():
        # objectives = self.objectives
        # TODO sort configurations
    
        return itertools.product(a, b)
        yield config

    def get_heuristic(self):
        return 0

    def expand(self):
        for config in self.config_iterator(self.configurations):
            yield self.eval(*config)

    def get_capability(self, robot, capability):
        pass

    # function on the injected dependencies
    def eval_config(self, max_speed_options):
        self.current_location = current_location
        self.place
        map
        # base calculation
        for (speed, config) in max_speed_options:
            time = estimate_dt(
                distance=map.getDistance(current_location, place),
                speed=speed)
            
            yield Evaluation({'speed': 'slow'},
                       [Outcome(res=r.SUCC, t=time)])
        

        battery = map.getDistance(current_location, place) * 
        # possible outcomes - probabily p should also be a function of time
        # staticaly assume that every robot is capable of 
        # 3 speeds to improve the readability
        return {
           

            Evaluation({'speed': 'medium'},
                       [Outcome(res=SUCC, t=time)]),

            Evaluation({'speed': 'fast'},
                       [Outcome(res=SUCC, t=time)]),

            'speed=["slow"]': [
                    {'p': 0.99, status: SUCC, time: time},
                    {'p': 0.01, status: ERR, time: time}
            ],
            'speed=["medium"]': [
                {'p': 0.99, status: SUCC, time: time},
                {'p': 0.01, status: ERR, time: time}
            ],
            'speed=["fast"]': [
                {'p': 0.99, status: SUCC, time: time},
                {'p': 0.01, status: ERR, time: time}
            ],
            }
        return (vars, eval)

    def task_end(self):
        pass

    def _get_required(self, name, container, default):
        value = container[name] if container[name] is not None else default
        if value is None:
            fail_code = f'get-required-{name}'
            self.logger(fail_code)
            raise Exception(fail_code)


required_capabilities = ['self_localization', 'move']

skill_visit = Skill('Visit [place]',
                    assumme=[required_capabilities],
                    guarantee=['location:[place]'],
                    nodes=['visit_skill']
                    fnc=visit_fnc())


# task decomposition model with a single task
task_decomposition = LeafTask('Visit [place]')
#MPCTL objective
#constraints = 

# Runtime ####
request = 'Visit'
