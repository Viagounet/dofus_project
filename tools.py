import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from PIL import Image

image_path = "img_1.png"  # Replace with your image path

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

image = Image.open(image_path)
width, height = image.size

fig = px.imshow(image, binary_format="png")
fig.update_xaxes(showgrid=False, visible=False)
fig.update_yaxes(showgrid=False, visible=False, scaleanchor="x")
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), clickmode="event+select")

fig.add_trace(
    go.Scatter(
        x=[],
        y=[],
        mode="markers",
        marker=dict(size=8, color="red"),
        showlegend=False,
    )
)

fig.add_trace(
    go.Scatter(
        x=[],
        y=[],
        mode="lines",
        line=dict(color="blue"),
        showlegend=False,
    )
)

app.layout = dbc.Container(
    [
        html.H1("Click on the Image to Add Dots"),
        dcc.Graph(
            id="clickable-image",
            figure=fig,
            config={"displayModeBar": False},
        ),
        html.Div([html.Button("Link Selected Points", id="link-button", n_clicks=0),
                  html.Button("Export", id="export-button", n_clicks=0)],
                 className="d-flex flex-row"),

        dcc.Store(data=[], id="stored-links"),
        dcc.Store(data={}, id="points-names"),
        html.Div([], id="point-inputs"),
        html.Hr(),
        html.Div([], id="segments-inputs")
    ],
    fluid=True
)

from dash.dependencies import Input, Output, State, ALL

import json


def export_to_json(n_clicks, point_names, figure, stored_links, orientations):
    if n_clicks == 0:
        return n_clicks  # Ignore the initial callback

    points_data = {name: [x, y]
                   for name, x, y in zip(point_names, figure["data"][1]["x"], figure["data"][1]["y"])
                   }
    orientation_dictionnary = {"1": "start_to_end",
                               "2": "bidirectional",
                               "3": "end_to_start"}
    links_data = [
        {
            "start_point": get_point_name(x0, y0, point_names, figure["data"][1]),
            "end_point": get_point_name(x1, y1, point_names, figure["data"][1]),
            "coordinates": [(x0, y0), (x1, y1)],
            "orientation": orientation_dictionnary[orientation]
        }
        for ((x0, y0), (x1, y1)), orientation in zip(stored_links, orientations)
    ]

    data = {
        "points": points_data,
        "links": links_data,
    }

    with open("10_-19.json", "w") as f:
        json.dump(data, f, indent=2)

    return n_clicks


def get_point_name(x, y, point_names, figure_data):
    index = -1
    for i, (x_point, y_point) in enumerate(zip(figure_data["x"], figure_data["y"])):
        if x_point == x and y_point == y:
            index = i
            break

    if index >= 0 and index < len(point_names) and point_names[index] is not None:
        return point_names[index]

    return f"({x}, {y})"


@app.callback(
    [Output("clickable-image", "figure"),
     Output("stored-links", "data"),
     Output("point-inputs", "children"),
     Output("segments-inputs", "children")],
    Input("clickable-image", "clickData"),
    Input("clickable-image", "selectedData"),
    Input("link-button", "n_clicks"),
    State("clickable-image", "figure"),
    State("stored-links", "data"),
    State("point-inputs", "children"),
    State("segments-inputs", "children"),
    State({"type": "point-name-input", "index": ALL}, "value")
)
def update_figure_and_inputs(click_data, selected_data, n_clicks, figure, stored_links, point_inputs, segment_inputs,
                             point_names):
    ctx = dash.callback_context
    if not ctx.triggered:
        return figure, stored_links, point_inputs, segment_inputs
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "clickable-image":
        if click_data is not None:
            x_click = click_data["points"][0]["x"]
            y_click = click_data["points"][0]["y"]

            # Adding the dot if it's not already present in the figure data
            if x_click not in figure["data"][1]["x"] or y_click not in figure["data"][1]["y"]:
                figure["data"][1]["x"].append(x_click)
                figure["data"][1]["y"].append(y_click)

                # Create a new InputGroup for the added point and append it to the point_inputs
                new_input_group = dbc.InputGroup(
                    [
                        dbc.Input(id={"type": "point-name-input",
                                      "index": f"point-name-{len(figure['data'][1]['x'])}"},
                                  placeholder="Enter point name",
                                  type="text"),
                        html.Div(f"({x_click:.2f}, {y_click:.2f})"),
                    ],
                    className="mb-3",
                )

                point_inputs.append(new_input_group)


    elif trigger_id == "link-button":

        if selected_data is not None and len(selected_data["points"]) == 2:

            x0, y0 = selected_data["points"][0]["x"], selected_data["points"][0]["y"]

            x1, y1 = selected_data["points"][1]["x"], selected_data["points"][1]["y"]

            stored_links.append([(x0, y0), (x1, y1)])

            figure["data"][2]["x"].extend([x0, x1, None])
            figure["data"][2]["y"].extend([y0, y1, None])

            point1_name = get_point_name(x0, y0, point_names, figure["data"][1])
            point2_name = get_point_name(x1, y1, point_names, figure["data"][1])
            link_select = dbc.Select(
                id={"type": "link-orient",
                    "index": f"select-{point1_name}-{point2_name}"},
                options=[
                    {"label": "->", "value": "1"},
                    {"label": "<->", "value": "2"},
                    {"label": "<-", "value": "3"},
                ],
                value="2"
            )
            new_input_group = html.Div([
                html.Div(point1_name), link_select, html.Div(point2_name)
            ], className="d-flex flex-row gap-2")

            segment_inputs.append(new_input_group)
        else:
            print("You must select only 2 points.")

    return figure, stored_links, point_inputs, segment_inputs


@app.callback(
    Output("export-button", "n_clicks"),
    Input("export-button", "n_clicks"),
    State({"type": "point-name-input", "index": ALL}, "value"),
    State("clickable-image", "figure"),
    State("stored-links", "data"),
    State({"type": "link-orient", "index": ALL}, "value"),
)
def handle_export_button(n_clicks, point_names, figure, stored_links, orientations):
    return export_to_json(n_clicks, point_names, figure, stored_links, orientations)


if __name__ == "__main__":
    app.run_server(debug=True)
