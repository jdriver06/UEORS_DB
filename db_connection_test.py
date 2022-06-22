
import tkinter as tk
import sys


def main():

    app = tk.Tk()
    label = tk.Label(app)
    var = tk.StringVar(label)
    var.set('my_var')
    label.config(textvariable=var)
    label.pack(side=tk.TOP)
    cnxn = None

    try:
        import pyodbc

        server = 'UEORS-DB\\'
        database = 'UEORS_MAIN_DB'
        username = 'ueors_user'
        password = 'ueor101'

        cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server +
                              ';DATABASE=' + database +
                              ';UID=' + username +
                              ';PWD=' + password)

        var.set('connection successful')

    except Exception as e:
        print(e)
        var.set('connection_failed')

    finally:
        if cnxn is not None:
            cnxn.close()
        sys.exit(app.mainloop())


if __name__ == '__main__':

    main()
