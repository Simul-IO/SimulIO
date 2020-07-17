# START_TRANSACTION: init
# EFFECT
return {
    'send_neighbour_ids': send_neighbour_ids,
    'receive_neighbour_ids': receive_neighbour_ids,
    'uid': uid,
    'max_uid': uid,
    'state': 'UNKNOWN',
    'leader': None,
    'received_message': '',
    'alive': True,
}
# OUTPUT
[[node_id, 'uid ' + str(current_state['max_uid'])] for node_id in current_state['send_neighbour_ids']]
# END_TRANSACTION

# START_TRANSACTION: receive
# EFFECT
{
    'received_message': message,
}
# END_TRANSACTION

# START_TRANSACTION: receive_uid
# PRE_CONDITION
current_state['received_message'].startswith('uid ') and current_state['state'] != 'LEADER'
# EFFECT
{
    'max_uid': int(current_state['received_message'][4:]),
    'received_message': '',
} if int(current_state['received_message'][4:]) > current_state['max_uid'] else {} if int(
    current_state['received_message'][4:]) < current_state['max_uid'] else {'state': 'LEADER',
                                                                            'received_message': '',
                                                                            'leader': current_state['uid'], } if int(
    current_state['received_message'][4:]) == current_state['uid'] else {
    'received_message': '', }
# OUTPUT
[[node_id, 'uid ' + str(current_state['max_uid'])] for node_id in current_state['send_neighbour_ids']]
# END_TRANSACTION

# START_TRANSACTION: receive_leader
# PRE_CONDITION
current_state['received_message'].startswith('leader ')
# EFFECT
{
    'leader': int(current_state['received_message'][7:]),
    'alive': False,
    'state': 'KNOWN',
    'received_message': '',
}
# OUTPUT
[[node_id, 'leader ' + str(current_state['leader'])] for node_id in current_state['send_neighbour_ids']]
# END_TRANSACTION


# START_TRANSACTION: send_leader
# PRE_CONDITION
current_state['state'] == 'LEADER'
# EFFECT
{
    'alive': False,
}
# OUTPUT
[[node_id, 'leader ' + str(current_state['uid'])] for node_id in current_state['send_neighbour_ids']]
# END_TRANSACTION
