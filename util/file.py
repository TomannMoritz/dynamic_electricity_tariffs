import json
import pandas as pd
import numpy as np

import util.time as time

DATE_LABEL = "date"
TIME_LABEL = "TIME"
TIME_ZONE_LABEL = "time_zone"
DATA_VALUE_LABEL = "value"

TIME_START_LABEL = "startsAt"
TOTAL_PRICE_LABEL = "total"
PRICE_LABEL = "price"

VALUE_LABEL = "value"
LABEL_LABEL = "label"

TIMEZONE_OFFSET = 6
YEAR_POS = 4
DAY_POS = 2

DAYS_IN_A_WEEK = 7


def prepare_data(file_path: str):
    data = []
    dates = []

    with open(file_path, 'r') as f_in:
        for row in f_in:
            json_row = json.loads(row)
            key = next(iter(json_row.keys()))
            dates.append(key.replace("_", "-"))

            # collect energy prices for each day
            day_data = json_row[key]
            for values in day_data:
                time_value = values[TIME_START_LABEL].replace(key, "")
                value = values[TOTAL_PRICE_LABEL]

                data.append({
                    DATE_LABEL: key,
                    TIME_LABEL: time_value[1:-TIMEZONE_OFFSET],
                    TIME_ZONE_LABEL: time_value[-TIMEZONE_OFFSET:],
                    DATA_VALUE_LABEL: value,
                })
    return data, dates


def get_filtered_data(data: list, filtered_dates: list) -> list:
    return [row for row in data if row[DATE_LABEL] in filtered_dates]


def get_price_data(data: list) -> dict:
    price_data = [[] for _ in range(time.HOURS_IN_DAY * time.QUARTERS_IN_HOUR)]
    price_labels = [time.index_to_str(i) for i in range(time.HOURS_IN_DAY * time.QUARTERS_IN_HOUR)]

    for row in data:
        time_value = row[TIME_LABEL]
        index = time.str_to_index(time_value)

        price_value = row[DATA_VALUE_LABEL]
        price_data[index].append(price_value)

    # filter empty rows
    result = {PRICE_LABEL: [], LABEL_LABEL: []}
    for price, label in zip(price_data, price_labels):
        if price != []:
            result[PRICE_LABEL].append(price)
            result[LABEL_LABEL].append(label)

    return result


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


# --------------------------------------------------
def get_avg_month_values(data: list, dates: list, year: str) -> list:
    assert len(year) == YEAR_POS, f"[!] Invalid year: {year}"

    # format: yyyy-mm-dd
    # create a list with all month labels -> drop dates
    month_labels = [{PRICE_LABEL: date[:-DAY_POS]} for date in dates if year in date]
    df_month_labels = pd.DataFrame(month_labels)[PRICE_LABEL].unique()

    month_values = []

    for month in df_month_labels:
        month_dates = [date for date in dates if month in date]

        month_data = get_filtered_data(data, month_dates)
        month_results = get_price_data(month_data)

        month_avg = [np.mean(price) for price in month_results[PRICE_LABEL]]
        month_values.append(round(np.mean(month_avg), 4))
    return month_values


def get_avg_hour_values(data: list, dates: list, day_indicies: list) -> dict:
    day_dates = [date for i, date in enumerate(dates) if i % DAYS_IN_A_WEEK in day_indicies]
    day_data = get_filtered_data(data, day_dates)
    day_results = get_price_data(day_data)

    day_avg = [np.mean(price) for price in day_results[PRICE_LABEL]]
    return {VALUE_LABEL: day_avg, LABEL_LABEL: day_results[LABEL_LABEL]}
