
# --------------------------------------------------
# constants
MONTH_LABELS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

DATE_SPEARATOR = '-'

# --------------------------------------------------
# helper functions


def get_index(array: list, value) -> int:
    for i, ele in enumerate(array):
        if ele == value:
            return i
    return -1


def show_date(date: str) -> str:
    date_list = date.split(DATE_SPEARATOR)
    return '.'.join(list(reversed(date_list)))
