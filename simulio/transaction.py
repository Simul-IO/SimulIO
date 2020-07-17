DEFAULT_PRE_CONDITION = 'False'
DEFAULT_EFFECT = 'state'
DEFAULT_OUTPUT = '[]'


class Transaction:
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


START_TRANSACTION = '# START_TRANSACTION: '
PRECONDITION_TRANSACTION = '# PRE_CONDITION'
EFFECT_TRANSACTION = '# EFFECT'
OUTPUT_TRANSACTION = '# OUTPUT'
END_TRANSACTION = '# END_TRANSACTION'


def parse(lines):
    transactions = {}
    transaction_name = None
    transaction_effect = None
    transaction_pre_condition = None
    transaction_output = None
    reader_state = None
    for line in lines:
        if line.startswith(START_TRANSACTION) and reader_state is None:
            transaction_name = line[len(START_TRANSACTION):].strip()
            transaction_effect = ''
            transaction_pre_condition = ''
            transaction_output = ''
            reader_state = None
        elif line.startswith(PRECONDITION_TRANSACTION):
            reader_state = PRECONDITION_TRANSACTION
        elif line.startswith(EFFECT_TRANSACTION):
            reader_state = EFFECT_TRANSACTION
        elif line.startswith(OUTPUT_TRANSACTION):
            reader_state = OUTPUT_TRANSACTION
        elif line.startswith(END_TRANSACTION):
            transactions[transaction_name] = Transaction(transaction_pre_condition, transaction_effect,
                                                         transaction_output)
            transaction_name = None
            transaction_effect = None
            transaction_pre_condition = None
            transaction_output = None
            reader_state = None
        elif reader_state == PRECONDITION_TRANSACTION:
            transaction_pre_condition += line
        elif reader_state == EFFECT_TRANSACTION:
            transaction_effect += line
        elif reader_state == OUTPUT_TRANSACTION:
            transaction_output += line

    return transactions
