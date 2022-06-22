
from PyPDF2 import PdfFileReader


def get_info(path: str):

    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        info = pdf.getDocumentInfo()

    return info


if __name__ == '__main__':
    path = 'U:\\Paper collection\\SPE Papers\\SPE-154270-MS Optimal Injection Design Utilizing Tracer and Simulation in a Surfactant Pilot for a Fractured Carbonate Yates Field.pdf'
    info = get_info(path=path)
    print(info)
