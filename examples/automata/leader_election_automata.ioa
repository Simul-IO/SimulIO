# Leader Election Algorithm in Unidirectional Ring

# START_TRANSACTION: init
# EFFECT
{
    'output_neighbour_ids': output_neighbour_ids,
    'input_neighbour_ids': input_neighbour_ids,
    'uid': uid,
    'max_uid': uid,
    'state': 'UNKNOWN',
    'leader': None,
    'received_messages': [],
    'alive': True,
    'new_uid': False,
}
# OUTPUT
[[node_id, 'uid ' + str(state['max_uid'])] for node_id in state['output_neighbour_ids']]
# END_TRANSACTION

# START_TRANSACTION: receive
# EFFECT
{
    'received_messages': state['received_messages'] + [message],
}
# END_TRANSACTION

# START_TRANSACTION: receive_uid
# PRE_CONDITION
state['received_messages'] and state['received_messages'][0].startswith('uid ') and state['state'] != 'LEADER'
# EFFECT
{
    'max_uid': int(state['received_messages'][0][4:]),
    'received_messages': state['received_messages'][1:],
    'new_uid': True,
} if int(state['received_messages'][0][4:]) > state['max_uid'] \
    else {'new_uid': False,
          'received_messages': state['received_messages'][1:],
          } if int(state['received_messages'][0][4:]) < state['max_uid'] \
    else {'state': 'LEADER',
          'received_messages': state['received_messages'][1:],
          'leader': state['uid'],
          'new_uid': False,
          }
# OUTPUT
[[node_id, 'uid ' + str(state['max_uid'])] for node_id in state['output_neighbour_ids']] if state['new_uid'] else []
# END_TRANSACTION

# START_TRANSACTION: receive_leader
# PRE_CONDITION
state['received_messages'] and state['received_messages'][0].startswith('leader ')
# EFFECT
{
    'leader': int(state['received_messages'][0][7:]),
    'alive': False,
    'state': 'KNOWN',
    'received_messages': state['received_messages'][1:],
}
# OUTPUT
[[node_id, 'leader ' + str(state['leader'])] for node_id in state['output_neighbour_ids']]
# END_TRANSACTION


# START_TRANSACTION: send_leader
# PRE_CONDITION
state['state'] == 'LEADER'
# EFFECT
{
    'alive': False,
}
# OUTPUT
[[node_id, 'leader ' + str(state['uid'])] for node_id in state['output_neighbour_ids']]
# END_TRANSACTION


# START_TRANSACTION: visualize
# EFFECT
{
    'label': 'uid: ' + str(state['uid']) +
             '\nmax_uid: ' + str(state['max_uid']) +
             '\nr_m: ' + str(state['received_messages']) +
             '\nstate: ' + str(state['state']),
    'color': '#cccccc' if state['state'] == 'UNKNOWN' else '#f7c7c7' if state['state'] == 'LEADER' else '#c7cff7',
}
# END_TRANSACTION
