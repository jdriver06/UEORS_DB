
import db_tools
import pandas as pd

server = 'UEORS-DB\\'
database = 'UEORS_MAIN_DB'
username = 'ueors_user'
password = 'ueor101'

connection = db_tools.connect_to_database(server, database, username, password)

if connection is not None:
    try:
        procedure = 'surfactants_schema.select_inventory_items_from_ig_id'
        params = {'ig_id': 2}
        sulfates = db_tools.execute_stored_procedure_with_params(connection, procedure, params).fetchall()
        new_sulfates = []
        for item in sulfates:
            new_sulfates.append(list(item))

        df = pd.DataFrame(new_sulfates, columns=['Name', 'Structure', 'Stock ID', 'Dilution ID', 'Lot #', 'Act. %'])

        writer = pd.ExcelWriter('Sulfates_Export.xlsx')
        df.to_excel(writer)

    except Exception as e:
        print(e)

    finally:
        connection.close()
