
import db_tools
import pandas as pd
import datetime

result = pd.read_excel('Cargill polymer inventory.xlsx')
n_rows = result.values.shape[0]

server = 'UEORS-DB\\'
database = 'UEORS_MAIN_DB'
username = 'sa'
password = '5k1a7n806UEORS'
connection = db_tools.connect_to_database(server, database, username, password)

Params = db_tools.DBObjects.Params
proc = db_tools.DBObjects.Procedures.AddPolymerInventory.value
company = 'Cargill'

for i in range(n_rows):

    row = result.values[i, :]
    row[0] = row[0].lstrip().rstrip()

    for j, element in enumerate(row):

        if pd.isnull(element):
            row[j] = 'NULL'
            continue

        if isinstance(element, datetime.date):
            element = str(element)
            row[j] = element[5:7] + '/' + element[8:10] + '/' + element[:4]

    db_tools.execute_stored_procedure_with_params(connection, proc, {Params.PolymerName.value: row[0],
                                                                     Params.ManufacturerName.value: company,
                                                                     Params.LotNum.value: row[5],
                                                                     Params.RecDate.value: row[4],
                                                                     Params.InitMass.value: row[2],
                                                                     Params.CurrMass.value: row[3],
                                                                     Params.LocID.value: row[1]})

connection.cursor().commit()
connection.close()
