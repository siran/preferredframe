from datetime import datetime
import os

import pandas as pd
from matplotlib import pyplot as plt

ranges_rows = []

def find_row_ranges(df, column = 'datetime', timespan_minutes=240):
    """
    Find ranges of sessions that span more than `timespan_minutes` in a sorted df using `column`

        Defaults:
            columnd = 'datetime'
            timespan_minutes = 240 (4h, 8 sessions)
    """

    row_ranges = []
    row_start = None
    row_end = None

    for i, row in df.iterrows():
        if row_start is None:
            datetime_start = row['datetime']
            row_start = i
            continue

        row_prev = i-1

        # print('-----------------')
        # print(f'{row_start=}')
        # print(f'{i=}')
        # print(f'{datetime_start=}')
        # print(f'{row["datetime"]=}')

        row_end = row_prev
        if row['datetime'] - df.iloc[row_prev]['datetime'] <= pd.Timedelta(f'2 hours') and i < df.shape[0]-1:
            continue

        if i == df.shape[0]-1:
            row_end = i

        if row_end - row_start >= 8:
            # adjusting with +2 because of header and first row is 0 index
            row_ranges.append((row_start+2, row_end+2, ))

        row_start = i
        row_end = None

    return row_ranges

def plot_range(tuple, writer, sheetname):
    """Makes a plot of the tuple range"""

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    ##  Amplitude
    # Create a chart object
    chart = workbook.add_chart({'type': 'scatter'})

    # Configure the series of the chart from the dataframe data.
    row_start = tuple[0]
    row_end = tuple[1]
    chart.add_series({
        'categories': f'={sheetname}!$F${row_start}:$F${row_end}',
        'values': f'={sheetname}!$H${row_start}:$H${row_end}',
        'trendline': {
            'type': 'moving_average',
            'period': 2,
        }
    })
    chart.set_legend({'none': True})
    chart.set_x_axis({
        'name': 'Fecha/Hora (dd/mm HH:MM)',
        'date_axis':  True,
        'num_format': 'dd/mm HH:MM',
        'num_font':  {'rotation': -45}
    })
    chart.set_y_axis({'name': 'Amplitud normalizada'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart(f'B{row_start}', chart)

    ##  Star Altitude
    # Create a chart object.
    chart = workbook.add_chart({'type': 'scatter'})

    # Configure the series of the chart from the dataframe data.
    row_start = tuple[0]
    row_end = tuple[1]
    chart.add_series({
        'categories': f'={sheetname}!$F${row_start}:$F${row_end}',
        'values': f'={sheetname}!$M${row_start}:$M${row_end}',
     })
    chart.set_legend({'none': True})
    chart.set_x_axis({
        'name': 'Fecha/Hora (dd/mm HH:MM)',
        'date_axis':  True,
        'num_format': 'dd/mm HH:MM',
        'num_font':  {'rotation': -45}
    })
    chart.set_y_axis({'name': 'Altitud estrella (° sobre horizonte)'})

    # Insert the chart into the worksheet.
    worksheet.insert_chart(f'J{row_start}', chart)

    ##  Amplitude vs Altitude
    # Create a chart object.
    chart = workbook.add_chart({'type': 'scatter'})
    chart.set_legend({'none': True})

    chart.add_series({
        'categories': f'={sheetname}!$M${row_start}:$M${row_end}',
        'values': f'={sheetname}!$H${row_start}:$H${row_end}',
        'trendline': {
            'type': 'moving_average',
            'period': 2,
        },
    })

    chart.set_x_axis({'name': 'Altitud estrella (° sobre horizonte)'})
    chart.set_y_axis({'name': 'Amplitud normalizada'})
    # Insert the chart into the worksheet.
    worksheet.insert_chart(f'R{row_start}', chart)

def plot_ranges_sidereal_time(row_ranges, writer, sheetname):
    """Plots all ranges vs a sidereal time"""

    # Get the xlsxwriter objects from the dataframe writer object.
    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    ##  Amplitude
    # Create a chart object
    chart = workbook.add_chart({'type': 'scatter'})
    chart.set_legend({'none': True})
    chart.set_x_axis({
        'name': 'Hora ajustada a día sideral (HH:MM)',
        'date_axis':  True,
        'num_format': 'HH:MM',
        'num_font':  {'rotation': -45}
    })
    chart.set_y_axis({'name': 'Amplitud normalizada'})

    chart2 = workbook.add_chart({'type': 'scatter'})
    chart2.set_legend({'none': True})
    chart2.set_x_axis({
        'name': 'Hora ajustada a día sideral (HH:MM)',
        'date_axis':  True,
        'num_format': 'HH:MM',
        'num_font':  {'rotation': -45}
    })
    chart2.set_y_axis({'name': 'Altitud estrella (° sobre horizonte)'})

    chart3 = workbook.add_chart({'type': 'scatter'})
    chart3.set_legend({'none': True})
    chart3.set_x_axis({
        'name': 'Altitud estrella (° sobre horizonte)',
    })
    chart3.set_y_axis({'name': 'Amplitud normalizada promedio del desplazamiento franjas)'})

    for tuple in row_ranges:
        # Configure the series of the chart from the dataframe data.
        row_start = tuple[0]
        row_end = tuple[1]
        chart.add_series({
            'categories': f'={sheetname}!$S${row_start}:$S${row_end}',
            'values': f'={sheetname}!$H${row_start}:$H${row_end}',
        })

        chart2.add_series({
            'categories': f'={sheetname}!$S${row_start}:$S${row_end}',
            'values': f'={sheetname}!$M${row_start}:$M${row_end}',
        })

        chart3.add_series({
            'categories': f'={sheetname}!$M${row_start}:$M${row_end}',
            'values': f'={sheetname}!$H${row_start}:$H${row_end}',
            'trendline': {
                'type': 'moving_average',
                'period': 2,
            },
        })


    # Insert the chart2 into the worksheet.
    worksheet.insert_chart(f'C6', chart)
    worksheet.insert_chart(f'J6', chart2)
    worksheet.insert_chart(f'S6', chart3)

def save_colored_spreadsheet(sourcefile, df, row_ranges, make_plot=True):
    """Saves a colored spreadsheet from df row_ranges, also plots charts """

    path, extension = os.path.splitext(sourcefile)
    filename = path.split('/')[-1]
    output_file = os.path.join(ANALYSIS_OUTPUT_PATH, f'{filename}.xlsx')

    num_columns = len(df.columns)
    last_column = chr(ord('A') + num_columns - 1)

    sheetname = 'ColoredSets'

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name=sheetname, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook  = writer.book
    worksheet = writer.sheets[sheetname]

    # Add a format. Light red fill with dark red text.
    formats = [
        workbook.add_format({'bg_color':   '#FFEB9C',
                            'font_color': '#000000'}),
        workbook.add_format({'bg_color':   '#C6EFCE',
                               'font_color': '#000000'})
    ]

    for i, tuple in enumerate(row_ranges):
        row_start, row_end = tuple
        formatnum = i%2
        # Apply a conditional format to the cell range.
        textrange = f'A{row_start}:{last_column}{row_end}'
        # print(textrange)
        worksheet.conditional_format(textrange,
                                        {'type':     'no_blanks',
                                        'format':   formats[formatnum]})

        if make_plot:
            plot_range(tuple, writer, sheetname)

    if make_plot:
        plot_ranges_sidereal_time(row_ranges, writer, sheetname)

    writer.save()
    a=1



def main():
    # read analisys source file
    analysis_sourcefile = os.path.join(ANALYSIS_PATH, ANALYSIS_FILE)
    df = pd.read_csv(analysis_sourcefile)

    # filter df to 'promediadas normalizadas'
    df = df[(df['figure_type']=='normalized') & (df['grouping_type']=='r10s10')]

    # convert datetime column to datetime
    try:
        df['datetime'] = pd.to_datetime(df['datetime'], format="%d-%m-%y %H:%M")
    except Exception:
        df['datetime'] = pd.to_datetime(df['datetime'], format="%Y-%m-%d %H:%M")

    # sorting by datetime
    df.sort_values(by='datetime', inplace=True, ignore_index=True)
    df.reset_index(drop=True, inplace=True)

    # print(df)

    # add sidereal datetime and time
    sidereal_solar_day_ratio = 86164.4 / (24*60*60)
    df['datetime_epoch'] = (df['datetime'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
    initial_datetime = df.iloc[0]['datetime_epoch']
    df['sidereal_datetime_seconds'] = ((df['datetime_epoch'] - initial_datetime) * sidereal_solar_day_ratio) + initial_datetime
    df['datetime_sidereal_adj'] = pd.to_datetime(df['sidereal_datetime_seconds'], unit='s', origin='unix')
    df['time_sidereal_adj'] = df['datetime_sidereal_adj'].apply(lambda dt: dt.replace(day=1,month=1, year=1970))

    df.drop(['datetime_epoch', 'sidereal_datetime_seconds'], axis=1)

    # find row ranges
    row_ranges = find_row_ranges(df)

    # mean amplitud inwindows
    df.set_index('time_sidereal_adj', inplace=True)
    df.sort_index(inplace=True)
    df['mean_amplitude_1h'] = df['amplitude'].rolling('1h').mean()

    df.sort_values(by='datetime', inplace=True, ignore_index=True)
    df.reset_index(drop=False, inplace=True)

    save_colored_spreadsheet(analysis_sourcefile, df, row_ranges, make_plot=MAKE_PLOTS)
    print('Done!')
    a=1


if __name__ == "__main__":

    MAKE_PLOTS = False

    ANALYSIS_FILES = [
        # "180818-181216.csv",
        # "190910-20190930.csv",
        # "180818-181216-filtered.csv",
        # "190910-190930.csv",
        # "190802-190804.csv",
        "200810-200820.csv",

    ]

    ANALYSIS_PATH = "../analysis-summaries"
    ANALYSIS_OUTPUT_PATH = "../analysis-excel"

    if not os.path.isdir(ANALYSIS_OUTPUT_PATH):
        os.mkdir(ANALYSIS_OUTPUT_PATH)


    for ANALYSIS_FILE in ANALYSIS_FILES:
        main()