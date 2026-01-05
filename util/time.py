# Time format: hh:mm:sss

HOURS_IN_DAY = 24
QUARTERS_IN_HOUR = 4

HOUR_LABEL = "hour"
MIN_LABEL = "min"
SEC_LABEL = "sec"

HOUR_POS = 2
MIN_POS = 2
SEC_POS = 3

FILL_CHAR = '0'


def str_to_values(time: str):
    values = time.split(":")
    assert len(values) == 3, f"[!] Invalid time: {time}"

    return {HOUR_LABEL: values[0], MIN_LABEL: values[1], SEC_LABEL: values[2]}


def value_to_str(values) -> str:
    keys = values.keys()
    valid_keys = HOUR_LABEL in keys and MIN_LABEL in keys and SEC_LABEL in keys
    assert valid_keys, f"[!] Invalid time values: {values}"

    hour = str(values[HOUR_LABEL]).zfill(HOUR_POS)
    min = str(values[MIN_LABEL]).zfill(MIN_POS)
    sec = str(values[SEC_LABEL]).ljust(SEC_POS, FILL_CHAR)
    return f"{hour}:{min}:{sec}"


# Energy prices are currently calculated every 15 minutes. (Quarterly)
# As a result, more precise information (e.g. seconds) is ignored
def str_to_index(time: str) -> int:
    values = str_to_values(time)
    return int(values[HOUR_LABEL]) * QUARTERS_IN_HOUR + int(values[MIN_LABEL])


def index_to_str(index: int) -> str:
    valid_index = index >= 0 and index < HOURS_IN_DAY * QUARTERS_IN_HOUR
    assert valid_index, f"[!] Invalid index: {index}"

    values = {HOUR_LABEL: int(index / QUARTERS_IN_HOUR), MIN_LABEL: int(index % QUARTERS_IN_HOUR), SEC_LABEL: 0}
    return value_to_str(values)
