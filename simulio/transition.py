DEFAULT_PRE_CONDITION = 'return False'
DEFAULT_EFFECT = 'return state'
DEFAULT_OUTPUT = 'return []'


class Transition:
    def __init__(self, pre_condition=None, effect=None, output=None):
        if not pre_condition:
            pre_condition = DEFAULT_PRE_CONDITION
        if not effect:
            effect = DEFAULT_EFFECT
        if not output:
            output = DEFAULT_OUTPUT
        self.pre_condition = pre_condition
        self.effect = effect
        self.output = output


START_TRANSITION = '# START_TRANSITION: '
PRECONDITION_TRANSITION = '# PRE_CONDITION'
EFFECT_TRANSITION = '# EFFECT'
OUTPUT_TRANSITION = '# OUTPUT'
END_TRANSITION = '# END_TRANSITION'


def parse(lines):
    transitions = {}
    transition_name = None
    transition_effect = None
    transition_pre_condition = None
    transition_output = None
    reader_state = None
    for line in lines:
        if line.startswith(START_TRANSITION) and reader_state is None:
            transition_name = line[len(START_TRANSITION):].strip()
            transition_effect = ''
            transition_pre_condition = ''
            transition_output = ''
            reader_state = None
        elif line.startswith(PRECONDITION_TRANSITION):
            reader_state = PRECONDITION_TRANSITION
        elif line.startswith(EFFECT_TRANSITION):
            reader_state = EFFECT_TRANSITION
        elif line.startswith(OUTPUT_TRANSITION):
            reader_state = OUTPUT_TRANSITION
        elif line.startswith(END_TRANSITION):
            transitions[transition_name] = Transition(transition_pre_condition, transition_effect,
                                                        transition_output)
            transition_name = None
            transition_effect = None
            transition_pre_condition = None
            transition_output = None
            reader_state = None
        elif reader_state == PRECONDITION_TRANSITION:
            transition_pre_condition += line
        elif reader_state == EFFECT_TRANSITION:
            transition_effect += line
        elif reader_state == OUTPUT_TRANSITION:
            transition_output += line

    return transitions
