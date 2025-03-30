import dash
from dash import html, dcc
import dash_mantine_components as dmc

dash.register_page(
    module=__name__,
    name="Edit a table",
    path="/tables/edit",
    category="tables",
)

layout = html.Div(
    [
        dmc.Title("Edit a table", order=1),
    ],
    style={"padding": "20px"},
)
