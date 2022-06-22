
import db_tools
import pandas as pd
import math

result = pd.read_excel('Tougas Polymer Database.xlsx')
n_rows = result.values.shape[0]

server = 'UEORS-DB\\'
database = 'UEORS_MAIN_DB'
username = 'sa'
password = '5k1a7n806UEORS'
connection = db_tools.connect_to_database(server, database, username, password)

Params = db_tools.DBObjects.Params

for i in range(n_rows):
    row = result.values[i, :]
    row[0] = row[0].lstrip().rstrip()
    for j, value in enumerate(row):
        if isinstance(value, float) and math.isnan(value):
            row[j] = 'NULL'

    db_tools.execute_stored_procedure_with_params(connection, db_tools.DBObjects.Procedures.AddPolymer.value,
                                                  {Params.PolymerName.value: row[0],
                                                   Params.Manufacturer.value: 47,
                                                   Params.RecCompany.value: 'NULL',
                                                   Params.PolymerType.value: 'synthetic',
                                                   Params.AcrylateLow.value: row[1],
                                                   Params.AcrylateHigh.value: row[2],
                                                   Params.SulfonateLow.value: row[3],
                                                   Params.SulfonateHigh.value: row[4],
                                                   Params.MWLow.value: row[5],
                                                   Params.MWHigh.value: row[6],
                                                   Params.Discontinued.value: row[7],
                                                   Params.Notes.value: row[8]})

connection.cursor().commit()
connection.close()
