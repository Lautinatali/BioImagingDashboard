import pandas as pd

# Function to load all sheets from the Excel file into a dictionary
def load_excel_tabs(platemap_path):
    # Read all sheets into a dictionary of DataFrames
    sheets_dict = pd.read_excel(platemap_path, sheet_name=None, index_col=0)
    return sheets_dict

# Function to process the DataFrame
def process_platemap(df, value_name):
    # Stack the dataframe and reset the index to make the data long-format
    platemap = df.stack().reset_index()

    # Rename columns to match the desired structure
    platemap.columns = ["Row", "Column", value_name]

    # Generate the well names by combining row and column
    platemap["Well"] = platemap["Row"] + platemap["Column"].astype(str)

    # Print the unique values for the specified value_name
    unique_values = platemap[value_name].unique()
    print(f"Available {value_name}s:")
    print(unique_values)

    # Drop the Row and Column columns as they are no longer needed
    return platemap.drop(columns=["Row", "Column"])

def process_microscopy_data(df):
    df.index.name = "Time"
    df = df.map(lambda x: float(x.replace(',', '.')) if isinstance(x, str) else x)
    return df



