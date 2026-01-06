import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    import altair as alt

    import util.file as file
    import util.time as time

    mo.md("# Dynamic electricity tariffs")
    return alt, file


@app.cell
def _(file):
    file_name = "data.json"
    data, dates = file.prepare_data(file_name)

    MONTH_LABELS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    return MONTH_LABELS, data, dates


@app.cell
def _(MONTH_LABELS, alt, data, dates, file):
    # year overview
    month_values = file.get_avg_month_values(data, dates, "2025")
    month_labels = MONTH_LABELS[0:len(month_values)]

    price_label = "Avg electricity tariffs in €"
    month_label = "Months"
    df_months, _, _ = file.create_dataframe(month_values, month_labels, price_label, month_label)

    # altair: create line and point plot
    year_line = alt.Chart(df_months).mark_line().encode(x=alt.X(month_label, sort=None), y=price_label)
    year_points = alt.Chart(df_months).mark_point(size=200, filled=True).encode(x=alt.X(month_label, sort=None), y=price_label, tooltip=[price_label])

    year_line + year_points
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
