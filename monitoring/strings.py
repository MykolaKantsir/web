# Commonly used strings
empty_string = ""

# Machine status
machine_stopped = "STOPPED"
machine_active = "ACTIVE"
machine_feed_hold = "FEED_HOLD"
machine_interupted = "INTERRUPTED"
machine_semi_automatic = "SEMI_AUTOMATIC"

stopped_statuses = [machine_stopped, machine_feed_hold, machine_interupted]


# default subprograms to ignore, all subprograms are setup cycles
subprograms_to_ignore = [
    'PRE_SUBPROGRAM.NC',
    'POST_SUBPROGRAM.NC',
    'O09007.NC',
    'DONT DELETE!.NC',
    ]


# Machine mode
mode_auto = "AUTOMATIC"
mode_mdi = "MANUAL_DATA_INPUT"
mode_hand_jog = "MANUAL"
unknown_mode = "UNKNOWN"

# Fomatted machine mode
MODE_FORMATTED_MAPPING = {
    mode_auto: "Auto",
    mode_mdi: "MDI",
    mode_hand_jog: "Jog",
}

# Machine Unnonwn
machine_uknown = "Unknown"
machine_network_name_unknown = "Unknown network name"