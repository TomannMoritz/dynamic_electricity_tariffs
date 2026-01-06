
# --------------------------------------------------
# constants
MONTH_LABELS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
DAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# --------------------------------------------------
# helper functions

def get_index(array: list, value) -> int:
    for i, ele in enumerate(array):
        if ele == value:
            return i
    return -1
