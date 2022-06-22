
import pandas as pd
import numpy as np
import db_tools
from math import nan, isnan

file = 'C:\\Users\\jdriver\\PyCharmProjects\\UEORS_DB\\Copy of Harcros not imported.xlsx'
# sheets = {'ARC': 2, 'BASF': 3, 'BH': 3, 'Bolland': 3, 'Carboxylates': 3, 'ChemEOR': 3, 'Clariant': 3, 'CNPC': 2}
#
# for sheet, h_row in sheets.items():
#     result = pd.read_excel(file, sheetname=sheet, skiprows=h_row - 1)
#     print(result)

result = pd.read_excel(file, sheetname='Harcros (new hydrophobes)', skiprows=2)

hydrophobes = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'G': 6, 'H': 7, 'P': 8, 'Z': 9, 'L': 10, 'M': 11, 'Q': 12,
               'X': 13, 'Y': 14, 'W': 15, 'V': 16, 'R': 17, 'U': 18, 'I': 19, 'T': 20, 'J': 21, 'S': 22}

locations = {'Nano-neat cabinet': 2, 'Rxn Top Shelf': 9, 'null': 1, 'Nano Top West': 5, 'unknown': 1, 'Main Surf': 6,
             'Nano bot QC': 4, 'Main Surf ': 6, 'Main Surf\'': 6, 'Nadeeka': 8, 'Back-up.': 1, 0: 1,
             'Stephanie cart': 7, 'Stephanie\'s cart': 7, 'Nano Top Shelf': 3, 'Rxn top shelf': 9, np.nan: 1,
             'Rxn Top shelf': 9, 'Nano neat cabinet': 2, 'Rxn bench': 10, 'Nano (50 mL- 9/7/16)': 11,
             'Nano (60 mL )': 11, 'Nano (60 mL)': 11, 'Nano Lab - Back up': 12, 'Nano MGL Bottom': 13,
             'Nano - backup': 12, 'Nano - Back Up': 13, 'Null': 1, 'Nano (60mL)': 11, 'Nano MGL shelf': 14,
             'Rxn - Main Surf': 6, 'Surf': 6, 'Main Surf - DI': 15, 'Nano Neat Cabinet': 2, 'Nano lab': 11}

surfactants = []
surfactants_test = []
unique_surfactants = []
unique_surfactants_test = []
names_and_lots = []
names_and_lots_dict = dict()
lot_nums = []
stocks = []
dilutions = []
ht_stocks = []
ht_dilutions = []


def heat_treated(notes: str) -> bool:

    if not notes:
        return False

    if notes.lower().find('heat-treated') > -1 or notes.lower().find('heat treated') > -1 or notes.find('HT') > -1:
        return True


def ph_measured_or_adjusted(notes: str) -> bool:

    if not notes:
        return False

    for note in notes.split('.'):
        if note.lower().find('ph ') > -1:
            return True


def get_ph(txt: str) -> float:

    try:
        return float(txt)
    except ValueError:
        return nan


def filtered(notes: str) -> bool:

    if not notes:
        return False

    if notes.lower().find('filtered'):
        return True


def standardize_date(txt: str) -> str:

    txt = txt.split('/')

    if len(txt) != 3:
        return ''

    date = ''

    if len(txt[0]) == 1:
        date += '0'
    date += txt[0] + '/'

    if len(txt[1]) == 1:
        date += '0'
    date += txt[1] + '/'

    if len(txt[2]) == 2:
        date += '20'
    date += txt[2]

    return date


def extract_ph_measured_or_adjusted(notes: str, sd_id: int) -> list:

    if not ph_measured_or_adjusted(notes):
        return []

    measurements_and_adjustments = []

    j = notes.lower().find('ph ')
    notes = notes[j:]
    notes = notes.lower().split(' ')

    for i, note in enumerate(notes):

        pH = nan
        date = ''
        is_measured = False
        punc = ['.', ',', ';']

        if note == 'ph':

            if i < len(notes) - 2:

                if notes[i + 1] == 'to':
                    pH = get_ph(notes[i + 2])

                    if i < len(notes) - 4:
                        if notes[i + 3] == 'on' and notes[i + 4].find('/') > -1:
                            date = notes[i + 4]
                            if date[-1] in punc:
                                date = date[:-1]
                            date = standardize_date(date)

                elif notes[i + 2] == 'to' and not isnan(get_ph(notes[i + 1])):

                    if i < len(notes) - 3:
                        pH = get_ph(notes[i + 3])

                        if i < len(notes) - 5:
                            if notes[i + 4] == 'on' and notes[i + 5].find('/') > -1:
                                date = notes[i + 5]
                                if date[-1] in punc:
                                    date = date[:-1]
                                date = standardize_date(date)

                elif notes[i + 1] in ['adj', 'adjusted']:
                    if i < len(notes) - 3:
                        pH = get_ph(notes[i + 3])
                        if isnan(pH):
                            pH = get_ph(notes[i + 3][:-1])
                        if i < len(notes) - 5:
                            if notes[i + 4] == 'on' and notes[i + 5].find('/') > -1:
                                date = notes[i + 5]
                                if date[-1] in punc:
                                    date = date[:-1]
                                date = standardize_date(date)

                elif notes[i + 1] == 'raised':
                    if notes[i + 2] == 'from' and i < len(notes) - 5:
                        pH = get_ph(notes[i + 5])
                        if isnan(pH):
                            pH = get_ph(notes[i + 5][:-1])
                        # print(i, pH)
                        if i < len(notes) - 7:
                            if notes[i + 6] == 'on' and notes[i + 7].find('/') > -1:
                                date = notes[i + 7]
                                if date[-1] in punc:
                                    date = date[:-1]
                                date = standardize_date(date)

                    elif notes[i + 2] == 'to' and i < len(notes) - 3:
                        pH = get_ph(notes[i + 3])
                        if isnan(pH):
                            pH = get_ph(notes[i + 3][:-1])
                        if i < len(notes) - 5:
                            if notes[i + 4] == 'on' and notes[i + 5].find('/') > -1:
                                date = notes[i + 5]
                                if date[-1] in punc:
                                    date = date[:-1]
                                date = standardize_date(date)

                elif notes[i + 2] == 'on':
                    pH = get_ph(notes[i + 1])
                    is_measured = True

                    if i < len(notes) - 3:
                        date = notes[i + 3]
                        if date[-1] in punc:
                            date = date[:-1]
                        date = standardize_date(date)

            if not isnan(pH):
                if is_measured:
                    mtt_id = 3
                else:
                    mtt_id = 2
                if not date:
                    date = 'NULL'

                measurements_and_adjustments.append((mtt_id, sd_id, pH, date))

    return measurements_and_adjustments


def extract_filtered(notes: str, sd_id: int) -> list:

    if not filtered(notes):
        return []

    filters = []

    i = notes.lower().find('filtered')
    notes = notes[i:]
    notes = notes.lower().split(' ')

    punc = ['.', ',', ';']

    for i, note in enumerate(notes):

        date = ''

        if note == 'filtered':

            if i < len(notes) - 1:
                date = notes[i + 1]
                if date[-1] in punc:
                    date = date[:-1]
                if date[-1] in punc:
                    date = date[:-1]
                date = standardize_date(date)

                if not date and i < len(notes) - 2 and notes[i + 1] == 'on':
                    date = notes[i + 2]
                    if date[-1] in punc:
                        date = date[:-1]
                    if date[-1] in punc:
                        date = date[:-1]
                    date = standardize_date(date)

        if date:
            filters.append((4, sd_id, 'NULL', date))

    return filters


for i in range(result.values.shape[0]):
    if isinstance(result.values[i, 0], str):
        structure = result.values[i, 1]
        structure = structure.split('-')
        n_po = 0
        n_eo = 0
        for element in structure:
            ind = element.find('PO')
            if ind > -1:
                n_po = element[:ind]
            ind = element.find('EO')
            if ind > -1:
                n_eo = element[:ind]

        n_po = float(n_po)
        n_eo = float(n_eo)
        hydro_char = result.values[i, 0][0]
        lot_num = result.values[i, 2]
        if isinstance(lot_num, str) and lot_num[-1] == ' ':
            lot_num = lot_num[:-1]

        name = hydro_char
        if n_po < 10.:
            name += '0' + str(n_po)
        else:
            name += str(n_po)
        name += '-'
        if n_eo < 10.:
            name += '0' + str(n_eo)
        else:
            name += str(n_eo)
        name += 'N'
        name_and_lot = (name, lot_num)
        if name_and_lot not in names_and_lots:
            names_and_lots.append(name_and_lot)
            names_and_lots_dict[name_and_lot] = []
        names_and_lots_dict[name_and_lot].append(i)

        hazards = str(result.values[i, 7])
        if hazards == 'nan':
            hazards = ''

        surfactant = ('NULL', 21, 'NULL', hydrophobes[hydro_char], n_eo, n_po, 6, 'NULL', 'NULL', 'NULL', hazards, 0)
        surfactant_test = ('NULL', 21, 'NULL', hydrophobes[hydro_char], n_eo, n_po, 6, 'NULL', 'NULL', 'NULL', 0)
        surfactants.append(surfactant)
        surfactants_test.append(surfactant_test)
        if surfactant_test not in unique_surfactants_test:
            unique_surfactants_test.append(surfactant_test)
            unique_surfactants.append(surfactant)

        act = round(100. * result.values[i, 3], 1)
        qty = round(result.values[i, 4])
        notes = result.values[i, 6]

        # location_str = str(result.values[i, 8]).rstrip()
        # if location_str not in locations.keys():
        #     location = location_str
        # else:
        #     location = locations[location_str]
        location = 6

        if lot_num not in lot_nums:
            lot_nums.append(lot_num)
            rec_date = str(result.values[i, 5]).rstrip()
            # syn_date = str(result.values[i, 5])[:10]
            # conv_perc = result.values[i, 6]
            #
            # if not isinstance(conv_perc, float) and not isinstance(conv_perc, int):
            #     conv_perc = 'NULL'
            # else:
            #     conv_perc = round(1. * conv_perc, 1)

            stock = (len(lot_nums), lot_num, rec_date, 'NULL', act, 0.0, qty, location, notes)
            stocks.append(stock)
        else:
            dilution = (len(stocks) + 540, act, qty, 'NULL')
            dilutions.append(dilution)

# print(stocks)
# print(dilutions)
# print(names_and_lots_dict)
print(len(names_and_lots_dict.keys()))
print(names_and_lots_dict.keys())

stocks = []
dilutions = []
ph_stocks = []
ph_dilutions = []
filtration_stocks = []
filtration_dilutions = []

for key, value in names_and_lots_dict.items():

    activities = []

    for j in value:
        activities.append(round(100. * result.values[j, 3], 1))

    stock_act = max(activities)
    ind = activities.index(stock_act)
    stock_id = len(stocks) + 1

    for k, act in enumerate(activities):

        i = value[k]

        qty = round(result.values[i, 4])
        rec_date = str(result.values[i, 5]).rstrip()
        rec_date = rec_date.split()[0]
        # syn_date = str(result.values[i, 5])[:10]
        # if syn_date.lower() == 'unknown':
        #     syn_date = 'NULL'
        # location_str = str(result.values[i, 8]).rstrip()
        # location = locations[location_str]
        location = 6
        notes = str(result.values[i, 6])
        if notes == 'nan':
            notes = ''

        if k == ind:
            search_surfactant = surfactants_test[i]
            s_ind = unique_surfactants_test.index(search_surfactant) + 1
            lot_num = str(key[1])
            # conv_perc = result.values[i, 6]
            #
            # if not isinstance(conv_perc, float) and not isinstance(conv_perc, int):
            #     conv_perc = 'NULL'
            # else:
            #     conv_perc = round(1. * conv_perc, 1)

            stock = (s_ind + 744, lot_num, rec_date, 'NULL', act, 0.0, qty, location, notes)
            print(rec_date)
            stocks.append(stock)

            # if heat_treated(notes):
            #     ht_stocks.append((1, len(stocks) + 281, 'NULL', 'NULL'))
            #
            # if ph_measured_or_adjusted(notes):
            #     ph_notes = extract_ph_measured_or_adjusted(notes, len(stocks) + 281)
            #     for ph_note in ph_notes:
            #         # print(ph_note)
            #         ph_stocks.append(ph_note)
            #
            # if filtered(notes):
            #     filter_notes = extract_filtered(notes, len(stocks) + 281)
            #     for filter_note in filter_notes:
            #         # print(filter_note)
            #         filtration_stocks.append(filter_note)

        else:
            dilution = (stock_id + 540, act, qty, 'NULL', location, notes)
            dilutions.append(dilution)

            # if heat_treated(notes):
            #     ht_dilutions.append((1, len(dilutions), 'NULL', 'NULL'))
            #     # print('heat-treated dilution:')
            #     # print(notes)
            #
            # if ph_measured_or_adjusted(notes):
            #     ph_notes = extract_ph_measured_or_adjusted(notes, len(dilutions) + 188)
            #     for ph_note in ph_notes:
            #         # print(ph_note)
            #         ph_dilutions.append(ph_note)
            #
            # if filtered(notes):
            #     filter_notes = extract_filtered(notes, len(dilutions) + 188)
            #     for filter_note in filter_notes:
            #         filtration_dilutions.append(filter_note)

# print('')
# print(stocks)
# print(dilutions)

server = 'UEORS-DB\\'
database = 'UEORS_MAIN_DB'
username = 'sa'
password = '5k1a7n806UEORS'
#
connection = db_tools.connect_to_database(server, database, username, password)
#
if connection is not None:
    try:
        # print(connection)
        print(len(stocks))
        print(stocks)
        # ii = 0
        # for stock in stocks:
        #     print(ii)
        #     ii += 1
        #     db_tools.insert_values_into_table(connection, 'surfactants_schema.surfactant_stocks', [stock])
        #
        # db_tools.insert_values_into_table(connection,
        #                                   'surfactants_schema.dilutions_measurements_and_treatments',
        #                                   filtration_dilutions)
        db_tools.insert_values_into_table(connection, 'surfactants_schema.surfactant_stocks', stocks)

    except Exception as e:
        print(e)
    finally:
        connection.close()
