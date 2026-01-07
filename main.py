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
def _():
    price_label = "Price"
    month_label = "Month"
    hour_label = "Hour"
    return hour_label, month_label, price_label


@app.cell
def _(alt, data, dates, file, gen, mo, month_label, price_label):
    # year overview
    month_values = file.get_avg_month_values(data, dates, "2025")
    month_labels = gen.MONTH_LABELS[0:len(month_values)]

    df_months = file.dict_to_dataframe({price_label: month_values, month_label: month_labels})

    # altair: create line and point plot
    year_line = alt.Chart(df_months).mark_line().encode(x=alt.X(month_label, sort=None), y=price_label)
    year_points = alt.Chart(df_months).mark_point(size=200, filled=True).encode(x=alt.X(month_label, sort=None), y=price_label, tooltip=[price_label])

    mo.vstack([
        mo.md("## Average monthly tariffs in 2025"),
        year_line + year_points
    ])
    return


@app.cell
def _(gen, mo):
    day_selection = mo.ui.multiselect(options=gen.DAY_LABELS, value=gen.DAY_LABELS, label="Select days: ")

    mo.vstack([
        mo.md("## Average hourly tariffs - Days"),
        day_selection,
    ])
    return (day_selection,)


@app.cell
def _(alt, data, dates, day_selection, file, gen, hour_label, price_label):
    day_results = {}

    for day in day_selection.value:
        day_indicies = [gen.get_index(gen.DAY_LABELS, day)]
        day_result = file.get_avg_hour_values(data, dates, day_indicies)
        day_results[day] = day_result["value"]
        day_results[hour_label] = day_result["label"]

    df_day = file.dict_to_dataframe(day_results)

    # create plots
    day_lines = alt.Chart(df_day).mark_line().transform_fold(
        fold=day_selection.value,
        as_=["Day", price_label],
    ).encode(
        x=f'{hour_label}',
        y=f'{price_label}:Q',
        color=alt.Color('Day:N', sort=False)
    )

    day_points = alt.Chart(df_day).mark_point().transform_fold(
        fold=day_selection.value,
        as_=["Day", price_label]
    ).encode(
        x=f'{hour_label}',
        y=f'{price_label}:Q',
        color=alt.Color('Day:N', sort=False),
        tooltip=["Day:N", f"{price_label}:Q", f"{hour_label}"]
    )
    return day_lines, day_points


@app.cell
def _(alt, day_lines, day_points):
    alt.layer(day_lines, day_points)
    return


@app.cell
def _(dates, mo):
    date_selection = mo.ui.date_range(start=dates[0], stop=dates[-1])

    mo.vstack([
        mo.md("## Hourly tariffs - Date Range"),
        date_selection,
    ])
    return (date_selection,)


@app.cell
def _(alt, data, date_selection, dates, file, gen, hour_label, price_label):
    # create total avg line
    total_avg_hourly = file.get_avg_hour_values(data, dates, [day_i  for day_i in range(len(gen.DAY_LABELS))])
    total_avg_hourly[price_label] = total_avg_hourly["value"]
    total_avg_hourly[hour_label] = total_avg_hourly["label"]

    df_total_avg_hourly = file.dict_to_dataframe(total_avg_hourly)
    total_avg_line = alt.Chart(df_total_avg_hourly).transform_calculate(
            Legend="'Total average'",
        ).mark_line(strokeDash=[4,4]).encode(
            x=hour_label, 
            y=price_label,
            color = alt.Color("Legend:N",
                scale=alt.Scale(
                    range=["#e89c46"]
                    )
                )
            )


    # create hourly box plots
    date_min = str(date_selection.value[0])
    date_max = str(date_selection.value[1])

    range_dates = [date for date in dates if date >= date_min and date <= date_max]
    range_data = file.get_filtered_data(data, range_dates)
    range_results = file.get_price_data(range_data)

    range_box_plots = []

    for a in range(len(range_results["price"])):
        df_selected_dates = file.get_dataframe({
            price_label: range_results["price"][a],
            hour_label: range_results["label"][a]
        })

        new_plot = alt.Chart(df_selected_dates).mark_boxplot(outliers=False).encode(
            x=alt.X(hour_label, sorted=False),
            y=price_label
        )

        range_box_plots.append(new_plot)

    total_avg_line + alt.layer(*range_box_plots)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
