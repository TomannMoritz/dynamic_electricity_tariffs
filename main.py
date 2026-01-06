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
def _(alt, data, dates, file, gen, mo):
    # year overview
    month_values = file.get_avg_month_values(data, dates, "2025")
    month_labels = gen.MONTH_LABELS[0:len(month_values)]

    price_label = "Avg electricity tariffs in €"
    month_label = "Months"
    df_months, _, _ = file.create_dataframe(month_values, month_labels, price_label, month_label)

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
    return (day_selection,)


@app.cell
def _(alt, data, dates, day_selection, file, gen, mo):
    day_results = []

    for day in day_selection.value:
        day_indicies = [gen.get_index(gen.DAY_LABELS, day)]
        day_result = file.get_avg_hour_values(data, dates, day_indicies)
        day_results.append(day_result)

    df_results = []
    if len(day_results) != 0:
        for v in range(len(day_results[0]["value"])):
            result = {"Hour": day_results[0]["label"][v][:-4]}

            for i, day in enumerate(day_results):
                result[day_selection.value[i]] = day["value"][v].round(3)

            df_results.append(result)

    day_df = file.get_dataframe(df_results)

    # create plots
    day_lines = alt.Chart(day_df).mark_line().transform_fold(
        fold=day_selection.value,
        as_=["Day", "Price"],
    ).encode(
        x='Hour',
        y='Price:Q',
        color=alt.Color('Day:N', sort=False)
    )

    day_points = alt.Chart(day_df).mark_point().transform_fold(
        fold=day_selection.value,
        as_=["Day", "Price"]
    ).encode(
        x='Hour',
        y='Price:Q',
        color=alt.Color('Day:N', sort=False),
        tooltip=["Day:N", "Price:Q"]
    )

    mo.vstack([
        mo.md("## Average hourly tariffs"),
        day_selection,
    ])
    return day_lines, day_points


@app.cell
def _(alt, day_lines, day_points):
    alt.layer(day_lines, day_points)
    return


if __name__ == "__main__":
    app.run()
