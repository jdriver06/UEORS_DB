
import pandas as pd
import db_tools
import math
from time import sleep


def make_sa_connection() -> db_tools.pyodbc.Connection:

    server = 'UEORS-DB\\'
    database = 'UEORS_MAIN_DB'
    username = 'sa'
    password = '5k1a7n806UEORS'

    conn = db_tools.connect_to_database(server, database, username, password)

    return conn


def export_single_components_to_db():

    data = pd.read_excel('Current OSHA Chemical Inventory (JWD).xlsx', sheetname='Single-Component Database')
    connection = make_sa_connection()

    for row in range(len(data.values[:, 0])):

        try:
            db_tools.insert_values_into_table(connection, 'OSHA_schema.single_component_chemical_db',
                                              data.values[row, :4])
        except Exception as e:
            print(e)

    connection.close()


def export_single_cas_database():

    data = pd.read_excel('Current OSHA Chemical Inventory (JWD).xlsx', sheetname='Chemicals Database (1 CAS)')
    connection = make_sa_connection()
    DB_CAS_NUMS = db_tools.select_column_from_table(connection, db_tools.DBObjects.Tables.SingleChemDB.value,
                                                    db_tools.DBObjects.Columns.CASNum.value).fetchall()
    DB_CHEM_NAMES = db_tools.select_column_from_table(connection, db_tools.DBObjects.Tables.ChemDB.value,
                                                      db_tools.DBObjects.Columns.ChemName.value).fetchall()
    DB_CAS_NUMS_LIST = list()
    DB_CHEM_NAMES_LIST = list()
    for CN, CHEM_NAME in zip(DB_CAS_NUMS, DB_CHEM_NAMES):
        DB_CAS_NUMS_LIST.append(CN[0])
        DB_CHEM_NAMES_LIST.append(CHEM_NAME[0])

    for i in range(data.values.shape[0]):
        if i < 0:
            continue
        chem_name = data.values[i, 0].strip()
        if chem_name not in DB_CHEM_NAMES_LIST:
            print('{} not in database.'.format(chem_name))
        else:
            continue
        syns = data.values[i, 1]
        syn_1 = 'NULL'
        syn_2 = 'NULL'
        syn_3 = 'NULL'
        if not isinstance(syns, str) and math.isnan(syns):
            pass
        else:
            syns = syns.split(';')
            for j in range(len(syns)):
                if j == 0:
                    syn_1 = syns[j].strip()
                elif j == 1:
                    syn_2 = syns[j].strip()
                elif j == 2:
                    syn_3 = syns[j].strip()

        p_state = data.values[i, 2]
        if p_state == 'S':
            p_state = 'solid'
        elif p_state == 'L':
            p_state = 'liquid'
        elif p_state == 'G':
            p_state = 'gas'
        else:
            p_state = 'NULL'

        flam = data.values[i, 3]
        if flam == 'Y':
            flam = 1
        else:
            flam = 0
        phs = data.values[i, 4]
        if phs == 'Y':
            phs = 1
        else:
            phs = 0
        corrosive = data.values[i, 5]
        if corrosive == 'Y':
            corrosive = 1
        else:
            corrosive = 0
        ox = data.values[i, 6]
        if ox == 'Y':
            ox = 1
        else:
            ox = 0
        reducer = data.values[i, 7]
        if reducer == 'Y':
            reducer = 1
        else:
            reducer = 0
        toxic = data.values[i, 8]
        if toxic == 'Y':
            toxic = 1
        else:
            toxic = 0
        health = data.values[i, 9]
        if health == 'Y':
            health = 1
        else:
            health = 0
        peroxide = data.values[i, 10]
        if peroxide == 'Y':
            peroxide = 1
        else:
            peroxide = 0
        warning = data.values[i, 11]
        if warning == 'Y':
            warning = 1
        else:
            warning = 0
        glove = data.values[i, 12]
        face = data.values[i, 13]
        if face == 'Y':
            face = 1
        else:
            face = 0
        apron = data.values[i, 14]
        if apron == 'Y':
            apron = 1
        else:
            apron = 0
        hood = data.values[i, 15]
        if hood == 'Y':
            hood = 1
        else:
            hood = 0
        avoid = data.values[i, 16]
        if not isinstance(avoid, str) and math.isnan(avoid):
            avoid = 'NULL'
        notes = data.values[i, 17]
        if not isinstance(notes, str) and math.isnan(notes):
            notes = 'NULL'
        safety = data.values[i, 18]
        if isinstance(safety, float) and math.isnan(safety):
            safety = 'NULL'
        nfpa = data.values[i, 19]
        if isinstance(nfpa, str):
            nfpa = nfpa.strip()
        else:
            nfpa = 'NULL'
        cas_num = data.values[i, 20].strip()
        perc = data.values[i, 21]

        # Do this if 1 CAS:
        # print(perc)
        if perc == 'xx':
            perc = 'NULL'
        else:
            perc = perc.strip()
            perc = perc.lstrip('>')
            perc = perc.rstrip('%')
            perc = float(perc)

        fire_code = data.values[i, 22]
        if not isinstance(fire_code, str) and math.isnan(fire_code):
            fire_code = 1
        elif fire_code == 'Class IA':
            fire_code = 2
        elif fire_code == 'Class IB':
            fire_code = 3
        elif fire_code == 'Class IC':
            fire_code = 4
        elif fire_code == 'Class II':
            fire_code = 5
        elif fire_code == 'Class IIIA':
            fire_code = 6
        elif fire_code == 'Class IIIB':
            fire_code = 7
        else:
            print('fire code not found: {}'.format(fire_code))
            return

        # cas_nums = cas_num.split(';')
        # percs = perc.split(';')
        #
        # chem_cas_nums = list()
        # chem_percs = list()
        #
        # print('\nName: {}'.format(chem_name))
        # for cn, p in zip(cas_nums, percs):
        #     chem_cas_nums.append(cn.strip())
        #     print('\tCAS #: {}, {}%'.format(cn.strip(), p.strip().strip('%')))
        #     chem_percs.append(p.strip().strip('%'))
        #     if cn.strip() not in DB_CAS_NUMS_LIST:
        #         print('NOT IN LIST!!!')

        # print('Name: {}, Synonyms: {}, {}, {}, Physical State: {}'.format(chem_name, syn_1, syn_2, syn_3, p_state))
        # print('CAS #: {}, Percentage: {}'.format(cas_num, perc))
        # print('NFPA: {}'.format(nfpa))
        # print('Flammable? {}; PHS? {}; Corrosive? {}; Oxidizer? {}; Reducer? {}; Peroxide Former? {}; Toxic? {}'.
        #       format(flam, phs, corrosive, ox, reducer, peroxide, toxic))
        # print('Glove Code: {}, Face Shield? {}, Apron? {}, Hood? {}'.
        #       format(glove, face, apron, hood))
        # print('Avoid: {}'.format(avoid))
        # print('Notes: {}'.format(notes))
        # print('Safety Details: {}'.format(safety))
        # print('Fire Code: {}'.format(fire_code))
        print('')

        values = list()
        values.append(chem_name)
        values.append(syn_1)
        values.append(syn_2)
        values.append(syn_3)
        values.append(cas_num)
        # values.append(chem_cas_nums[0])
        values.append(perc)
        # values.append(chem_percs[0])
        # if len(chem_cas_nums) > 1:
        #     values.append(1)
        # else:
        values.append(0)
        values.append(p_state)
        values.append(phs)
        values.append(flam)
        values.append(corrosive)
        values.append(ox)
        values.append(reducer)
        values.append(peroxide)
        values.append(toxic)
        values.append(health)
        values.append(warning)
        values.append(nfpa)
        values.append(glove)
        values.append(face)
        values.append(apron)
        values.append(hood)
        values.append(avoid)
        values.append(notes)
        values.append(safety)
        values.append(fire_code)
        values.append('NULL')

        db_tools.insert_values_into_table(connection, 'OSHA_schema.chemical_db', values)

        DBO = db_tools.DBObjects
        params = {DBO.Params.ChemName.value: chem_name}
        chem_id = db_tools.execute_stored_procedure_with_params(connection, DBO.Procedures.ChemIDforName.value, params)
        chem_id = chem_id.fetchall()[0][0]
        print(chem_id)
        # if len(chem_cas_nums) > 1:
        #     for cn, p in zip(chem_cas_nums[1:], chem_percs[1:]):
        #         db_tools.insert_values_into_table(connection, 'OSHA_schema.additional_cas_nums', [chem_id, cn, float(p)])

    connection.close()


def export_inventory():

    data = pd.read_excel('Chemicals Inventory (1 CAS).xlsx', sheetname='Chemicals Inv. (1 CAS)')
    connection = make_sa_connection()

    DB_CHEM_NAMES = db_tools.select_column_from_table(connection, 'OSHA_schema.chemical_db', 'chemical_name').fetchall()
    DB_CHEM_NAMES_LIST = list()
    for chem_name in DB_CHEM_NAMES:
        DB_CHEM_NAMES_LIST.append(chem_name[0])

    DBO = db_tools.DBObjects

    for i in range(data.values[:, 0].shape[0]):

        chem_name = data.values[i, 0]
        params = {DBO.Params.ChemName.value: chem_name}
        chem_id = db_tools.execute_stored_procedure_with_params(connection,
                                                                DBO.Procedures.ChemIDforName.value,
                                                                params).fetchall()[0][0]
        loc_id = data.values[i, 1]
        container_size = data.values[i, 2]
        qty = data.values[i, 3]
        units = data.values[i, 4]

        if not isinstance(units, str):
            params = {DBO.Params.ChemName.value: chem_name}
            p_state = db_tools.execute_stored_procedure_with_params(connection,
                                                                    DBO.Procedures.GetPStateforName.value,
                                                                    params).fetchall()[0][0]
            if p_state == 'solid':
                units = 'kg'
            elif p_state == 'liquid':
                units = 'L'
            else:
                units = 'ft^3'

        params = {DBO.Params.ChemID.value: chem_id, DBO.Params.UnitAbbr.value: units,
                  DBO.Params.Size.value: container_size}
        db_tools.execute_stored_procedure_with_params(connection,
                                                      DBO.Procedures.CondInsertContainer.value,
                                                      params)
        connection.commit()
        container_id = db_tools.execute_stored_procedure_with_params(connection,
                                                                     DBO.Procedures.GetContainerID.value,
                                                                     params).fetchall()[0][0]

        final_values = list()
        final_values.append(container_id)
        final_values.append(qty)
        final_values.append(loc_id)

        # print(final_values)

        db_tools.insert_values_into_table(connection, 'OSHA_schema.chemical_inventory', final_values)

    connection.close()


if __name__ == '__main__':
    export_inventory()
