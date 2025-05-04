# BioImaging Dashboard

This project is an interactive dashboard for visualizing live cell imaging data (e.g. Incucyte data) built using [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/). It allows users to upload data, visualize it in various formats (line plots, multi-plots, heatmaps), and export the visualizations in different formats.

## Features

- **Data Upload**: Upload Excel files to visualize data.
- **Dynamic Visualizations**:
  - Individual plots for selected data types (e.g., Phase, Green, Red, Green/Red Ratio).
  - Multi-plot view to compare multiple data types side by side.
  - Heatmaps to visualize data trends over time and treatments.
- **Customizable Exports**:
  - Export graphs in SVG or PNG format.
  - Specify custom filenames for exported graphs.
- **Responsive Design**: Built with [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) for a clean and responsive UI.


## Getting Started

### Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lautinatali/BioImagingDashboard.git
   cd plotly-dashboard
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the dashboard:
   ```bash
   python src/dashboard.py
   ```

4. Open your browser and navigate to `http://127.0.0.1:8050/` to view the dashboard.

## Usage

1. **Upload Data**:
   - Drag and drop an Excel file or select one using the upload component.
   - Ensure the file contains the required sheets (minimum required is celltypes, treatments and one of phase/green/red).

2. **Select Data Type**:
   - Choose the data type to visualize individually (e.g., Phase, Green, Red, Green/Red Ratio).

3. **Customize Visualizations**:
   - Filter by treatments and cell types.
   - Switch between tabs for individual plots, multi-plots, diagnostics, and heatmaps.

4. **Export Graphs**:
   - Select the export format (SVG or PNG).
   - Specify a custom filename for the exported graph.

## Tabs Overview

- **Individual**: Displays a single plot for the selected data type.
- **Multi Plot**: Displays multiple plots side by side for comparison.
- **Diagnostics**: Provides diagnostic information about the uploaded data.
- **Heatmaps**: Displays data as heatmaps with treatments on the X-axis, time on the Y-axis, and values represented by color intensity.

## Dependencies

This project uses the following libraries:
- [Dash](https://dash.plotly.com/) for building the interactive dashboard.
- [Plotly](https://plotly.com/) for creating visualizations.
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/) for styling and layout.
- [Pandas](https://pandas.pydata.org/) for data manipulation.
- [NumPy](https://numpy.org/) for numerical operations.


## Contributing

Contributions are welcome! If you'd like to improve this project, please fork the repository and submit a pull request.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgments

- [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/) for providing powerful tools for data visualization.
- [Bootstrap](https://getbootstrap.com/) for the responsive design framework.