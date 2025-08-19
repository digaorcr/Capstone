"""
SpaceX Launch Dashboard (Dash 3+)
— includes dropdown, pie chart, payload slider, and scatter plot
— keeps official component IDs required by the lab
"""

# 1) Imports
import os
import sys
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# 2) Data
CSV_PATH = "spacex_launch_dash.csv"
if not os.path.exists(CSV_PATH):
    sys.exit(f"ERROR: '{CSV_PATH}' not found in the current folder.")

df = pd.read_csv(CSV_PATH)
pmin = df["Payload Mass (kg)"].min()
pmax = df["Payload Mass (kg)"].max()

# 3) App
app = dash.Dash(__name__)
server = app.server  # for hosted environments

# 4) Layout
app.layout = html.Div(
    [
        html.H1("SpaceX Launch Records Dashboard", style={"textAlign": "center"}),

        # TASK 1 — Launch Site dropdown
        dcc.Dropdown(
            id="site-dropdown",
            options=[{"label": "All Sites", "value": "ALL"}]
            + [{"label": s, "value": s} for s in sorted(df["Launch Site"].unique())],
            value="ALL",
            placeholder="Select a Launch Site...",
            searchable=True,
            style={"width": "80%", "margin": "0 auto"},
        ),

        html.Br(),

        # Pie Chart
        dcc.Graph(id="success-pie-chart"),

        html.Br(),
        html.P("Payload range (Kg):", style={"textAlign": "center"}),

        # TASK 3 — Payload slider
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            marks={i: str(i) for i in range(0, 10001, 2500)},
            value=[pmin, pmax],
            tooltip={"placement": "bottom", "always_visible": True},
        ),

        html.Br(),

        # Scatter Plot
        dcc.Graph(id="success-payload-scatter-chart"),
    ],
    style={"maxWidth": 1100, "margin": "0 auto"},
)

# 5) Callbacks

# TASK 2 — Pie chart by site
@app.callback(Output("success-pie-chart", "figure"), Input("site-dropdown", "value"))
def update_pie(selected_site):
    if selected_site == "ALL":
        # Sum successes (class=1) per site
        fig = px.pie(
            df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site",
        )
    else:
        site_df = df[df["Launch Site"] == selected_site]
        outcome = (
            site_df["class"]
            .value_counts()
            .rename(index={0: "Failure", 1: "Success"})
            .reset_index()
            .rename(columns={"index": "Outcome", "class": "Count"})
        )
        fig = px.pie(
            outcome,
            values="Count",
            names="Outcome",
            title=f"Launch Outcomes for {selected_site}",
        )
    return fig

# TASK 4 — Scatter by site + payload
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter(selected_site, payload_range):
    lo, hi = payload_range
    mask = (df["Payload Mass (kg)"] >= lo) & (df["Payload Mass (kg)"] <= hi)
    data = df[mask]
    if selected_site != "ALL":
        data = data[data["Launch Site"] == selected_site]

    fig = px.scatter(
        data,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site"],
        labels={"class": "Launch Outcome (1=Success, 0=Failure)"},
        title=(
            "Correlation between Payload and Success for All Sites"
            if selected_site == "ALL"
            else f"Correlation between Payload and Success for {selected_site}"
        ),
    )
    return fig

# 6) Run (Dash 3)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
