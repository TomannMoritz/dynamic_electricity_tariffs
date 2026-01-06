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


def get_dataframe(df_data: list):
    return pd.DataFrame(df_data)


def create_dataframe(value_data: list, label_data: list, value_label: str = VALUE_LABEL, label_label: str = LABEL_LABEL):
    num_values = len(value_data)
    num_labels = len(label_data)
    assert num_values == num_labels, f"[!] Invalid lengths: \nValues: {num_values}\nLabels: {num_labels}"

    results = []
    for value, label in zip(value_data, label_data):
        results.append({
            value_label: value,
            label_label: label
            })
    return pd.DataFrame(results), value_label, label_label


# --------------------------------------------------
def get_avg_month_values(data: list, dates: list, year: str):
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


def get_avg_hour_values(data: list, dates: list, day_indicies: list):
    day_dates = [date for i, date in enumerate(dates) if i % DAYS_IN_A_WEEK in day_indicies]
    day_data = get_filtered_data(data, day_dates)
    day_results = get_price_data(day_data)

    day_avg = [np.mean(price) for price in day_results[PRICE_LABEL]]
    return {VALUE_LABEL: day_avg, LABEL_LABEL: day_results[LABEL_LABEL]}
