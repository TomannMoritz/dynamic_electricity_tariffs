import marimo

__generated_with = "0.18.4"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    import altair as alt

    import util.file as file
    import util.general as gen

    mo.md("# Dynamic electricity tariffs")
    return alt, file, gen, mo


@app.cell
def _(file, mo):
    file_name = "data.csv"
    data, dates = file.prepare_data(file_name)

    mo.vstack([
        mo.md("## Data"),
        data
    ])
    return data, dates


@app.cell
def _():
    PRICE_LABEL = "Price"
    MONTH_LABEL = "Month"
    TIME_LABEL = "Time"
    YEAR_LABEL = "Year"
    DAY_LABEL = "Day"

    # Settings
    DECIMAL_FORMAT = ".2f"
    POINT_SIZE = 100

    COLOR_SCHEME = {'scheme': 'spectral'}

    tab_line_label = "Avg price"
    tab_box_plot_label = "Box plot"
    tab_bar_plot_label = "Stacked bar plot"
    return (
        COLOR_SCHEME,
        DAY_LABEL,
        DECIMAL_FORMAT,
        MONTH_LABEL,
        POINT_SIZE,
        PRICE_LABEL,
        TIME_LABEL,
        YEAR_LABEL,
        tab_bar_plot_label,
        tab_box_plot_label,
        tab_line_label,
    )


@app.cell
def _(
    COLOR_SCHEME,
    DECIMAL_FORMAT,
    MONTH_LABEL,
    PRICE_LABEL,
    YEAR_LABEL,
    alt,
    data,
    file,
    gen,
    mo,
):
    year_month_data = data[[file.DATE_YEAR, file.DATE_MONTH, file.VALUE_LABEL]]
    df_year_month = year_month_data.groupby(by=[file.DATE_YEAR, file.DATE_MONTH])[file.VALUE_LABEL].mean()
    df_year_month = df_year_month.reset_index()

    # NOTE: Assumption that dates are in order (and without gaps)
    # title with first and last date
    year_month_title = f"Average monthly tariffs: {data[file.DATE_LABEL][0]} - {data[file.DATE_LABEL][len(data[file.DATE_LABEL]) - 1]}"

    # average line
    year_month_plot = alt.Chart(df_year_month, title=year_month_title).mark_bar().encode(
        x=alt.X(file.DATE_MONTH, title=MONTH_LABEL, sort=gen.MONTH_LABELS),
        y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL, stack=True),
        order=alt.Order(file.DATE_YEAR, sort="ascending"),
        tooltip=[
            alt.Tooltip(file.DATE_YEAR, title=YEAR_LABEL),
            alt.Tooltip(file.DATE_MONTH, title=MONTH_LABEL),
            alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=DECIMAL_FORMAT)
        ],
        color=alt.Color(file.DATE_YEAR, title=YEAR_LABEL, scale=COLOR_SCHEME, sort="descending"),
    )


    mo.vstack([
        mo.md("## " + year_month_title),
        year_month_plot
    ])
    return


@app.cell
def _(dates, gen, mo, tab_bar_plot_label, tab_line_label):
    day_selection = mo.ui.multiselect(options=gen.DAY_LABELS, value=gen.DAY_LABELS, label="Select days: ")
    day_date_range = mo.ui.date_range(start=dates[0], stop=dates[-1])
    day_tabs = mo.ui.tabs({
        tab_line_label: "",
        tab_bar_plot_label: ""
    })

    mo.vstack([
        mo.md(f"## Average hourly tariffs per day: {gen.show_date(dates[0])} - {gen.show_date(dates[-1])}"),
        day_selection,
        day_date_range,
        day_tabs
    ])
    return day_date_range, day_selection, day_tabs


@app.cell
def _(
    COLOR_SCHEME,
    DAY_LABEL,
    DECIMAL_FORMAT,
    POINT_SIZE,
    PRICE_LABEL,
    TIME_LABEL,
    YEAR_LABEL,
    alt,
    data,
    day_date_range,
    day_selection,
    day_tabs,
    file,
    gen,
    tab_bar_plot_label,
    tab_line_label,
):
    day_plot = []

    day_hourly_data = data[data[file.WEEKDAY_LABEL].isin(day_selection.value)]

    day_start, day_end = day_date_range.value
    day_start = str(day_start)
    day_end = str(day_end)

    # filter data
    day_title = f"Average hourly tariffs per day: {day_start} - {day_end}"
    day_hourly_data = day_hourly_data[day_hourly_data[file.DATE_LABEL] >= day_start]
    day_hourly_data = day_hourly_data[day_hourly_data[file.DATE_LABEL] <= day_end]

    df_day_hourly_group = day_hourly_data.groupby(by=[file._WEEKDAY_LABEL, file.WEEKDAY_LABEL, file.TIME_START_LABEL])[file.VALUE_LABEL]


    # avg line plot
    if day_tabs.value == tab_line_label:
        df_day_hour = df_day_hourly_group.mean()
        df_day_hour = df_day_hour.reset_index()

        # create plots
        day_lines = alt.Chart(df_day_hour, title=day_title).mark_line().encode(
            x=alt.X(field=file.TIME_START_LABEL, type="nominal", title=TIME_LABEL),
            y=alt.Y(field=file.VALUE_LABEL, type="quantitative", title=PRICE_LABEL),
            color=alt.Color(file.WEEKDAY_LABEL, sort=False)
        )


        day_points = alt.Chart(df_day_hour).mark_point(size=POINT_SIZE/2).encode(
            x=alt.X(field=file.TIME_START_LABEL, type="nominal", title=TIME_LABEL),
            y=alt.Y(field=file.VALUE_LABEL, type="quantitative", title=PRICE_LABEL),
            color=alt.Color(field=file.WEEKDAY_LABEL, sort=False),
            tooltip=[
                alt.Tooltip(file.WEEKDAY_LABEL, title=DAY_LABEL),
                alt.Tooltip(file.TIME_START_LABEL, title=TIME_LABEL, type="nominal"),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=DECIMAL_FORMAT)
            ]
        )

        day_plot = [day_lines, day_points]


    # stacked bar plot
    if day_tabs.value == tab_bar_plot_label:
        df_day_hour = df_day_hourly_group.mean()
        df_day_hour = df_day_hour.reset_index()

        day_bar_plot = alt.Chart(df_day_hour, title=day_title).mark_bar().encode(
            x=alt.X(file.TIME_START_LABEL, title=TIME_LABEL, type="nominal"),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL, stack=True),
            order=alt.Order(file._WEEKDAY_LABEL, sort="descending"),
            tooltip=[
                alt.Tooltip(file.WEEKDAY_LABEL, title=YEAR_LABEL),
                alt.Tooltip(file.TIME_START_LABEL, title=TIME_LABEL, type="nominal"),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=DECIMAL_FORMAT)
            ],
            color=alt.Color(file.WEEKDAY_LABEL, title=DAY_LABEL, scale=COLOR_SCHEME, sort=gen.DAY_LABELS),
        )

        day_plot = [day_bar_plot]


    alt.layer(*day_plot)
    return


@app.cell
def _(dates, mo, tab_box_plot_label, tab_line_label):
    date_selection = mo.ui.date_range(start=dates[0], stop=dates[-1])
    date_range_tab = mo.ui.tabs({
        tab_line_label: "",
        tab_box_plot_label: ""
    })


    mo.vstack([
        mo.md("## Hourly tariffs - Date Range"),
        date_selection,
        date_range_tab
    ])
    return date_range_tab, date_selection


@app.cell
def _(
    DECIMAL_FORMAT,
    POINT_SIZE,
    PRICE_LABEL,
    TIME_LABEL,
    alt,
    data,
    date_range_tab,
    date_selection,
    file,
    tab_box_plot_label,
    tab_line_label,
):
    date_range_plot = []
    legend_colors = ["orange", "blue"]

    # date ranges
    # total range
    total_legend = f"{date_selection.start} - {date_selection.stop}"

    # total average line plot
    df_total_hourly = data[[file.TIME_START_LABEL, file.VALUE_LABEL]].groupby(by=[file.TIME_START_LABEL])[file.VALUE_LABEL].mean()
    df_total_hourly = df_total_hourly.reset_index()


    total_hour_plot = alt.Chart(df_total_hourly).mark_line(strokeDash=[4,4], color=legend_colors[0]).encode(
            x=alt.X(file.TIME_START_LABEL, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
        )


    date_range_plot = [total_hour_plot]


    # selected range
    start_date, stop_date = date_selection.value
    start_date = str(start_date)
    stop_date = str(stop_date)
    range_legend = f"{start_date} - {stop_date}"

    # filter date range
    range_hour_title = f"Average hourly tariffs"
    range_hour_data = data[data[file.DATE_LABEL] >= start_date]
    range_hour_data = range_hour_data[range_hour_data[file.DATE_LABEL] <= stop_date]

    range_hour_group = range_hour_data[[file.TIME_START_LABEL, file.VALUE_LABEL]].groupby(by=[file.TIME_START_LABEL])[file.VALUE_LABEL]


    # line plot
    if date_range_tab.value == tab_line_label:
        df_range_hour = range_hour_group.mean()
        df_range_hour = df_range_hour.reset_index()

        # avg. line
        date_range_line_plot = alt.Chart(df_range_hour, title=range_hour_title).mark_line().encode(
            x=alt.X(file.TIME_START_LABEL, sort=False),
            y=alt.Y(file.VALUE_LABEL, PRICE_LABEL)
        )
        date_range_plot.append(date_range_line_plot)

        # points
        date_range_point_plot = alt.Chart(df_range_hour).mark_point(size=POINT_SIZE).encode(
            x=alt.X(file.TIME_START_LABEL, sort=False, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            tooltip=[
                alt.Tooltip(file.TIME_START_LABEL, title=TIME_LABEL),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=DECIMAL_FORMAT)
            ]
        )
        date_range_plot.append(date_range_point_plot)


    # box plot
    if date_range_tab.value == tab_box_plot_label:
        date_range_box_plot = alt.Chart(range_hour_data, title=range_hour_title).mark_boxplot(outliers=False).encode(
            x=alt.X(file.TIME_START_LABEL, sort=False, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL)
        )

        date_range_plot.append(date_range_box_plot)


    range_legend_plot = alt.Chart().mark_line().encode(
            color=alt.Color("category:N", scale=alt.Scale(
                domain=[total_legend, range_legend],
                range=legend_colors,
            ), title="Legend")
        )
    date_range_plot.append(range_legend_plot)

    alt.layer(*date_range_plot)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
