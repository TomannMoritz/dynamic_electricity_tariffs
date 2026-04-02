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
def _(data, file, mo):
    PRICE_LABEL = "Price"
    MONTH_LABEL = "Month"
    TIME_LABEL = "Time"

    # Settings
    DECIMAL_POS = 2
    POINT_SIZE = 100


    # ui elements
    year_list = data[file.DATE_YEAR].unique().tolist()
    year_selection = mo.ui.dropdown(options=year_list, value=year_list[0], label="Select year: ")

    tab_line_label = "Avg price"
    tab_box_plot_label = "Box plot"
    year_tab = mo.ui.tabs({
        tab_line_label: "",
        tab_box_plot_label: ""
    })
    return (
        DECIMAL_POS,
        MONTH_LABEL,
        POINT_SIZE,
        PRICE_LABEL,
        TIME_LABEL,
        tab_box_plot_label,
        tab_line_label,
        year_selection,
        year_tab,
    )


@app.cell
def _(
    DECIMAL_POS,
    MONTH_LABEL,
    POINT_SIZE,
    PRICE_LABEL,
    alt,
    data,
    dates,
    file,
    gen,
    mo,
    tab_box_plot_label,
    tab_line_label,
    year_selection,
    year_tab,
):
    year_month_values = data[[file.DATE_YEAR, file.DATE_MONTH, file.VALUE_LABEL]]
    year_month_values = data[(data[file.DATE_YEAR] == year_selection.value)]
    month_groupby = year_month_values.groupby(by=[file.DATE_YEAR, file.DATE_MONTH])[file.VALUE_LABEL]

    year_plot = []

    # line plot
    if year_tab.value == tab_line_label:
        df_months = month_groupby.mean()
        df_months = df_months.reset_index()
        df_months[file.VALUE_LABEL] = df_months[file.VALUE_LABEL].round(DECIMAL_POS)

        # average line
        year_line_plot = alt.Chart(df_months).mark_line().encode(
            x=alt.X(file.DATE_MONTH, sort=False, title=MONTH_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL)
        )
        year_plot.append(year_line_plot)

        # points with tooltip
        year_points = alt.Chart(df_months).mark_point(
            size=POINT_SIZE,
            filled=True
        ).encode(
            x=alt.X(file.DATE_MONTH, sort=None, title=MONTH_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            tooltip=[
                alt.Tooltip(file.DATE_MONTH, title=MONTH_LABEL),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL)
            ]
        )
        year_plot.append(year_points)


    # box plot
    if year_tab.value == tab_box_plot_label:
        year_box_plot = alt.Chart(year_month_values).mark_boxplot(outliers=False).encode(
            x=alt.X(file.DATE_MONTH, sort=False, title=MONTH_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL)
        )
        year_plot.append(year_box_plot)


    mo.vstack([
        mo.md(f"## Average monthly tariffs: {gen.show_date(dates[0])} - {gen.show_date(dates[-1])}"),
        year_selection,
        year_tab,
        alt.layer(*year_plot)
    ])
    return


@app.cell
def _(dates, gen, mo, tab_box_plot_label, tab_line_label):
    day_selection = mo.ui.multiselect(options=gen.DAY_LABELS, value=gen.DAY_LABELS, label="Select days: ")
    day_tabs = mo.ui.tabs({
        tab_line_label: "",
        tab_box_plot_label: ""
    })

    mo.vstack([
        mo.md(f"## Average hourly tariffs: {gen.show_date(dates[0])} - {gen.show_date(dates[-1])}"),
        day_selection,
        day_tabs
    ])
    return day_selection, day_tabs


@app.cell
def _(
    POINT_SIZE,
    PRICE_LABEL,
    TIME_LABEL,
    alt,
    data,
    day_selection,
    day_tabs,
    file,
    tab_box_plot_label,
    tab_line_label,
):
    day_plot = []

    day_hourly_data = data[data[file.WEEKDAY_LABEL].isin(day_selection.value)]

    df_day_groupby = day_hourly_data[[file._WEEKDAY_LABEL, file.WEEKDAY_LABEL, file.TIME_START_LABEL, file.VALUE_LABEL]].groupby(by=[file._WEEKDAY_LABEL, file.WEEKDAY_LABEL, file.TIME_START_LABEL])[file.VALUE_LABEL]


    # avg line plot
    if day_tabs.value == tab_line_label:
        df_day_data = df_day_groupby.mean()
        df_day_data = df_day_data.reset_index()

        # create plots
        day_lines = alt.Chart(df_day_data).mark_line().encode(
            x=alt.X(field=file.TIME_START_LABEL, type="temporal", title=TIME_LABEL),
            y=alt.Y(field=file.VALUE_LABEL, type="quantitative", title=PRICE_LABEL),
            color=alt.Color(file.WEEKDAY_LABEL, sort=False)
        )


        day_points = alt.Chart(df_day_data).mark_point(size=POINT_SIZE/2).encode(
            x=alt.X(field=file.TIME_START_LABEL, type="temporal", title=TIME_LABEL, axis=alt.Axis(format='%H:%M', tickCount='hour')),
            y=alt.Y(field=file.VALUE_LABEL, type="quantitative", title=PRICE_LABEL),
            color=alt.Color(field=file.WEEKDAY_LABEL, sort=False),
            tooltip=[
                alt.Tooltip(field=file.WEEKDAY_LABEL, title="Day"),
                alt.Tooltip(filed=file.TIME_START_LABEL, title=TIME_LABEL, axis=alt.Axis(format='%H:%M', tickCount='hour')),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=".2f")
            ]
        )

        day_plot = [day_lines, day_points]


    # box plot
    if day_tabs.value == tab_box_plot_label:
        day_box_plot = alt.Chart(day_hourly_data).mark_boxplot(outliers=False).encode(
            x=alt.X(file.TIME_START_LABEL, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color=alt.Color(file.WEEKDAY_LABEL, sort=False, title="Day"),
        )

        day_plot = [day_box_plot]


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

    # total average
    total_hourly_data = data[[file.TIME_START_LABEL, file.VALUE_LABEL]].groupby(by=[file.TIME_START_LABEL])[file.VALUE_LABEL].mean()
    total_hourly_data = total_hourly_data.reset_index()


    total_line_plot = alt.Chart(total_hourly_data).transform_calculate(
            Legend="'Total average'",
        ).mark_line(strokeDash=[4,4]).encode(
            x=alt.X(file.TIME_START_LABEL, title=TIME_LABEL), 
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color = alt.Color("Legend:N",
                scale=alt.Scale(
                    range=["#e89c46"]
                    )
                )
            )
    date_range_plot.append(total_line_plot)


    # range values
    start_date, stop_date = date_selection.value
    start_date = str(start_date)
    stop_date = str(stop_date)

    df_range_hourly = data[data["Date"] >= start_date]
    df_range_hourly = df_range_hourly[df_range_hourly["Date"] <= stop_date]

    df_range_hourly_groupby = df_range_hourly[[file.TIME_START_LABEL, file.VALUE_LABEL]].groupby(by=[file.TIME_START_LABEL])[file.VALUE_LABEL]


    # line plot
    if date_range_tab.value == tab_line_label:
        df_date_range = df_range_hourly_groupby.mean()
        df_date_range = df_date_range.reset_index()

        # avg. line
        date_range_line_plot = alt.Chart(df_date_range).mark_line().encode(
            x=alt.X(file.TIME_START_LABEL, sort=False),
            y=alt.Y(file.VALUE_LABEL, PRICE_LABEL)
        )
        date_range_plot.append(date_range_line_plot)

        # points
        date_range_point_plot = alt.Chart(df_date_range).mark_point(size=POINT_SIZE).encode(
            x=alt.X(file.TIME_START_LABEL, sort=False, title=TIME_LABEL, axis=alt.Axis(format='%H:%M', tickCount='hour')),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            tooltip=[
                alt.Tooltip(file.TIME_START_LABEL, title=TIME_LABEL, axis=alt.Axis(format='%H:%M', tickCount='hour')),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL, format=".2f")
            ]
        )
        date_range_plot.append(date_range_point_plot)


    # box plot
    if date_range_tab.value == tab_box_plot_label:
        date_range_box_plot = alt.Chart(data).mark_boxplot(outliers=False).encode(
            x=alt.X(file.TIME_START_LABEL, sort=False, title=TIME_LABEL, axis=alt.Axis(format='%H:%M', tickCount='hour')),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL)
        )
        date_range_plot.append(date_range_box_plot)


    alt.layer(*date_range_plot)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
