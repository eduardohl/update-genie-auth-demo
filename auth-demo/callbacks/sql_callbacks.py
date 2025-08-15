import dash
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, html

from auth import cfg, get_connection_obo, get_connection_sp
from sql import run_query


@callback(
    [
        Output("table-output-sp", "data"),
        Output("table-output-sp", "columns"),
        Output("table-output-sp", "tooltip_data"),
        Output("alert-sp", "children"),
        Output("alert-sp", "color"),
        Output("alert-sp", "hide"),
        Output("alert-sp", "title"),
        Output("table-container-sp", "style"),
        Output("loading-overlay-sp", "visible"),
        Output("run-query-sp", "loading"),
    ],
    Input("run-query-sp", "n_clicks"),
    State("sql-http-path", "value"),
    State("table-name-input", "value"),
    running=[
        (Output("run-query-sp", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def run_sp_query_callback(n_clicks, http_path, table_name):
    container_style = {"display": "none"}
    loading_visible = False

    if not n_clicks or not http_path or not table_name:
        return dash.no_update + (False, False)

    if not cfg:
        return (
            [],
            [],
            [],
            [
                "Error: Databricks SDK not configured. Check environment variables like ",
                dmc.InlineCodeHighlight(code="DATABRICKS_HOST"),
                " etc.",
            ],
            "red",
            False,
            "Configuration Error",
            container_style,
            False,
            False,
        )

    loading_visible = True

    alert_hide = False

    try:
        conn = get_connection_sp(http_path)
        df = run_query(table_name, conn)
        conn.close()
        loading_visible = False

        if not df.empty:
            data = df.to_dict("records")
            columns = [{"name": i, "id": i} for i in df.columns]
            tooltips = [
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in data
            ]
            alert_msg = [
                "Success! Fetched ",
                html.B(f"{len(df)}"),
                " rows from ",
                dmc.Code(f"{table_name}"),
                " using the service principal's permissions.",
            ]
            alert_color = "green"
            alert_title = "Success"
            container_style = {"display": "block"}
            return (
                data,
                columns,
                tooltips,
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )
        else:
            alert_msg = [
                "Query ran successfully using Service Principal but returned no data from ",
                dmc.Code(f"'{table_name}'"),
                ".",
            ]
            alert_color = "yellow"
            alert_title = "No Data"
            container_style = {"display": "block"}
            return (
                [],
                [],
                [],
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )

    except Exception as e:
        alert_msg = [
            "Error running query with Service Principal: ",
            dmc.Code(str(e)),
        ]
        alert_color = "red"
        alert_title = "Error"
        container_style = {"display": "block"}
        return (
            [],
            [],
            [],
            alert_msg,
            alert_color,
            alert_hide,
            alert_title,
            container_style,
            False,
            False,
        )


@callback(
    [
        Output("table-output-obo", "data"),
        Output("table-output-obo", "columns"),
        Output("table-output-obo", "tooltip_data"),
        Output("alert-obo", "children"),
        Output("alert-obo", "color"),
        Output("alert-obo", "hide"),
        Output("alert-obo", "title"),
        Output("table-container-obo", "style"),
        Output("loading-overlay-obo", "visible"),
        Output("run-query-obo", "loading"),
    ],
    Input("run-query-obo", "n_clicks"),
    State("sql-http-path", "value"),
    State("table-name-input", "value"),
    State("obo-token-store", "data"),
    running=[
        (Output("run-query-obo", "loading"), True, False),
    ],
    prevent_initial_call=True,
)
def run_obo_query_callback(n_clicks, http_path, table_name, obo_data):
    container_style = {"display": "none"}
    loading_visible = False

    if not n_clicks or not http_path or not table_name:
        return dash.no_update + (False, False)

    if not obo_data or not obo_data.get("token"):
        return (
            [],
            [],
            [],
            [
                "Error: No OBO token available. Cannot run query using your identity.",
            ],
            "red",
            False,
            "No OBO Token",
            container_style,
            False,
            False,
        )

    loading_visible = True

    alert_hide = False

    try:
        conn = get_connection_obo(http_path)
        df = run_query(table_name, conn)
        conn.close()
        loading_visible = False

        if not df.empty:
            data = df.to_dict("records")
            columns = [{"name": i, "id": i} for i in df.columns]
            tooltips = [
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in data
            ]
            alert_msg = [
                "Success! Fetched ",
                html.B(f"{len(df)}"),
                " rows from ",
                dmc.Code(f"{table_name}"),
                " using your OBO identity.",
            ]
            alert_color = "green"
            alert_title = "Success"
            container_style = {"display": "block"}
            return (
                data,
                columns,
                tooltips,
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )
        else:
            alert_msg = [
                "Query ran successfully using OBO but returned no data from ",
                dmc.Code(f"'{table_name}'"),
                ".",
            ]
            alert_color = "yellow"
            alert_title = "No Data"
            container_style = {"display": "block"}
            return (
                [],
                [],
                [],
                alert_msg,
                alert_color,
                alert_hide,
                alert_title,
                container_style,
                loading_visible,
                False,
            )

    except Exception as e:
        alert_msg = [
            "Error running query with OBO: ",
            dmc.Code(str(e)),
        ]
        alert_color = "red"
        alert_title = "Error"
        container_style = {"display": "block"}
        return (
            [],
            [],
            [],
            alert_msg,
            alert_color,
            alert_hide,
            alert_title,
            container_style,
            False,
            False,
        )
