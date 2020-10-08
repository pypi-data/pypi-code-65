from pymint.mintcomponent import MINTComponent
from lfr.netlistgenerator.v2.mappingoption import MappingOption
from lfr.netlistgenerator.mappinglibrary import MappingLibrary
from lfr.compiler.module import Module


def generate_MARS_library() -> MappingLibrary:
    # TODO - Programatically create each of the items necessary for the MARS primitive library,
    # we shall serialize them after experimentation

    mix_primitive = MappingOption()

    mint_component = MINTComponent("mixer_interaction", "MIXER")

    mix_primitive.init_single_component(mint_component)

    # mix_primitive.add



def generate(module: Module):
    # First go through all the interactions in the design

    # IF interaction is mix/sieve/divide/dilute/meter look at the library
    # to get all the options available and set them up as options for the
    # construction graph to pick and choose from the options.
    #
    # FUTURE WORK
    #
    # Do the regex matching to find the mapping options

    # Apply all the explicit mappings in the module to the nodes, overwriting
    # the options from the library to match against

    # Size all the Meter/Dilute/Divide nodes based on the value nodes

    # Size all the node's netlist components to based on the CONSTRAINTS set
    # by the postprocessor

    # Finally join all the netlist pieces attached to the construction nodes
    # and the input/output/load/carrier flows
    # MINIMIZE - carrier / load flows - this might require us to generate
    # multiple netlist options and pick the best

    # Generate all the unaccounted carriers and waste output lines necessary
    # for this to function

    pass
