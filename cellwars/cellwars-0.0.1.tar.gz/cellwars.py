'''
cellwars.py
===========
The cellwars python bot package.
'''

from enum import Enum
import sys

# Internal classes start here

class InputProcessingException(Exception):
    pass

class CommandType(Enum):
    INITIALIZE = 0
    SPAWN = 1
    DIE = 2
    SET_CELL_PROPERTIES = 3
    CONFLICTING_ACTIONS = 4
    RUN_ROUND = 5
    END_GAME = 6

class ActionType(Enum):
    ATTACK = "ATTACK"
    MOVE = "MOVE"
    EXPLODE = "EXPLODE"
    ROUND_END = "ROUND_END"
    INITIALIZED = "INITIALIZED"

class Direction(Enum):
    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST  = (1, 0)
    WEST  = (-1, 0)

class Action:
    def __init__(self, action_type, parameters):
        self.action_type = action_type
        self.parameters = parameters

    def serialize(self):
        return '{} {}'.format(self.action_type.value, ' '.join(map(str, self.parameters)))

    @classmethod
    def attack(cls, cell_id, position):
        return Action(ActionType.ATTACK, [cell_id, position.x, position.y])

    @classmethod
    def move(cls, cell_id, position):
        return Action(ActionType.MOVE, [cell_id, position.x, position.y])

    @classmethod
    def explode(cls, cell_id):
        return Action(ActionType.EXPLODE, [cell_id])

    @classmethod
    def initialized(cls):
        return Action(ActionType.INITIALIZED, [])

class Command:
    def __init__(self, command_type, parameters):
        self.command_type = command_type
        self.parameters = parameters

    def _get_callback(self, game_coordinator):
        if self.command_type == CommandType.INITIALIZE:
            return game_coordinator.initialize
        elif self.command_type == CommandType.SPAWN:
            return game_coordinator.spawn_cell
        elif self.command_type == CommandType.DIE:
            return game_coordinator.kill_cell
        elif self.command_type == CommandType.SET_CELL_PROPERTIES:
            return game_coordinator.set_cell_properties
        elif self.command_type == CommandType.CONFLICTING_ACTIONS:
            # Not handled yet
            return lambda x, y: None
        else:
            raise Exception("Unexpected command")

    def apply(self, game_coordinator):
        callback = self._get_callback(game_coordinator)
        callback(*self.parameters)

class Communicator:
    REQUIRED_ARGS = {
        CommandType.INITIALIZE: 5,
        CommandType.SPAWN: 6,
        CommandType.DIE: 1,
        CommandType.SET_CELL_PROPERTIES: 5,
        CommandType.CONFLICTING_ACTIONS: 2,
        CommandType.RUN_ROUND: 0,
        CommandType.END_GAME: 0,
    }

    def __init__(self, input_stream, output_stream):
        self._input_stream = input_stream
        self._output_stream = output_stream

    def emit_action(self, action, flush=False):
        self._output_stream.write('{}\n'.format(action.serialize()))
        if flush:
            self._output_stream.flush()

    def end_round(self):
        self.emit_action(Action(ActionType.ROUND_END, []))
        self._output_stream.flush()

    def read_command(self):
        line = self._input_stream.readline().strip()
        if not line:
            return None
        tokens = line.split(' ')
        command_type, raw_parameters = (tokens[0], tokens[1:])
        if command_type not in CommandType.__members__:
            print(repr(command_type))
            raise InputProcessingException(
                "Unknown command {}".format(command_type)
            )
        command_type = CommandType[command_type]
        expected_args = self.REQUIRED_ARGS[command_type]
        if len(raw_parameters) != expected_args:
            raise InputProcessingException(
                "Found {} parameters for command {}, expected {}".format(
                    len(raw_parameters),
                    command_type,
                    expected_args
                )
            )
        try:
            parameters = list(map(int, raw_parameters))
        except Exception as ex:
            raise InputProcessingException("Non integer parameter found")
        return Command(command_type, parameters)

class GameCoordinator:
    LOOP_DONE_COMMANDS = set([
        CommandType.RUN_ROUND,
        CommandType.END_GAME
    ])

    def __init__(self, communicator, bot):
        self.communicator = communicator
        self._bot = bot
        self._state = None

    def state(self):
        return self._state

    def initialize(self, width, height, player_team_id, my_column, enemy_column):
        self._state = WorldState(width, height, player_team_id, my_column, enemy_column)

    def spawn_cell(self, cell_id, x, y, health, team_id, age):
        is_enemy = team_id != self._state.my_team_id
        self._state.cells[cell_id] = Cell(
            self,
            cell_id,
            Position(x, y),
            health,
            team_id,
            age,
            is_enemy
        )

    def set_cell_properties(self, cell_id, x, y, health, age):
        cell = self._state.cells[cell_id]
        cell.position = Position(x, y)
        cell.health = health
        cell.age = age

    def kill_cell(self, cell_id):
        del self._state.cells[cell_id]

    def loop(self):
        self.communicator.emit_action(Action.initialized(), flush=True)
        while True:
            command = self.communicator.read_command()
            while command and command.command_type not in self.LOOP_DONE_COMMANDS:
                command.apply(self)
                command = self.communicator.read_command()
            if not command or command.command_type == CommandType.END_GAME:
                break
            self._bot.run_round(self._state)
            self.communicator.end_round()

# End of internal classes

class Position:
    '''
    Represents a position, identified by an x and y components.
    '''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def translated_by_offset(self, x_offset, y_offset):
        '''
        Constructs a new position which is translated by the given x and y offsets.

        Args:
            x_offset (int): the x offset to apply.
            y_offset (int): the y offset to apply.

        Returns:
            A new Position which is the result of translating the x and
            y coordinates of this instance by the given offsets.
        '''
        return Position(self.x + x_offset, self.y + y_offset)

    def translated_by_direction(self, direction):
        '''
        Constructs a new position which is translated by the given direction.

        Args:
            direction (Direction): the direction to translate this position to.

        Returns:
            A new Position which is the result of translating the x and
            y coordinates of this instance by the given direction.
        '''
        return self.position.translated_by_offset(*direction.value)

    def distance(self, other_position):
        '''
        Returns the manhattan distance to the provided position.

        Args:
            other_position (Position): the position to get the distance to.

        Returns:
            int. The manhattan distance to the provided position.
        '''
        return abs(other_position.x - self.x) + abs(other_position.y - self.y)

    def is_adjacent(self, other_position):
        '''
        Indicates whether this position is adjacent to the provided one.

        A position is considered to be adjacent to another one iff the
        manhattan distance to it is 1.

            Args:
                other_position (Position): the position to be checked.

            Returns:
                bool: true iff the position is adjacent to this one.
        '''
        return self.distance(other_position) == 1

    def is_surrounding(self, other_position):
        '''
        Indicates whether this position is surrounding to the provided one.

        A position is considered to be surrounding another one if they're at
        most one step away in the X axis and at most one in the Y one.

        Args:
            other_position (Position): the position to be checked.

        Returns:
            bool: true iff the position is adjacent to this one.
        '''
        return self != other_position and \
            abs(other_position.x - self.x) <= 1 and \
            abs(other_position.y - self.y) <= 1

    def __eq__(self, other_position):
        '''
        Checks positions for equality
        '''
        return (self.x, self.y) == (other_position.x, other_position.y)

    def __ne__(self, other_position):
        '''
        Checks positions for equality
        '''
        return not (self == other_position)

    def __hash__(self):
        return hash((self.x, self.y))

class Cell:
    '''
    Represents a cell that either you or your enemy control.
    '''

    def __init__(self, coordinator, cell_id, position, health, team_id, age, is_enemy):
        self._coordinator = coordinator
        self.cell_id = cell_id
        self.position = position
        self.health = health
        self.team_id = team_id
        self.age = age
        self.is_enemy = is_enemy

    def _is_in_bounds(self, position):
        return position.x >= 0 and position.x < self._coordinator.state().width and \
            position.y >= 0 and position.y < self._coordinator.state().height

    def _is_valid_position(self, position):
        return self._is_in_bounds(position) and self.position.is_adjacent(position)

    def can_move_to_position(self, target_position):
        '''
        Indicates whether this cell can move to this position.

        This simply checks if the target position is valid distance-wise and
        whether it is inside the map's bounds: it will not validate if there's
        a cell in the target position.

        Args:
            target_position (Position): the position to be checked.

        Returns:
            bool: whether this cell can move to the target position.
        '''
        return self._is_in_bounds(target_position) and \
                self.position.is_adjacent(target_position)

    def can_move_in_direction(self, direction):
        '''
        Indicates whether this cell can move in the specified direction.

        This simply checks if moving in the specified direction would be inside
        the map's bounds: it will not validate if there's a cell in the target
        position.

        Args:
            direction (Direction): the direction to be checked.

        Returns:
            bool: whether this cell can move in the specified direction.
        '''
        position = self.position.translated_by_offset(*direction.value)
        return self.can_move_to_position(position)

    def can_attack_position(self, target_position):
        '''
        Indicates whether this cell can attack this position.

        This simply checks if the target position is valid distance-wise and
        whether it is inside the map's bounds: it will not validate if there's
        a cell in the target position.

        Args:
            target_position (Position): the position to be checked.

        Returns:
            bool: whether this cell can attack the target position.
        '''
        return self._is_in_bounds(target_position) and \
                self.position.is_surrounding(target_position)

    def can_attack_cell(self, target_cell):
        '''
        Indicates whether this cell can attack the target cell's position.

        This checks if the target cell's position is within reach and whether
        it is inside the map's bounds.

        Args:
            target_cell (Cell): the cell to be checked.

        Returns:
            bool: whether this cell can attack the target position.
        '''
        return self.can_attack_position(target_cell.position)

    def attack_position(self, target_position):
        '''
        Causes this cell to attack the target position.

        The position should be valid, as checked by a call
        to Cell.can_attack_position.

        Args:
            target_position (Position): the position to be attacked.
        '''
        self._coordinator.communicator.emit_action(
            Action.attack(self.cell_id, target_position)
        )

    def attack_cell(self, target_cell):
        '''
        Causes this cell to attack the target cell.

        The cell should be within reach, as checked by a call
        to Cell.can_attack_cell.

        Args:
            target_cell (Cell): the cell to be attacked.
        '''
        self._coordinator.communicator.emit_action(
            Action.attack(self.cell_id, target_cell.position)
        )

    def explode(self):
        '''
        Causes this cell to explode.

        Explosing causes this cell to die, inflicting damage in every position
        in the map surrounding this cell's position.
        '''
        self._coordinator.communicator.emit_action(Action.explode(self.cell_id))

    def move_to_position(self, target_position):
        '''
        Causes this cell to move to the target position.

        The position should be valid, as checked by a call
        to Cell.can_move_to_position.

        Args:
            target_position (Position): the position to move to.
        '''
        self._coordinator.communicator.emit_action(
            Action.move(self.cell_id, target_position)
        )

    def move_in_direction(self, direction):
        '''
        Causes this cell to move in the specified direction.

        The position should be valid, as checked by a call
        to Cell.can_move_in_direction.

        Args:
            direction (Direction): the direction to move to.
        '''
        position = self.position.translated_by_offset(*direction.value)
        self.move_to_position(position)

class WorldState:
    '''
    Represents the state of the world.

    The world contains:
    * Cells, both yours and the enemy ones.
    * Map properties, like width and height.
    '''

    def __init__(self, width, height, my_team_id, my_column, enemy_column):
        self.width = width
        self.height = height
        self.my_team_id = my_team_id
        self.my_column = my_column
        self.enemy_column = enemy_column
        self.cells = {}

    def my_cells(self):
        '''
        Retrieves the cells that belong to your team.

        Returns:
            (list[Cell]): The list of cells that belong to you.
        '''
        return list(filter(
            lambda cell: cell.team_id == self.my_team_id,
            self.cells.values()
        ))

    def enemy_cells(self):
        '''
        Retrieves the cells that belong to the enemy.

        Returns:
            (list[Cell]): The list of cells that belong to the enemy.
        '''
        return list(filter(
            lambda cell: cell.team_id != self.my_team_id,
            self.cells.values()
        ))

    def cell_by_id(self, cell_id):
        '''
        Finds a cell by id.

        Args:
            cell_id (int): the cell id to be looked up

        Returns:
            Cell: the cell, if found. Otherwise None.
        '''
        return self.cells.get(cell_id)

    def my_starting_column(self):
        '''
        Gets the column in the grid in which your cells spawn. This is typically either 0
        or the grid's width - 1

        Returns:
            int: The column in which your cells spawn
        '''
        return self.my_column

    def enemy_starting_column(self):
        '''
        Gets the column in the grid in which the enemy cells spawn. This is typically either 0
        or the grid's width - 1

        Returns:
            int: The column in which the enemy cells spawn
        '''
        return self.enemy_column

class BotBase:
    '''
    The base class for any bot.

    Create a class named Bot in your code that inherits from this one
    and override the BotBase.run_round method with whatever your bot's logic is.
    '''

    def __init__(self, *args):
        super().__init__(*args)

    def run_round(self, world_state):
        '''
        Runs a round of the game.

        This method must be implemented by derived classes and should implement
        the bot's logic. Use the world_state to find your cells and emit an
        action for each of them.

        Args:
            world_state (WorldState): the current world state.
        '''
        raise Exception("Bot.run_round not implemented")

if __name__ == "__main__":
    communicator = Communicator(sys.stdin, sys.stdout)
    bot = Bot()
    coordinator = GameCoordinator(communicator, bot)
    coordinator.loop()
