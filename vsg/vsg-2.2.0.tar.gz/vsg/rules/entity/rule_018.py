
from vsg.rules import keyword_alignment_rule


class rule_018(keyword_alignment_rule):
    '''
    Entity rule 018 ensures the alignment of the := operator for each generic and port in the entity.
    '''

    def __init__(self):
        keyword_alignment_rule.__init__(self, 'entity', '018')
        self.solution = 'Inconsistent alignment of ":=" in generic or port declaration of entity.'
        self.sKeyword = ':='
        self.sStartGroupTrigger = 'isEntityDeclaration'
        self.sEndGroupTrigger = 'isEndEntityDeclaration'
        self.lLineTriggers = ['isGenericDeclaration', 'isPortDeclaration']

        self.separate_generic_port_alignment = True
        self.configuration.append('separate_generic_port_alignment')

        self.configuration_triggers += [{'name': 'separate_generic_port_alignment', 'triggers': ['isEndGenericMap']}]
