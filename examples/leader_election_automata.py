# START_TRANSACTION: init
# EFFECT
{
    'send_neighbour_ids': send_neighbour_ids,
    'receive_neighbour_ids': receive_neighbour_ids,
    'uid': uid,
    'max_uid': uid,
    'state': 'UNKNOWN',
    'leader': None,
    'received_message': [],
    'alive': True,
    'new_uid': False,
}
# OUTPUT
[[node_id, 'uid ' + str(state['max_uid'])] for node_id in state['send_neighbour_ids']]
# END_TRANSACTION

# START_TRANSACTION: receive
# EFFECT
{
    'received_message': state['received_message']+[message],
}
# END_TRANSACTION

# START_TRANSACTION: receive_uid
# PRE_CONDITION
state['received_message'] and state['received_message'][0].startswith('uid ') and state['state'] != 'LEADER'
# EFFECT
{
    'max_uid': int(state['received_message'][0][4:]),
    'received_message': [],
    'new_uid': True,
} if int(state['received_message'][0][4:]) > state['max_uid'] else {'new_uid': False, 'received_message': [],} if int(
    state['received_message'][0][4:]) < state['max_uid'] else {'state': 'LEADER',
                                                                            'received_message': [],
                                                                            'leader': state['uid'],
                                                                            'new_uid': False, } if int(
    state['received_message'][0][4:]) == state['uid'] else {
    'received_message': [], 'new_uid': False}
# OUTPUT
[[node_id, 'uid ' + str(state['max_uid'])] for node_id in state['send_neighbour_ids']] if state[
    'new_uid'] else []
# END_TRANSACTION

# START_TRANSACTION: receive_leader
# PRE_CONDITION
state['received_message'] and state['received_message'][0].startswith('leader ')
# EFFECT
{
    'leader': int(state['received_message'][0][7:]),
    'alive': False,
    'state': 'KNOWN',
    'received_message': [],
}
# OUTPUT
[[node_id, 'leader ' + str(state['leader'])] for node_id in state['send_neighbour_ids']]
# END_TRANSACTION


# START_TRANSACTION: send_leader
# PRE_CONDITION
state['state'] == 'LEADER'
# EFFECT
{
    'alive': False,
}
# OUTPUT
[[node_id, 'leader ' + str(state['uid'])] for node_id in state['send_neighbour_ids']]
# END_TRANSACTION


# START_TRANSACTION: visualize
# EFFECT
{
    'label': 'uid: ' + str(state['uid']) + '\nmax_uid: ' + str(
        state['max_uid']) + '\nr_m: ' + str(state['received_message']) + '\nstate: ' + str(
        state['state']),
    'color': '#cccccc' if state['state'] == 'UNKNOWN' else '#f7c7c7' if state['state'] == 'LEADER' else '#c7cff7',
}
# END_TRANSACTION
