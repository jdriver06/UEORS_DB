
import pandas as pd
import db_tools
import datetime

file = 'Sasol Surfactants for import.xlsx'
result = pd.read_excel(file, sheetname='Sasol (Not imported) (stocks)', skiprows=2)

stocks = []

for i in range(result.values.shape[0]):
    s_id = result.values[i, 0]
    lot_num = str(result.values[i, 1])
    activity = 100. * result.values[i, 2]
    qty = result.values[i, 3]
    rec_date = result.values[i, 4]
    notes = result.values[i, 5]

    if isinstance(rec_date, datetime.date):
        rec_date = '{}/{}/{}'.format(rec_date.month, rec_date.day, rec_date.year)

    # print([s_id, lot_num, activity, qty, rec_date, notes])

    stocks.append([s_id, lot_num, rec_date, 'NULL', activity, 'NULL', qty, 11, notes])


server = 'UEORS-DB\\'
database = 'UEORS_MAIN_DB'
username = 'sa'
password = '5k1a7n806UEORS'

connection = db_tools.connect_to_database(server, database, username, password)

if connection is not None:
    try:
        # print(connection)
        # print(len(stocks))
        # print(stocks)
        ii = 0
        for stock in stocks:
            print(ii, stock)
            ii += 1
            db_tools.insert_values_into_table(connection, 'surfactants_schema.surfactant_stocks', stock)
        #
        # db_tools.insert_values_into_table(connection,
        #                                   'surfactants_schema.dilutions_measurements_and_treatments',
        #                                   filtration_dilutions)
        # db_tools.insert_values_into_table(connection, 'surfactants_schema.surfactant_stocks', stocks)

    except Exception as e:
        print(e)
    finally:
        connection.close()
