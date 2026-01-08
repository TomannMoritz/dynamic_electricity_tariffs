import json
import pandas as pd

DATE_LABEL = "date"
TIME_LABEL = "time"
TIME_ZONE_LABEL = "time_zone"
VALUE_LABEL = "value"

TIMEZONE_OFFSET = 6

TIME_START_LABEL = "startsAt"
TOTAL_PRICE_LABEL = "total"

DAYS_IN_A_WEEK = 7


def prepare_data(file_path: str):
    data = []
    dates = []

    with open(file_path, 'r') as f_in:
        for row in f_in:
            json_row = json.loads(row)
            key = next(iter(json_row.keys()))
            dates.append(key)

            # collect energy prices for each day
            day_data = json_row[key]
            for values in day_data:
                time_value = values[TIME_START_LABEL].replace(key, "")
                value = values[TOTAL_PRICE_LABEL]

                data.append({
                    DATE_LABEL: key,
                    TIME_LABEL: time_value[1:-TIMEZONE_OFFSET],
                    TIME_ZONE_LABEL: time_value[-TIMEZONE_OFFSET:],
                    VALUE_LABEL: value,
                })
    return data, dates


def get_filtered_data(data: list, filtered_dates: list) -> list:
    return [row for row in data if row[DATE_LABEL] in filtered_dates]


def dict_to_dataframe(data: dict):
    keys = data.keys()
    assert len(data) > 0, f"[!] Invalid dictionary: {data}"
    assert all([type(data[key]) is list for key in keys]), f"[!] Invalid types!"

    array_len = len(data[next(iter(keys))])
    assert all([len(data[key]) == array_len for key in keys]), f"[!] Lengths does not match!"

    result = []
    for i in range(array_len):
        row = {}
        for key in keys:
            row[key] = data[key][i]
        result.append(row)
    return pd.DataFrame(result)


def get_dataframe(data: dict):
    return pd.DataFrame(data)


def clean_dataframe(df, value_label=VALUE_LABEL, time_label=TIME_LABEL, decimal_pos=3):
    df[value_label] = df[value_label].round(decimal_pos)

    # format: HH:MM
    df[time_label] = df[time_label].apply(lambda x: str(x)[:5])
    return df


# --------------------------------------------------
def get_date_range_data(data: list, dates: list, date_start: str, date_end: str) -> list:
    # format: yyyy-mm-dd
    # create a list with all month labels -> drop dates

    day_dates = [date for date in dates if date >= date_start and date <= date_end]

    day_data = get_filtered_data(data, day_dates)
    return day_data


def get_day_data(data: list, dates: list, day_indicies: list) -> list:
    day_dates = [date for i, date in enumerate(dates) if i % DAYS_IN_A_WEEK in day_indicies]
    day_data = get_filtered_data(data, day_dates)

    return day_data
