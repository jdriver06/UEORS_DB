
from PyPDF2 import PdfFileReader
import re


def extract_information(pdf_path):

    page_text = []

    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        for i in range(number_of_pages):
            page = pdf.getPage(i)
            page_text.append(page.extractText())

    j = 1
    found = False

    while not found:

        txt = page_text[1][:j]

        for i in range(number_of_pages):
            if i in [0, 1]:
                continue
            if page_text[i][:j] != txt:
                found = True

        j += 1

    total_text = ''
    for i in range(number_of_pages):
        new_text = page_text[i]
        new_text = re.split('_+Page ', new_text)[0]
        if i > 0:
            new_text = new_text[j-2:]
        total_text += new_text

    # print('')
    #
    # print(total_text)

    print('')

    first_info = re.split('1\. Identification', total_text)[1]
    first_info = re.split('2\. Hazard\(s\) identification', first_info)[0]
    product_name = re.split('Product Name', first_info)[1]
    product_name = re.split('Cat No\. :', product_name)[0]
    cat_num = re.split('Cat No\. :', first_info)[1]
    cas_num = ''
    syns = ''

    if first_info.find('CAS-No') != -1 or first_info.find('CAS No') != -1:
        cat_num = re.split('CAS.No', cat_num)[0]
        cas_num = re.split('CAS.No', first_info)[1]
        if first_info.find('Synonyms') != -1:
            cas_num = re.split('Synonyms', cas_num)[0]
            syns = re.split('Synonyms', first_info)[1]
            syns = re.split('Recommended Use', syns)[0]
        else:
            cas_num = re.split('Recommended Use', cas_num)[0]
    elif first_info.find('Synonyms') != -1:
        cat_num = re.split('Synonyms', cat_num)[0]
        syns = re.split('Synonyms', first_info)[1]
        syns = re.split('Recommended Use', syns)[0]
    else:
        cat_num = re.split('Recommended Use', cat_num)[0]

    physical_info = re.split('9\. Physical and chemical properties', total_text)[1]
    physical_info = re.split('10\. Stability and reactivity', physical_info)[0]
    physical_state = re.split('Physical State', physical_info)[1]
    physical_state = re.split('Appearance', physical_state)[0]

    print('1. Identification\n\nProduct Name: {}\nCat No.: {}\nCAS #: {}\nSynonyms: {}\nPhysical State: {}\n'.format(
        product_name, cat_num, cas_num, syns, physical_state))

    hazards_id = re.split('2\. Hazard\(s\) identification', total_text)[1]
    hazards_id = re.split('3\. Composition/Information on Ingredients', hazards_id)[0]
    temp_categories = re.findall('Category [0-9] ?', hazards_id)
    temp_hazards = re.split('Category [0-9] ?', hazards_id)
    hazards = []
    categories = []
    i = 0
    trunc_next = False
    for tc, th in zip(temp_categories, temp_hazards):
        if trunc_next:
            th = th[2:]
        trunc_next = False
        if tc[-1] == ' ':
            categories.append(tc[:-1] + temp_hazards[i + 1][0:2])
            hazards.append(th)
            trunc_next = True
        else:
            categories.append(tc)
            hazards.append(th)
        i += 1
    first_hazard = re.split('[A-Z]', hazards[0])[-1]
    first_letter = re.findall('[A-Z]', hazards[0])[-1]
    first_hazard = first_letter + first_hazard
    hazards[0] = first_hazard

    print('2. Hazard(s) identification')
    print('\nClassification:')
    for hazard, category in zip(hazards, categories):
        print('{} - {}'.format(hazard, category))

    hazard_statements = re.split('Hazard Statements', hazards_id)[1]
    hazard_statements = re.split('Precautionary Statements', hazard_statements)[0]
    if hazard_statements.find('Company') != -1:
        hazard_statements = hazard_statements[:hazard_statements.find('Company')]

    print('\nHazard Statements:')
    hss = re.split('[A-Z]', hazard_statements)[1:]
    caps = re.findall('[A-Z]', hazard_statements)

    print_hss = ''
    for cap, hs in zip(caps, hss):
        print_hss += cap + hs + '\n'
    print(print_hss)

    stability_reactivity = re.split('10\. Stability and reactivity', total_text)[1]
    stability_reactivity = re.split('11\. Toxicological information', stability_reactivity)[0]

    # print('\n' + stability_reactivity)

    stability = re.split('Stability', stability_reactivity)[1]
    stability = re.split('Conditions to Avoid', stability)[0]
    conditions = re.split('Conditions to Avoid', stability_reactivity)[1]
    conditions = re.split('Incompatible Materials', conditions)[0]
    incompatible = re.split('Incompatible Materials', stability_reactivity)[1]
    incompatible = re.split('Hazardous Decomposition Products', incompatible)[0]

    print('\n10. Stability and reactivity\n')
    print('Stability: {}\nConditions to Avoid: {}\nIncompatible Materials: {}'.format(stability, conditions,
                                                                                      incompatible))

    return information


# path = '1--3-DIMETHLAMINOPROPL--3-E-1G.pdf'
# path = 'HYDROGEN-PEROXIDE-30---500ML.pdf'
# path = 'U:\\UEORLAB1\\SDS - Chem Haz Profiles\\GHS_SDS\\1-Butanol, Fisher.pdf'
path = 'TOLUENE-CERTIFIED-ACS-1L.pdf'
info = extract_information(path)
# print(info)
