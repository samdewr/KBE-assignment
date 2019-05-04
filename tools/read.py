import pandas as pd


def import_aircraft_data(aircraft_component, filename):
    types = {'Quantity': str,
             'Units': str,
             'Remarks': str}

    if aircraft_component == 'fuselage':
        types.update({'Value': float})

    # Read the input file.
    data_frame = pd.read_excel(filename,
                               sheet_name=aircraft_component,
                               header=0,
                               index_col=0,
                               dtype=types,
                               comment='#')

    # Drop the rows that have a row indexer equal to NaN, such as empty rows.
    # data_frame.drop(labels=np.NaN, inplace=True)
    data_frame.dropna(subset=['Value'], inplace=True)

    try:
        # The rows that contain a list.
        mask = (data_frame['Value'].str[0] == '[')
        # Convert list strings to actual lists
        data_frame['Value'][mask] = data_frame[mask]['Value'].apply(eval)

    except AttributeError:
        # # The rows that are not strings
        # mask = ~(data_frame['Value'] == str)
        pass

    # Return and convert to a dictionary.
    return data_frame['Value'].to_dict()
