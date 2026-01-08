import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import altair as alt

    import util.file as file
    import util.general as gen

    mo.md("# Dynamic electricity tariffs")
    return alt, file, gen, mo


@app.cell
def _(file):
    file_name = "data.json"
    data, dates = file.prepare_data(file_name)
    return data, dates


@app.cell
def _(dates, mo):
    PRICE_LABEL = "Price"
    MONTH_LABEL = "Month"
    TIME_LABEL = "Time"

    YEAR_POS = 4

    DECIMAL_POS = 2

    POINT_SIZE = 100

    # ui elements
    year_list = list(set([date[:YEAR_POS] for date in dates]))
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
    month_values = []
    curr_year = "2025"
    MONTH_FIRST_DAY = "01"
    MONTH_LAST_DAY = "31"
    year_plot = []

    _M_LABEL = "_month"
    M_LABEL = _M_LABEL[1:]

    # TODO: get available month indicies in the selected year
    # [!] month index is invalid with missing early months
    for m_index in range(len(gen.MONTH_LABELS)):
        month_str = str(m_index + 1).zfill(2)

        date_start = gen.DATE_SPEARATOR.join([curr_year, month_str, MONTH_FIRST_DAY])
        date_end = gen.DATE_SPEARATOR.join([curr_year, month_str, MONTH_LAST_DAY])

        month_value = file.get_date_range_data(data, dates, date_start, date_end)

        for m_value in month_value:
            m_value[_M_LABEL] = m_index
            m_value[M_LABEL] = gen.MONTH_LABELS[m_index]
            month_values.append(m_value)

    df_months = file.get_dataframe(month_values)


    # line plot
    if year_tab.value == tab_line_label:
        df_months = df_months.groupby([_M_LABEL, M_LABEL])[file.VALUE_LABEL].mean()
        df_months = df_months.reset_index()
        df_months = file.clean_dataframe(df_months, time_label=M_LABEL, decimal_pos=DECIMAL_POS)

         # average line
        year_line_plot = alt.Chart(df_months).mark_line().encode(
            x=alt.X(M_LABEL, sort=False, title=MONTH_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL)
        )
        year_plot.append(year_line_plot)

        # points with tooltip
        year_points = alt.Chart(df_months).mark_point(
            size=POINT_SIZE,
            filled=True
        ).encode(
            x=alt.X(M_LABEL, sort=None, title=MONTH_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            tooltip=[
                alt.Tooltip(M_LABEL, title=MONTH_LABEL),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL)
            ]
        )
        year_plot.append(year_points)


    # box plot
    if year_tab.value == tab_box_plot_label:
        df_months[file.VALUE_LABEL] = df_months[file.VALUE_LABEL].round(DECIMAL_POS)

        year_box_plot = alt.Chart(df_months).mark_boxplot(outliers=False).encode(
            x=alt.X(M_LABEL, sort=False, title=MONTH_LABEL),
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
    DECIMAL_POS,
    POINT_SIZE,
    PRICE_LABEL,
    TIME_LABEL,
    alt,
    data,
    dates,
    day_selection,
    day_tabs,
    file,
    gen,
    tab_box_plot_label,
    tab_line_label,
):
    day_plot = []

    day_indicies = [gen.get_index(gen.DAY_LABELS, day) for day in day_selection.value]
    day_data = file.get_day_data(data, dates, day_indicies)
    df_day_data = file.get_dataframe(day_data)

    df_day_data["_day"] = df_day_data.apply(lambda x: (gen.get_index(dates, x["date"]) % 7), axis=1)
    df_day_data["day"] = df_day_data.apply(lambda x: gen.DAY_LABELS[x["_day"]], axis=1)

    # avg line plot
    if day_tabs.value == tab_line_label:
        df_day_data = df_day_data.groupby(["_day", "day", file.TIME_LABEL])[file.VALUE_LABEL].mean()
        df_day_data = df_day_data.reset_index()
        df_day_data = file.clean_dataframe(df_day_data, decimal_pos=DECIMAL_POS)

        # create plots
        day_lines = alt.Chart(df_day_data).mark_line().encode(
            x=alt.X(file.TIME_LABEL, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color=alt.Color('day:N', sort=False)
        )


        day_points = alt.Chart(df_day_data).mark_point(size=POINT_SIZE/2).encode(
            x=alt.X(file.TIME_LABEL, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color=alt.Color('day:N', sort=False),
            tooltip=[
                alt.Tooltip("day:N", title="Day"),
                alt.Tooltip(file.TIME_LABEL, title=TIME_LABEL),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL)
            ]
        )

        day_plot = [day_lines, day_points]

    # box plot
    if day_tabs.value == tab_box_plot_label:
        df_day_data = file.clean_dataframe(df_day_data, decimal_pos=DECIMAL_POS)

        day_box_plot = alt.Chart(df_day_data).mark_boxplot(outliers=False).encode(
            x=alt.X(file.TIME_LABEL, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color=alt.Color('day:N', sort=False, title="Day"),
        )
        day_plot = [day_box_plot]
    return (day_plot,)


@app.cell
def _(alt, day_plot):
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
    DECIMAL_POS,
    POINT_SIZE,
    PRICE_LABEL,
    TIME_LABEL,
    alt,
    data,
    date_range_tab,
    date_selection,
    dates,
    file,
    tab_box_plot_label,
    tab_line_label,
):
    date_range_plot = []

    # total avg line
    total_avg_data = file.get_date_range_data(data, dates, dates[0], dates[-1])
    df_total_avg_data = file.get_dataframe(total_avg_data)

    df_avg_values = df_total_avg_data.groupby(file.TIME_LABEL)[file.VALUE_LABEL].mean()
    df_avg_values = df_avg_values.reset_index()
    df_avg_values = file.clean_dataframe(df_avg_values, decimal_pos=DECIMAL_POS)

    total_line_plot = alt.Chart(df_avg_values).transform_calculate(
            Legend="'Total average'",
        ).mark_line(strokeDash=[4,4]).encode(
            x=alt.X(file.TIME_LABEL, title=TIME_LABEL), 
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            color = alt.Color("Legend:N",
                scale=alt.Scale(
                    range=["#e89c46"]
                    )
                )
            )
    date_range_plot.append(total_line_plot)

    # get range data
    date_range_data = file.get_date_range_data(data, dates, str(date_selection.value[0]), str(date_selection.value[1]))
    df_date_range = file.get_dataframe(date_range_data)

    # line plot
    if date_range_tab.value == tab_line_label:
        df_date_range = df_date_range.groupby(file.TIME_LABEL)[file.VALUE_LABEL].mean()
        df_date_range = df_date_range.reset_index()
        df_date_range = file.clean_dataframe(df_date_range, decimal_pos=DECIMAL_POS)

        # avg. line
        date_range_line_plot = alt.Chart(df_date_range).mark_line().encode(
            x=alt.X(file.TIME_LABEL, sort=False),
            y=alt.Y(file.VALUE_LABEL, PRICE_LABEL)
        )
        date_range_plot.append(date_range_line_plot)

        # points
        date_range_point_plot = alt.Chart(df_date_range).mark_point(size=POINT_SIZE).encode(
            x=alt.X(file.TIME_LABEL, sort=False, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
            tooltip=[
                alt.Tooltip(file.TIME_LABEL, title=TIME_LABEL),
                alt.Tooltip(file.VALUE_LABEL, title=PRICE_LABEL)
            ]
        )
        date_range_plot.append(date_range_point_plot)


    # box plot
    if date_range_tab.value == tab_box_plot_label:
        df_date_range = file.clean_dataframe(df_date_range, decimal_pos=DECIMAL_POS)

        date_range_box_plot = alt.Chart(df_date_range).mark_boxplot(outliers=False).encode(
            x=alt.X(file.TIME_LABEL, sort=False, title=TIME_LABEL),
            y=alt.Y(file.VALUE_LABEL, title=PRICE_LABEL),
        )
        date_range_plot.append(date_range_box_plot)

    alt.layer(*date_range_plot)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
