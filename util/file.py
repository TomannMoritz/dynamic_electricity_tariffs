import pandas as pd
import datetime as dt

import util.general as gen


WEEKDAY_LABEL = "WeekDay"
_WEEKDAY_LABEL = "_WeekDay"

DATE_LABEL = "Date"
TIME_START_LABEL = "TimeStart"
TIME_END_LABEL = "TimeEnd"
TIME_ZONE_LABEL = "TimeZone"
VALUE_LABEL = "Value"

EXPECTED_COLUMN_LABELS = [
        DATE_LABEL,
        TIME_START_LABEL,
        TIME_END_LABEL,
        TIME_ZONE_LABEL,
        VALUE_LABEL
        ]

DATE_YEAR = "Year"
DATE_MONTH = "Month"
DATE_DAY = "Day"

DAY_OFFSET = 0
DAY_LEN = 2

MONTH_OFFSET = DAY_OFFSET + DAY_LEN + 1
MONTH_LEN = 2

YEAR_OFFSET = MONTH_OFFSET + MONTH_LEN + 1
YEAR_LEN = 4

DAYS_IN_A_WEEK = 7
CSV_SEPERATOR = ';'


def prepare_data(file_path: str):
    # convert csv file into pandas dataframe
    data = pd.read_csv(file_path, sep=CSV_SEPERATOR)

    # check column names
    data_labels = data.columns.tolist()

    invalid_size = len(EXPECTED_COLUMN_LABELS) != len(data_labels)
    if invalid_size:
        return None, None

    for i, label in enumerate(EXPECTED_COLUMN_LABELS):
        found_label = data_labels[i]
        different_label = label != found_label

        if different_label:
            print(f"[!] Different label:\n\tFound: {found_label} \t Expected: {label}")
            return None, None

    data[DATE_DAY] = data[DATE_LABEL].str[DAY_OFFSET:DAY_OFFSET + DAY_LEN]
    data[DATE_MONTH] = data[DATE_LABEL].str[MONTH_OFFSET:MONTH_OFFSET + MONTH_LEN]
    data[DATE_YEAR] = data[DATE_LABEL].str[YEAR_OFFSET:YEAR_OFFSET + YEAR_LEN]

    # add week day indicies
    data = add_week_days(data)

    data[DATE_LABEL] = data[DATE_YEAR] + "-" + data[DATE_MONTH] + "-" + data[DATE_DAY]
    data[DATE_MONTH] = data[DATE_MONTH].astype(int)
    data[DATE_MONTH] = data[DATE_MONTH].apply(lambda x: gen.MONTH_LABELS[x - 1])

    # convert datatypes
    data = convert_columntype_to_float(data, VALUE_LABEL)

    # filter dates
    dates = data[DATE_LABEL].unique()
    return data, dates


def convert_columntype_to_float(df: pd.DataFrame, column_name: str):
    df[column_name] = df[column_name].str.replace(',', '.')
    df[column_name] = df[column_name].astype(float)
    return df


def add_week_days(df: pd.DataFrame) -> pd.DataFrame:
    df[_WEEKDAY_LABEL] = df.apply(
            lambda x: (dt.datetime(
                int(x[DATE_YEAR]),
                int(x[DATE_MONTH]),
                int(x[DATE_DAY])
                ).weekday() - 1) % 7, axis=1)

    df[WEEKDAY_LABEL] = df.apply(
            lambda x: gen.DAY_LABELS[x[_WEEKDAY_LABEL]], axis=1)

    return df
