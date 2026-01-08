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
def _(dates, file, mo):
    PRICE_LABEL = "Price"
    MONTH_LABEL = "Month"
    TIME_LABEL = "Time"

    POINT_SIZE = 100

    # ui elements
    year_list = list(set([date[:file.YEAR_POS] for date in dates]))
    year_selection = mo.ui.dropdown(options=year_list, value=year_list[0], label="Select year: ")

    tab_line_label = "Avg price"
    tab_box_plot_label = "Box plot"
    year_tab = mo.ui.tabs({
        tab_line_label: "",
        tab_box_plot_label: ""
    })
    return (
        MONTH_LABEL,
        POINT_SIZE,
        PRICE_LABEL,
        tab_box_plot_label,
        tab_line_label,
        year_selection,
        year_tab,
    )


@app.cell
def _(
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

    for m_index in range(len(gen.MONTH_LABELS)):
        month_str = str(m_index + 1).zfill(2)

        date_start = gen.DATE_SPEARATOR.join([curr_year, month_str, MONTH_FIRST_DAY])
        date_end = gen.DATE_SPEARATOR.join([curr_year, month_str, MONTH_LAST_DAY])
        month_value = file.get_date_range_data(data, dates, date_start, date_end)
        collected_values = [value["value"] for value in month_value]

        month_values.append(collected_values)


    # line plot
    if year_tab.value == tab_line_label:
        df_avg_collect = file.dict_to_dataframe({
            MONTH_LABEL: [gen.MONTH_LABELS[year_line_index] for year_line_index in range(len(month_values))],
            PRICE_LABEL: [sum(year_line_values) / len(year_line_values) for year_line_values in month_values]
        })

        year_line_plot = alt.Chart(df_avg_collect).mark_line().encode(x=alt.X(MONTH_LABEL, sort=False), y=PRICE_LABEL)
        year_plot.append(year_line_plot)

        year_points = alt.Chart(df_avg_collect).mark_point(size=POINT_SIZE, filled=True).encode(x=alt.X(MONTH_LABEL, sort=None), y=PRICE_LABEL, tooltip=[PRICE_LABEL, MONTH_LABEL])
        year_plot.append(year_points)



    # box plot
    if year_tab.value == tab_box_plot_label:
        for box_index, box_values in enumerate(month_values):

            df_collect = file.dict_to_dataframe({
                MONTH_LABEL: [gen.MONTH_LABELS[box_index] for _ in range(len(box_values))],
                PRICE_LABEL: box_values
            })

            year_box_plot = alt.Chart(df_collect).mark_boxplot(outliers=False).encode(x=alt.X(MONTH_LABEL, sort=False), y=PRICE_LABEL)
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
        df_day_data = df_day_data.groupby(["_day", "day", "time"])["value"].mean()
        df_day_data = df_day_data.reset_index()

        # create plots
        day_lines = alt.Chart(df_day_data).mark_line().encode(
        x="time",
        y=f'value:Q',
        color=alt.Color('day:N', sort=False)
        )


        day_points = alt.Chart(df_day_data).mark_point(size=POINT_SIZE/2).encode(
        x=f'time',
        y=f'value:Q',
        color=alt.Color('day:N', sort=False),
        tooltip=["day:N", f"value:Q", f"time"]
        )

        day_plot = [day_lines, day_points]

    # box plot
    if day_tabs.value == tab_box_plot_label:
        day_box_plot = alt.Chart(df_day_data).mark_boxplot(outliers=False).encode(
            x="time",
            y=f'value:Q',
            color=alt.Color('day:N', sort=False)
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
    POINT_SIZE,
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

    df_avg_values = df_total_avg_data.groupby(file.TIME_LABEL)["value"].mean()
    df_avg_values = df_avg_values.reset_index()

    total_line_plot = alt.Chart(df_avg_values).transform_calculate(
            Legend="'Total average'",
        ).mark_line(strokeDash=[4,4]).encode(
            x=file.TIME_LABEL, 
            y="value",
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
        df_date_range = df_date_range.groupby(file.TIME_LABEL)["value"].mean()
        df_date_range = df_date_range.reset_index()
    

        date_range_line_plot = alt.Chart(df_date_range).mark_line().encode(x=alt.X(file.TIME_LABEL, sort=False), y="value")
        date_range_plot.append(date_range_line_plot)

        date_range_point_plot = alt.Chart(df_date_range).mark_point(size=POINT_SIZE).encode(x=alt.X(file.TIME_LABEL, sort=False), y="value", tooltip=[file.TIME_LABEL, "value"])
        date_range_plot.append(date_range_point_plot)


    # box plot
    if date_range_tab.value == tab_box_plot_label:
        date_range_box_plot = alt.Chart(df_date_range).mark_boxplot(outliers=False).encode(x=alt.X(file.TIME_LABEL, sort=False), y="value")
        date_range_plot.append(date_range_box_plot)


    alt.layer(*date_range_plot)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
