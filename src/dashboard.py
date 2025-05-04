import base64
import io
import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html
from dash.dependencies import Input, Output, State
from advanced_data_loader import load_excel_tabs, process_platemap, process_microscopy_data
import numpy as np

# Initialize Dash app with the MATERIA theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MATERIA])  # Changed theme to MATERIA

# Define the Navbar
navbar = dbc.NavbarSimple(
    children=[],
    brand="Live Cell Imaging Dashboard",
    brand_href="#",  # Link to home or refresh
    color="dark",  # Use a dark background for the navbar
    dark=True,  # Set to True for light text on dark background
    sticky="top",  # Makes the navbar stick to the top when scrolling
    fluid=True,  # Make the navbar span the full width of the page
    className="mb-4"  # Add bottom margin for spacing
)

# Define the control card
control_card = dbc.Card(
    [
        dbc.CardHeader("Controls"), # Optional: Adds a header to the card
        dbc.CardBody(
            [
                # File Upload Component (Moved here)
                dcc.Upload(
                    id="upload-data",
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Excel File') # More conventional text
                    ]),
                    style={ # Basic styling for the upload zone
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin-bottom': '10px'
                    },
                    multiple=False
                ),
                # Use dbc.Alert for status messages for better styling
                dbc.Alert(id="upload-status", color="info", dismissable=True, is_open=False), # Start closed

                # Accordion for selection options
                dbc.Accordion(
                    [
                        dbc.AccordionItem(
                            [
                                # Removed the Label, RadioItems usually suffice
                                dcc.RadioItems(
                                    id="data_type_selector",
                                    options=[
                                        {"label": "Phase", "value": "phase"},
                                        {"label": "Green", "value": "green"},
                                        {"label": "Red", "value": "red"},
                                        {"label": "Green/Red Ratio", "value": "ratio"}
                                    ],
                                    value="phase",
                                    inputStyle={"marginRight": "5px"},
                                    labelStyle={'display': 'block', 'marginBottom': '5px'} # Style labels
                                )
                            ], title="Data Type", item_id="item-data-type" # Added item_id
                        ),
                        dbc.AccordionItem(
                            [
                                # Removed the Label
                                dcc.Checklist(
                                    id="treatment_selector",
                                    inputStyle={"marginRight": "5px"},
                                    labelStyle={'display': 'block', 'marginBottom': '5px'} # Style labels
                                 )
                            ], title="Treatments", item_id="item-treatments" # Added item_id
                        ),
                        dbc.AccordionItem(
                            [
                                # Removed the Label
                                dcc.Checklist(
                                    id="celltype_selector",
                                    inputStyle={"marginRight": "5px"},
                                    labelStyle={'display': 'block', 'marginBottom': '5px'} # Style labels
                                )
                            ], title="Cell Types", item_id="item-cell-types" # Added item_id
                        ),
                    ],
                    # active_item="item-treatments", # Use item_id here
                    always_open=True, # Optional: Keep multiple sections open
                    className="mb-3" # Margin below accordion
                ),

                # Export Format Dropdown (Moved here)
                dbc.Label("Select Export Format:", html_for="export_format_selector", className="fw-bold"),
                dcc.Dropdown(
                    id="export_format_selector",
                    options=[
                        {"label": "SVG", "value": "svg"},
                        {"label": "PNG", "value": "png"}
                    ],
                    value="svg",
                    clearable=False
                ),
                dbc.Label("Export Filename:", html_for="export_filename_input", className="fw-bold mt-3"),
                dcc.Input(
                    id="export_filename_input",
                    type="text",
                    placeholder="Enter filename",
                    value="custom_image",  # Default filename
                    debounce=True,  # Update value only when the user stops typing
                    style={"width": "100%"}
                )
            ]
        )
    ],
    className="mb-4" # Margin below the card
)

# Update the layout with improved scrolling behavior
app.layout = html.Div(
    style={
        "height": "100vh",  # Full viewport height
        "overflow": "auto",  # Allow scrolling when needed
        "display": "flex",  # Use flexbox for layout
        "flexDirection": "column",  # Stack elements vertically
        "margin": "0",  # Remove default margins
        "padding": "0",  # Remove default padding
    },
    children=[
        navbar,
        dbc.Container(
            [
                dcc.Store(id='stored-data'),  # For sheets data
                dcc.Store(id='processed-data'),  # For processed treatments and celltypes
                dbc.Row(
                    [
                        # Sidebar column
                        dbc.Col(
                            [
                                dbc.Button(
                                    id="toggle-sidebar",
                                    color="light",  # Use a light button to contrast with the dark background
                                    className="mb-3",
                                    n_clicks=0,
                                    style={"width": "100%", "marginTop": "10px"}  # Add margin at the top
                                ),
                                html.Div(
                                    id="sidebar-content",
                                    children=control_card,  # Default: show the control card
                                    style={"width": "100%"}
                                )
                            ],
                            id="sidebar",
                            width=3,  # Default width when open
                            style={
                                "transition": "width 0.3s ease",
                                "height": "100vh",  # Make the sidebar span the full height of the viewport
                                "padding": "10px",  # Restore padding for better spacing
                                "margin": "0",  # Remove external margins
                                "overflow": "auto",  # Allow scrolling within the sidebar if needed
                            }
                        ),
                        # Main content column
                        dbc.Col(
                            [
                                dbc.Tabs(
                                    id="graph_tabs",
                                    active_tab="individual",
                                    children=[
                                        dbc.Tab(label="Individual", tab_id="individual"),
                                        dbc.Tab(label="Multi Plot", tab_id="multi_plot"),
                                        dbc.Tab(label="Heatmaps", tab_id="heatmaps"),  # Move Heatmaps to the third position
                                        dbc.Tab(label="Diagnostics", tab_id="diagnostics")  # Move Diagnostics to the last position
                                    ],
                                    className="mb-3"
                                ),
                                dbc.Spinner(html.Div(id="graph_content"))
                            ],
                            id="main-content",
                            width=9,  # Default width when sidebar is open
                            style={"transition": "width 0.3s ease"}  # Smooth transition for width changes
                        )
                    ]
                )
            ],
            fluid=True,
            style={"flex": "1", "overflow": "auto"}  # Allow scrolling when needed
        )
    ]
)

# Callback to toggle the sidebar
@app.callback(
    [Output("sidebar", "width"),
     Output("main-content", "width"),
     Output("sidebar-content", "style"),
     Output("toggle-sidebar", "children")],
    Input("toggle-sidebar", "n_clicks"),
    State("sidebar", "width")
)
def toggle_sidebar(n_clicks, sidebar_width):
    if n_clicks % 2 == 1:  # Odd clicks: collapse the sidebar
        return 1, 11, {"display": "none"}, ">>"  # Hide contents, show minimal button
    else:  # Even clicks: expand the sidebar
        return 3, 9, {"display": "block"}, "Hide Controls"  # Show contents, restore button text

@app.callback(
    [Output("upload-status", "children"),
     Output("upload-status", "color"),
     Output("upload-status", "is_open"),
     Output("treatment_selector", "options"),
     Output("celltype_selector", "options"),
     Output("treatment_selector", "value"),
     Output("celltype_selector", "value"),
     Output("stored-data", "data"),  # New output for sheets
     Output("processed-data", "data")],  # New output for processed data
    Input("upload-data", "contents"),
    State("upload-data", "filename")
)
def load_file(contents, filename):
    if contents is None:
        return dash.no_update, dash.no_update, False, \
               dash.no_update, dash.no_update, dash.no_update, \
               dash.no_update, dash.no_update, dash.no_update

    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    file_io = io.BytesIO(decoded)

    try:
        # Load data
        sheets = load_excel_tabs(file_io)
        
        # Process treatments and cell types
        treatments = process_platemap(sheets.get("treatments"), "Treatment") if "treatments" in sheets else pd.DataFrame()
        celltypes = process_platemap(sheets.get("celltypes"), "Cell type") if "celltypes" in sheets else pd.DataFrame()

        available_treatments = sorted(treatments["Treatment"].dropna().unique()) if not treatments.empty else []
        available_celltypes = sorted(celltypes["Cell type"].dropna().unique()) if not celltypes.empty else []

        # Convert DataFrames to dictionaries for storage
        stored_sheets = {name: df.to_dict('split') for name, df in sheets.items()}
        processed_data = {
            'treatments': treatments.to_dict('split'),
            'celltypes': celltypes.to_dict('split')
        }

        return (
            f"File '{filename}' uploaded successfully!",  # message
            "success",  # color
            True,  # is_open
            [{"label": t, "value": t} for t in available_treatments],  # treatment options
            [{"label": c, "value": c} for c in available_celltypes],  # celltype options
            available_treatments[:1],  # selected treatment
            available_celltypes[:1],  # selected celltype
            stored_sheets,  # stored sheets data
            processed_data  # processed data
        )

    except Exception as e:
        return (
            f"Error processing file: {str(e)}",
            "danger",
            True,
            [], [], [], [],
            None, None
        )


# Callback to update the content of the tabs
@app.callback(
    Output("graph_content", "children"),
    [
        Input("graph_tabs", "active_tab"),
        Input("treatment_selector", "value"),
        Input("celltype_selector", "value"),
        Input("data_type_selector", "value"),
        Input("export_format_selector", "value"),
        Input("export_filename_input", "value"),
        Input("stored-data", "data"),
        Input("processed-data", "data")
    ]
)
def update_graph(active_tab, selected_treatments, selected_celltypes, selected_data_type, export_format, export_filename, stored_data, processed_data):
    if not stored_data or not processed_data:
        return html.P("Please upload data first.")

    # Convert stored data back to DataFrames
    sheets = {name: pd.DataFrame(data=df_dict['data'], columns=df_dict['columns'], index=df_dict['index']) 
              for name, df_dict in stored_data.items()}
    treatments = pd.DataFrame(data=processed_data['treatments']['data'], 
                              columns=processed_data['treatments']['columns'], 
                              index=processed_data['treatments']['index'])
    celltypes = pd.DataFrame(data=processed_data['celltypes']['data'], 
                             columns=processed_data['celltypes']['columns'], 
                             index=processed_data['celltypes']['index'])

    if active_tab == "individual":
        return create_individual_plot(selected_treatments, selected_celltypes, selected_data_type, 
                                      export_format, export_filename, sheets, treatments, celltypes)
    elif active_tab == "multi_plot":
        return create_multi_plot(selected_treatments, selected_celltypes, selected_data_type, 
                                 export_format, export_filename, sheets, treatments, celltypes)
    elif active_tab == "diagnostics":
        return create_diagnostics_content(sheets)
    elif active_tab == "heatmaps":
        return create_heatmap(selected_treatments, selected_celltypes, selected_data_type, sheets, treatments, celltypes, export_format, export_filename)

    return html.P("Select a tab.")

def generate_plot(data_type, selected_treatments, selected_celltypes, export_format, export_filename, sheets, treatments, celltypes, is_multi_plot=False):
    # Load data
    data_files = {
        "phase": process_microscopy_data(sheets["phase"]) if "phase" in sheets else None,
        "green": process_microscopy_data(sheets["green"]) if "green" in sheets else None,
        "red": process_microscopy_data(sheets["red"]) if "red" in sheets else None,
    }

    # Compute ratio if needed
    if "green" in sheets and "red" in sheets:
        data_files["ratio"] = data_files["green"] / data_files["red"]

    y_axis_titles = {
        "phase": "Confluence (%)",
        "green": "Green Fluorescence (AU)",
        "red": "Red Fluorescence (AU)",
        "ratio": "Green/Red Fluorescence Ratio"
    }
    graph_titles = {
        "phase": "Confluence Over Time",
        "green": "Green Fluorescence Over Time",
        "red": "Red Fluorescence Over Time",
        "ratio": "Green/Red Fluorescence Ratio Over Time"
    }

    config = {
        'toImageButtonOptions': {
            'format': export_format,
            'filename': export_filename,
            'scale': 2
        }
    }

    def create_plot(data_type):
        df = data_files.get(data_type)
        if df is None:
            return go.Figure(layout_title_text=f"No data available for {data_type}")

        # Compute ratio if needed
        if data_type == "ratio":
            green_df = data_files.get("green")
            red_df = data_files.get("red")
            if green_df is None or red_df is None:
                return go.Figure(layout_title_text="Green or Red data missing for Ratio calculation")
            red_df_safe = red_df.replace(0, np.nan)
            df = green_df / red_df_safe

        # Reshape and merge data
        df = df.reset_index().melt(id_vars=["Time"], var_name="Well", value_name="Confluence")
        df["Well"] = df["Well"].str.strip().str.upper()
        treatments["Well"] = treatments["Well"].str.strip().str.upper()
        celltypes["Well"] = celltypes["Well"].str.strip().str.upper()

        treatments.rename(columns={"Treatment": "Treatment"}, inplace=True)
        celltypes.rename(columns={"Cell type": "CellType"}, inplace=True)

        df = df.merge(treatments, on="Well", how="left")
        df = df.merge(celltypes, on="Well", how="left")

        if "Treatment" not in df.columns or "CellType" not in df.columns:
            return go.Figure(layout_title_text="Missing columns: Treatment or CellType")

        # Filter based on selections
        df = df.dropna(subset=['Treatment', 'CellType'])
        df = df[df["Treatment"].isin(selected_treatments) & df["CellType"].isin(selected_celltypes)]

        grouped = df.groupby(["Time", "Treatment", "CellType"]).agg({"Confluence": ["mean", "std"]}).reset_index()
        grouped.columns = ["Time", "Treatment", "CellType", "Mean Confluence", "Std Confluence"]

        fig = go.Figure()
        colors = px.colors.qualitative.Set1
        color_map = {(t, c): colors[i % len(colors)] for i, (t, c) in
                     enumerate(grouped.groupby(["Treatment", "CellType"]).groups.keys())}

        for (t, c), subset in grouped.groupby(["Treatment", "CellType"]):
            color = color_map[(t, c)]
            fig.add_trace(go.Scatter(
                x=subset["Time"],
                y=subset["Mean Confluence"],
                mode='lines',
                name=f"{t} ({c})",
                line=dict(color=color)
            ))

            fig.add_trace(go.Scatter(
                x=subset["Time"].tolist() + subset["Time"].tolist()[::-1],
                y=(subset["Mean Confluence"] + subset["Std Confluence"]).tolist() +
                  (subset["Mean Confluence"] - subset["Std Confluence"]).tolist()[::-1],
                fill='toself',
                fillcolor=f'rgba({color[4:-1]},0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                showlegend=False
            ))

        fig.update_layout(
            title=graph_titles.get(data_type, f"{data_type.capitalize()} Over Time"),
            xaxis_title="Time (hours)",
            yaxis_title=y_axis_titles.get(data_type, "Value"),
            template="simple_white",
            legend_title_text="Treatment (Cell Type)"
        )
        return fig

    if is_multi_plot:
        # Prioritize the order of graphs: phase and ratio first
        ordered_data_types = ["phase", "ratio", "green", "red"]
        return html.Div([
            dbc.Card(
                [
                    dbc.CardHeader(graph_titles.get(dt, f"{dt.capitalize()} Plot")),
                    dbc.CardBody(
                        dcc.Graph(figure=create_plot(dt), config=config)
                    )
                ],
                className="mb-4"
            ) for dt in ordered_data_types if data_files.get(dt) is not None
        ], style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gap": "20px"})
    else:
        # Generate a single plot for individual view
        figure_object = create_plot(data_type)
        return dbc.Card(
            [
                dbc.CardHeader(graph_titles.get(data_type, f"{data_type.capitalize()} Plot")),
                dbc.CardBody(
                    dcc.Graph(
                        id="confluence_graph",
                        figure=figure_object,
                        config=config
                    )
                )
            ],
            className="mt-3"
        )


# Function to create diagnostics content
def create_diagnostics_content(sheets):
    diagnostics = []

    # Extract phase data
    phase_data = sheets.get("phase", pd.DataFrame())

    # Ensure "Time" is treated as a column
    if phase_data.index.name is None:
        phase_data.index.name = "Time"  # Explicitly name the index as "Time"
    phase_data = phase_data.reset_index()  # Reset index to make "Time" a column

    # Debugging: Check the structure of phase_data
    print("Phase DataFrame structure after resetting index:")
    print(phase_data.head())
    print(phase_data.columns)

    if "Time" not in phase_data.columns:
        diagnostics.append(html.Div("No 'Time' column found in phase data.", className="text-danger"))
    else:
        # Filter rows where Time == 0
        timepoint_0_data = phase_data[phase_data["Time"] == 0]

        if timepoint_0_data.empty:
            diagnostics.append(html.Div("No phase data available at timepoint 0.", className="text-danger"))
        else:
            # Drop NaN values and reshape data
            timepoint_0_data = timepoint_0_data.drop(columns=["Time"]).dropna(axis=1)
            melted_data = timepoint_0_data.melt(value_vars=timepoint_0_data.columns, var_name="Well", value_name="Phase Value")

            # Create histogram
            histogram_fig = px.histogram(
                melted_data,
                x="Phase Value",
                nbins=200,
                labels={"x": "Phase Value", "y": "Count"},
                title="Cell Seeding Check: Phase Data Distribution at Timepoint 0"
            )
            histogram_fig.update_layout(
                template="simple_white",
                height=400,
                width=1000,  # Set a fixed height for the histogram
                margin=dict(l=40, r=20, t=40, b=40)  # Adjust margins if needed
            )

            # Create bar chart
            bar_chart_fig = px.bar(
                melted_data,
                x="Well",
                y="Phase Value",
                labels={"Well": "Well", "Phase Value": "Phase Value"},
                title="Phase Values Across Wells at Timepoint 0"
            )
            bar_chart_fig.update_layout(
                template="simple_white",
                xaxis=dict(tickangle=45, title=dict(standoff=10)),  # Rotate X-axis labels for compactness
                yaxis=dict(title="Phase Value"),
                margin=dict(l=40, r=20, t=40, b=80),  # Compact margins
                height=300  # Compact height
            )

            # Add histogram and bar chart to diagnostics
            diagnostics.append(
                dbc.AccordionItem(
                    [
                        dcc.Graph(figure=histogram_fig),
                        dcc.Graph(figure=bar_chart_fig)
                    ],
                    title="Phase Data Visualizations"
                )
            )

    # Display available sheets
    diagnostics.append(
        dbc.AccordionItem(
            [
                html.H5("Available Sheets"),
                html.Ul([html.Li(sheet) for sheet in sheets.keys()])
            ],
            title="Available Sheets"
        )
    )

    # Wrap diagnostics in an Accordion
    return dbc.Accordion(diagnostics, always_open=True)


def create_individual_plot(selected_treatments, selected_celltypes, selected_data_type, export_format, export_filename, sheets, treatments, celltypes):
    return generate_plot(selected_data_type, selected_treatments, selected_celltypes, export_format, export_filename, sheets, treatments, celltypes, is_multi_plot=False)

def create_multi_plot(selected_treatments, selected_celltypes, selected_data_type, export_format, export_filename, sheets, treatments, celltypes):
    return generate_plot(selected_data_type, selected_treatments, selected_celltypes, export_format, export_filename, sheets, treatments, celltypes, is_multi_plot=True)

def create_heatmap(selected_treatments, selected_celltypes, selected_data_type, sheets, treatments, celltypes, export_format, export_filename):
    # Load the selected data type
    data_files = {
        "phase": process_microscopy_data(sheets["phase"]) if "phase" in sheets else None,
        "green": process_microscopy_data(sheets["green"]) if "green" in sheets else None,
        "red": process_microscopy_data(sheets["red"]) if "red" in sheets else None,
    }

    # Compute ratio if needed
    if "green" in sheets and "red" in sheets:
        data_files["ratio"] = data_files["green"] / data_files["red"]

    df = data_files.get(selected_data_type)
    if df is None:
        return html.P(f"No data available for {selected_data_type}.")

    # Reshape and merge data
    df = df.reset_index().melt(id_vars=["Time"], var_name="Well", value_name="Value")
    df["Well"] = df["Well"].str.strip().str.upper()
    treatments["Well"] = treatments["Well"].str.strip().str.upper()
    celltypes["Well"] = celltypes["Well"].str.strip().str.upper()

    treatments.rename(columns={"Treatment": "Treatment"}, inplace=True)
    celltypes.rename(columns={"Cell type": "CellType"}, inplace=True)

    df = df.merge(treatments, on="Well", how="left")
    df = df.merge(celltypes, on="Well", how="left")

    if "Treatment" not in df.columns or "CellType" not in df.columns:
        return html.P("Missing columns: Treatment or CellType.")

    # Filter based on selections
    df = df.dropna(subset=['Treatment', 'CellType'])
    df = df[df["Treatment"].isin(selected_treatments) & df["CellType"].isin(selected_celltypes)]

    if df.empty:
        return html.P("No data available for the selected treatments and cell types.")

    # Combine Treatment and CellType into a single identifier
    df["Treatment_CellType"] = df["Treatment"] + " (" + df["CellType"] + ")"

    # Pivot the data for heatmap (flip x and y axes)
    heatmap_data = df.pivot_table(index="Treatment_CellType", columns="Time", values="Value", aggfunc="mean")

    # Reorder the rows of the heatmap to group by cell type first, then by treatment
    combined_order = [
        f"{treatment} ({celltype})"
        for celltype in selected_celltypes
        for treatment in selected_treatments
    ]
    heatmap_data = heatmap_data.loc[combined_order]

    # Generate a proper title for the heatmap
    data_type_titles = {
        "phase": "Confluence",
        "green": "Green Fluorescence",
        "red": "Red Fluorescence",
        "ratio": "Green/Red Ratio"
    }
    heatmap_title = f"{data_type_titles.get(selected_data_type, selected_data_type.capitalize())} Over Time"

    # Create the heatmap
    fig = px.imshow(
        heatmap_data,
        labels={"x": "Time", "y": "Treatment (CellType)", "color": data_type_titles.get(selected_data_type, selected_data_type.capitalize())},
        color_continuous_scale="RdYlGn",  # Green-to-red color scale
        title=heatmap_title
    )
    fig.update_layout(
        template="simple_white",
        xaxis_title="Time (hours)",
        yaxis_title="Treatment (CellType)",
        height=600
    )

    # Configure download options
    config = {
        'toImageButtonOptions': {
            'format': export_format,  # Use the user-selected format (e.g., 'svg', 'png')
            'filename': export_filename,  # Use the user-provided filename
            'scale': 2  # Adjust the scale for higher resolution
        }
    }

    return dbc.Card(
        [
            dbc.CardHeader(heatmap_title),
            dbc.CardBody(
                dcc.Graph(
                    id="heatmap_graph",
                    figure=fig,
                    config=config  # Add the config for download options
                )
            )
        ],
        className="mt-3"
    )


if __name__ == "__main__":
    app.run(debug=True)
