
from PyQt5.QtWidgets import QWidget, QMainWindow, QGridLayout, QListWidget, QLabel, QListWidgetItem, QLineEdit, QDialog,\
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QCheckBox
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.Qt import pyqtSignal, Qt
import db_tools
from db_tools import DBObjects
from os import startfile
import datetime


class PolymerConnection:

    def __init__(self, cnxn: db_tools.pyodbc.Connection):
        self._cnxn = cnxn
        self._cursor = cnxn.cursor()

    def get_cursor(self):
        return self._cursor

    @staticmethod
    def check_column_and_table(column: DBObjects.Columns, table: DBObjects.Tables):

        if not DBObjects.is_column_in_table(column, table):
            raise(TypeError('The enumerated column is not in the enumerated table.'))

    def update_table_key_value(self, table: DBObjects.Tables, column: DBObjects.Columns, key: str, val: int,
                               set_val: str):

        return db_tools.update_table_set_column_where_key_equals(self._cnxn, table.value, column.value, set_val, key,
                                                                 val)

    def exec_stored_procedure_with_params_no_fetchall(self, procedure: DBObjects.Procedures, params: dict):

        return db_tools.execute_stored_procedure_with_params(self._cnxn, procedure.value, params)

    def exec_stored_procedure_with_params(self, procedure: DBObjects.Procedures, params: dict):

        return db_tools.execute_stored_procedure_with_params(self._cnxn, procedure.value, params).fetchall()

    def exec_search_polymers(self, polymer_name: str, company_name: str, ac_low, ac_high, sulf_low,
                             sulf_high, mw_low, mw_high, inc_disc: int):

        params = {DBObjects.Params.PolymerName.value: polymer_name,
                  DBObjects.Params.ManufacturerName.value: company_name,
                  DBObjects.Params.RecCompanyName.value: company_name,
                  DBObjects.Params.AcrylateLow.value: ac_low,
                  DBObjects.Params.AcrylateHigh.value: ac_high,
                  DBObjects.Params.SulfonateLow.value: sulf_low,
                  DBObjects.Params.SulfonateHigh.value: sulf_high,
                  DBObjects.Params.MWLow.value: mw_low,
                  DBObjects.Params.MWHigh.value: mw_high,
                  DBObjects.Params.IncludeDiscontinued.value: inc_disc}

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SearchPolymers, params)

    def exec_get_polymer_inventory(self, polymer_id: int):

        params = {DBObjects.Params.PolymerID.value: polymer_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetPolymerInventory, params)

    def exec_add_polymer_inventory_by_id(self, polymer_id: int, lot_num: str, rec_date: str, init_mass: int,
                                         loc_id: int):

        params = {DBObjects.Params.PolymerID.value: polymer_id,
                  DBObjects.Params.LotNum.value: lot_num,
                  DBObjects.Params.RecDate.value: rec_date,
                  DBObjects.Params.InitMass.value: init_mass,
                  DBObjects.Params.LocID.value: loc_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddPolymerInventoryID, params)

    def exec_get_rooms(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRooms, {})

    def exec_get_rm_locations(self, room_id: int):

        params = {DBObjects.Params.RoomID.value: room_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRoomLocs, params)

    def exec_search_companies(self, company_name: str):

        params = {DBObjects.Params.CompName.value: company_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SearchCompanies, params)

    def exec_add_polymer(self, polymer_name: str, m_id, r_id, polymer_type: str, a_low, a_high, s_low, s_high,
                         mw_low, mw_high, notes: str):

        params = {DBObjects.Params.PolymerName.value: polymer_name,
                  DBObjects.Params.Manufacturer.value: m_id,
                  DBObjects.Params.RecCompany.value: r_id,
                  DBObjects.Params.PolymerType.value: polymer_type,
                  DBObjects.Params.AcrylateLow.value: a_low,
                  DBObjects.Params.AcrylateHigh.value: a_high,
                  DBObjects.Params.SulfonateLow.value: s_low,
                  DBObjects.Params.SulfonateHigh.value: s_high,
                  DBObjects.Params.MWLow.value: mw_low,
                  DBObjects.Params.MWHigh.value: mw_high,
                  DBObjects.Params.Discontinued.value: 0,
                  DBObjects.Params.Notes.value: notes}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddPolymer, params)

    def exec_move_inventory_item(self, inventory_id: int, loc_id: int):

        params = {DBObjects.Params.InvID.value: inventory_id, DBObjects.Params.LocID.value: loc_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.MovePolymerInvItem, params)

    def exec_update_inventory_item_mass(self, inventory_id: int, current_mass: int):

        params = {DBObjects.Params.InvID.value: inventory_id, DBObjects.Params.CurrMass.value: current_mass}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetPolymerInvItemMass, params)


class PolymerDBGUI(QWidget):

    def __init__(self, cnxn: db_tools.pyodbc.Connection, linked_main_window: QMainWindow):
        super(PolymerDBGUI, self).__init__()
        self.cnxn = None
        self.linked_main_window = linked_main_window
        lyt = QGridLayout()
        self.setLayout(lyt)

        polymer_name_label = QLabel(parent=self, text='Polymer Name:')
        company_name_label = QLabel(parent=self, text='Company Name:')
        acrylate_low_label = QLabel(parent=self, text='Acrylate Low:')
        acrylate_high_label = QLabel(parent=self, text='Acrylate High:')
        sulfonate_low_label = QLabel(parent=self, text='Sulfonate Low:')
        sulfonate_high_label = QLabel(parent=self, text='Sulfonate High:')
        mw_low_label = QLabel(parent=self, text='Mw Low:')
        mw_high_label = QLabel(parent=self, text='Mw High:')

        self.polymer_name_edit = QLineEdit(parent=self)
        self.polymer_name_edit.editingFinished.connect(self.check_enable_add_polymer)
        self.company_name_edit = QLineEdit(parent=self)
        self.company_name_edit.editingFinished.connect(self.check_enable_add_polymer)
        self.acrylate_low_edit = QLineEdit(parent=self)
        self.acrylate_low_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.acrylate_low_edit))
        self.acrylate_high_edit = QLineEdit(parent=self)
        self.acrylate_high_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.acrylate_high_edit))
        self.sulfonate_low_edit = QLineEdit(parent=self)
        self.sulfonate_low_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.sulfonate_low_edit))
        self.sulfonate_high_edit = QLineEdit(parent=self)
        self.sulfonate_high_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.sulfonate_high_edit))
        self.mw_low_edit = QLineEdit(parent=self)
        self.mw_low_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.mw_low_edit))
        self.mw_high_edit = QLineEdit(parent=self)
        self.mw_high_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.mw_high_edit))

        self.include_discontinued_checkbox = QCheckBox(parent=self, text='Include Discontinued?')
        self.search_button = QPushButton(parent=self, text='Search')
        self.search_button.clicked.connect(self.search_button_clicked)

        self.polymer_db_listbox = QListWidget(parent=self)
        self.polymer_db_listbox.itemClicked.connect(self.db_list_item_clicked)
        font = self.polymer_db_listbox.font()
        font.setFamily('Courier')
        self.polymer_db_listbox.setFont(font)

        self.add_polymer_button = QPushButton(parent=self, text='Add Polymer')
        self.add_polymer_button.clicked.connect(self.add_polymer_clicked)
        self.add_polymer_button.setEnabled(False)
        or_label = QLabel(parent=self, text='---- OR ----')
        or_label.setAlignment(Qt.AlignCenter)

        notes_label = QLabel(parent=self, text='Item info:')
        self.notes_text = QTextEdit(parent=self)
        self.notes_text.setReadOnly(True)
        self.notes_text.setFont(font)

        inventory_label = QLabel(parent=self, text='Inventory:')
        self.inventory_listbox = QListWidget(parent=self)
        self.inventory_listbox.setFont(font)
        self.inventory_listbox.itemClicked.connect(self.inventory_item_clicked)

        self.add_inventory_button = QPushButton(parent=self, text='Add Bottle')
        self.add_inventory_button.clicked.connect(self.add_inventory_clicked)
        self.move_inventory_button = QPushButton(parent=self, text='Move Bottle')
        self.move_inventory_button.clicked.connect(self.move_inventory_clicked)
        self.set_qty_edit = QLineEdit(parent=self)
        self.set_qty_edit.editingFinished.connect(lambda: self.vet_integer_edit(self.set_qty_edit,
                                                                                self.activate_qty_button))
        self.set_qty_button = QPushButton(parent=self, text='Update Mass')
        self.set_qty_button.clicked.connect(self.set_qty_clicked)

        lyt.addWidget(polymer_name_label, 0, 0, 1, 1)
        lyt.addWidget(self.polymer_name_edit, 0, 1, 1, 11)
        lyt.addWidget(company_name_label, 1, 0, 1, 1)
        lyt.addWidget(self.company_name_edit, 1, 1, 1, 11)
        lyt.addWidget(acrylate_low_label, 2, 0, 1, 1)
        lyt.addWidget(self.acrylate_low_edit, 2, 1, 1, 1)
        lyt.addWidget(acrylate_high_label, 2, 2, 1, 1)
        lyt.addWidget(self.acrylate_high_edit, 2, 3, 1, 1)
        lyt.addWidget(sulfonate_low_label, 2, 4, 1, 1)
        lyt.addWidget(self.sulfonate_low_edit, 2, 5, 1, 1)
        lyt.addWidget(sulfonate_high_label, 2, 6, 1, 1)
        lyt.addWidget(self.sulfonate_high_edit, 2, 7, 1, 1)
        lyt.addWidget(mw_low_label, 2, 8, 1, 1)
        lyt.addWidget(self.mw_low_edit, 2, 9, 1, 1)
        lyt.addWidget(mw_high_label, 2, 10, 1, 1)
        lyt.addWidget(self.mw_high_edit, 2, 11, 1, 1)
        lyt.addWidget(self.include_discontinued_checkbox, 3, 0, 1, 2)
        lyt.addWidget(self.search_button, 3, 10, 1, 2)

        lyt.addWidget(self.polymer_db_listbox, 4, 0, 1, 12)
        lyt.addWidget(or_label, 3, 8, 1, 2)
        lyt.addWidget(self.add_polymer_button, 3, 6, 1, 2)

        lyt.addWidget(notes_label, 5, 0, 1, 4)
        lyt.addWidget(self.notes_text, 6, 0, 2, 4)
        lyt.addWidget(inventory_label, 5, 4, 1, 8)
        lyt.addWidget(self.inventory_listbox, 6, 4, 1, 8)
        lyt.addWidget(self.add_inventory_button, 7, 4, 1, 2)
        lyt.addWidget(self.move_inventory_button, 7, 6, 1, 2)
        lyt.addWidget(self.set_qty_edit, 7, 9, 1, 1)
        lyt.addWidget(self.set_qty_button, 7, 10, 1, 2)

        self.set_connection(cnxn=cnxn)
        self.polymer_search_results = []
        self.inventory_search_results = []
        self.search_button_clicked()

    def set_connection(self, cnxn: db_tools.pyodbc.Connection):

        self.cnxn = PolymerConnection(cnxn=cnxn)

    @staticmethod
    def vet_integer_edit(edit: QLineEdit, finally_func=None):

        text = edit.text()
        if not text:
            return

        try:
            val = float(text)
            if val != int(val) or val < 0:
                raise ValueError

        except ValueError:
            edit.setText('')

        finally:
            if finally_func is not None:
                finally_func()

    def activate_qty_button(self):

        self.set_qty_button.setEnabled(False)

        if self.set_qty_edit.text():
            self.set_qty_button.setEnabled(True)

    def check_enable_add_polymer(self):

        self.add_polymer_button.setEnabled(False)

        if self.polymer_name_edit.text() and self.company_name_edit.text():
            self.add_polymer_button.setEnabled(True)

    def add_polymer_clicked(self):

        AddPolymerDialog(parent=self).exec_()

    def load_listbox_from_search(self, search_results: list):

        self.polymer_db_listbox.clear()

        for polymer in search_results:
            item = QListWidgetItem(parent=self.polymer_db_listbox)
            m_name = polymer[1]
            if m_name is None:
                m_name = ''
            r_name = polymer[2]
            if r_name is None:
                r_name = ''
            item.setText('{} Manufacturer: {} From: {}'.format(m_name.ljust(35), r_name.ljust(25), polymer[3]))

    def search_button_clicked(self):

        polymer_name = self.polymer_name_edit.text()
        company_name = self.company_name_edit.text()

        ac_low = self.acrylate_low_edit.text()
        if not ac_low:
            ac_low = 'NULL'
        else:
            ac_low = int(ac_low)
        ac_high = self.acrylate_high_edit.text()
        if not ac_high:
            ac_high = 'NULL'
        else:
            ac_high = int(ac_high)

        sulf_low = self.sulfonate_low_edit.text()
        if not sulf_low:
            sulf_low = 'NULL'
        else:
            sulf_low = int(sulf_low)
        sulf_high = self.sulfonate_high_edit.text()
        if not sulf_high:
            sulf_high = 'NULL'
        else:
            sulf_high = int(sulf_high)

        mw_low = self.mw_low_edit.text()
        if not mw_low:
            mw_low = 'NULL'
        else:
            mw_low = int(mw_low)
        mw_high = self.mw_high_edit.text()
        if not mw_high:
            mw_high = 'NULL'
        else:
            mw_high = int(mw_high)

        inc_disc = 0
        if self.include_discontinued_checkbox.isChecked():
            inc_disc = 1

        try:
             polymers = self.cnxn.exec_search_polymers(polymer_name, company_name, ac_low, ac_high,
                                                       sulf_low, sulf_high, mw_low, mw_high, inc_disc)
             self.polymer_search_results = polymers
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()
            return

        self.load_listbox_from_search(polymers)

        self.inventory_listbox.clear()
        self.add_inventory_button.setEnabled(False)
        self.move_inventory_button.setEnabled(False)
        self.set_qty_edit.setEnabled(False)
        self.set_qty_button.setEnabled(False)

    def db_list_item_clicked(self, _):

        i = self.polymer_db_listbox.currentIndex().row()
        info = self.polymer_search_results[i]
        for j, piece in enumerate(info):
            if piece is None:
                info[j] = ''
        info_string = 'Acrylate: {}-{}%\nATBS: {}-{}%\nMw: {}-{} MDa\n\nNotes: {}'
        self.notes_text.setText(info_string.format(*info[5:11], info[12]))

        self.load_inventory(info)

        self.add_inventory_button.setEnabled(True)
        self.move_inventory_button.setEnabled(False)
        self.set_qty_edit.blockSignals(True)
        self.set_qty_edit.clear()
        self.set_qty_edit.blockSignals(False)
        self.set_qty_edit.setEnabled(False)
        self.set_qty_button.setEnabled(False)

    def inventory_item_clicked(self, _):

        self.move_inventory_button.setEnabled(True)
        self.set_qty_edit.setEnabled(True)

    def load_inventory(self, info):

        self.inventory_listbox.clear()

        results = self.cnxn.exec_get_polymer_inventory(info[0])
        self.inventory_search_results = results
        inv_str = 'Lot #: {}, Mass: {}/{} g, Loc.: {}, {}'

        for result in results:
            item = QListWidgetItem(parent=self.inventory_listbox)
            item.setText(inv_str.format(result[1], result[4], result[3], result[5], result[6]))

    def add_inventory_clicked(self):

        try:
            AddPolymerInventoryItemDlg(parent=self).exec_()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def move_inventory_clicked(self):

        try:
            MoveDialog(parent=self).exec_()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def set_qty_clicked(self):

        self.linked_main_window.run_login_with_functions(self.set_qty)
        self.db_list_item_clicked(0)

    def set_qty(self):

        i = self.inventory_listbox.currentIndex().row()
        inventory_id = self.inventory_search_results[i][0]
        current_mass = int(self.set_qty_edit.text())
        self.cnxn.exec_update_inventory_item_mass(inventory_id, current_mass)


class AddPolymerDialog(QDialog):

    def __init__(self, parent: PolymerDBGUI):
        super(AddPolymerDialog, self).__init__(parent=parent)
        self.PDBGUI = parent
        self.setWindowTitle('Add New Polymer')
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 300), int(sf * 500))

        lyt = QGridLayout()
        self.setLayout(lyt)

        polymer_data_label = QLabel(parent=self, text='Data:')
        self.polymer_data_edit = QTextEdit(parent=self)
        self.polymer_data_edit.setReadOnly(True)
        polymer_type_label = QLabel(parent=self, text='Polymer Type:')
        self.polymer_type_combo = QComboBox(parent=self)
        self.polymer_type_combo.addItems(['synthetic', 'biopolymer'])
        self.polymer_type_combo.setCurrentIndex(0)
        manufacturer_label = QLabel(parent=self, text='Manufacturer:')
        self.manufacturer_edit = QLineEdit(parent=self)
        self.manufacturer_listbox = QListWidget(parent=self)
        self.manufacturer_listbox.currentRowChanged.connect(self.set_submit_active)
        self.manufacturer_edit.editingFinished.connect(lambda: self.search_companies(self.manufacturer_edit,
                                                                                     self.manufacturer_listbox))
        received_label = QLabel(parent=self, text='Received from:')
        self.received_company_edit = QLineEdit(parent=self)
        self.received_company_listbox = QListWidget(parent=self)
        self.received_company_listbox.currentRowChanged.connect(self.set_submit_active)
        self.received_company_edit.editingFinished.connect(lambda: self.search_companies(self.received_company_edit,
                                                                                         self.received_company_listbox))
        notes_label = QLabel(parent=self, text='Notes:')
        self.notes_text_edit = QTextEdit(parent=self)

        self.submit_button = QPushButton(parent=self, text='Submit to Database')
        self.submit_button.setDefault(False)
        self.submit_button.setAutoDefault(False)
        self.submit_button.clicked.connect(self.submit_clicked)
        self.submit_button.setEnabled(False)

        lyt.addWidget(polymer_data_label, 0, 0, 1, 2)
        lyt.addWidget(self.polymer_data_edit, 1, 0, 1, 2)
        lyt.addWidget(polymer_type_label, 2, 0, 1, 1)
        lyt.addWidget(self.polymer_type_combo, 2, 1, 1, 1)
        lyt.addWidget(manufacturer_label, 3, 0, 1, 1)
        lyt.addWidget(self.manufacturer_edit, 3, 1, 1, 1)
        lyt.addWidget(self.manufacturer_listbox, 4, 0, 1, 2)
        lyt.addWidget(received_label, 5, 0, 1, 1)
        lyt.addWidget(self.received_company_edit, 5, 1, 1, 1)
        lyt.addWidget(self.received_company_listbox, 6, 0, 1, 2)
        lyt.addWidget(notes_label, 7, 0, 1, 2)
        lyt.addWidget(self.notes_text_edit, 8, 0, 1, 2)
        lyt.addWidget(self.submit_button, 9, 0, 1, 2)

        self.manufacturer_results = list()
        self.received_company_results = list()

        self.load_polymer_data()

    def load_polymer_data(self):

        p_name = self.PDBGUI.polymer_name_edit.text()
        c_name = self.PDBGUI.company_name_edit.text()
        mw_low = self.PDBGUI.mw_low_edit.text()
        mw_high = self.PDBGUI.mw_high_edit.text()
        a_low = self.PDBGUI.acrylate_low_edit.text()
        a_high = self.PDBGUI.acrylate_high_edit.text()
        s_low = self.PDBGUI.sulfonate_low_edit.text()
        s_high = self.PDBGUI.sulfonate_high_edit.text()

        disp_str = 'Name: {}\n\nMw: {}-{} MDa, Acrylate: {}-{}%, Sulfonate: {}-{}%'
        self.polymer_data_edit.setText(disp_str.format(p_name, mw_low, mw_high, a_low, a_high, s_low, s_high))
        self.manufacturer_edit.setText(c_name)
        self.manufacturer_edit.editingFinished.emit()

    def search_companies(self, edit: QLineEdit, list_widget: QListWidget):

        if not edit.text():
            return

        list_widget.clear()
        results = self.PDBGUI.cnxn.exec_search_companies(edit.text())

        for result in results:
            item = QListWidgetItem(parent=list_widget)
            item.setText(result[1])

        if edit == self.manufacturer_edit:
            self.manufacturer_results = results
        else:
            self.received_company_results = results

    def set_submit_active(self, _):

        self.submit_button.setEnabled(False)

        if self.manufacturer_listbox.currentIndex().row() > -1 or \
                self.received_company_listbox.currentIndex().row() > -1:
            self.submit_button.setEnabled(True)

    def submit_clicked(self):

        self.PDBGUI.linked_main_window.run_login_with_functions(self.submit_polymer, self.close)

    def submit_polymer(self):

        p_name = self.PDBGUI.polymer_name_edit.text()
        i = self.manufacturer_listbox.currentIndex().row()
        if i > -1:
            m_id = self.manufacturer_results[i][0]
        else:
            m_id = 'NULL'
        j = self.received_company_listbox.currentIndex().row()
        if j > -1:
            r_id = self.received_company_results[j][0]
        else:
            r_id = 'NULL'

        p_type = self.polymer_type_combo.currentText()

        mw_low = self.PDBGUI.mw_low_edit.text()
        if not mw_low:
            mw_low = 'NULL'
        else:
            mw_low = float(mw_low)
        mw_high = self.PDBGUI.mw_high_edit.text()
        if not mw_high:
            mw_high = 'NULL'
        else:
            mw_high = float(mw_high)
        a_low = self.PDBGUI.acrylate_low_edit.text()
        if not a_low:
            a_low = 'NULL'
        else:
            a_low = int(a_low)
        a_high = self.PDBGUI.acrylate_high_edit.text()
        if not a_high:
            a_high = 'NULL'
        else:
            a_high = int(a_high)
        s_low = self.PDBGUI.sulfonate_low_edit.text()
        if not s_low:
            s_low = 'NULL'
        else:
            s_low = int(s_low)
        s_high = self.PDBGUI.sulfonate_high_edit.text()
        if not s_high:
            s_high = 'NULL'
        else:
            s_high = int(s_high)

        notes = self.notes_text_edit.toPlainText()
        if not notes:
            notes = 'NULL'

        self.PDBGUI.cnxn.exec_add_polymer(p_name, m_id, r_id, p_type, a_low, a_high, s_low, s_high, mw_low, mw_high,
                                          notes)


class AddPolymerInventoryItemDlg(QDialog):

    def __init__(self, parent: PolymerDBGUI):
        super(AddPolymerInventoryItemDlg, self).__init__(parent=parent)
        self.PDBGUI = parent
        i = parent.polymer_db_listbox.currentIndex().row()
        polymer = parent.polymer_search_results[i]

        self.setWindowTitle('Add new bottle: {}'.format(polymer[1]))
        self.setFixedSize(int(parent.linked_main_window.sf * 300), int(parent.linked_main_window.sf * 200))

        lyt = QGridLayout()
        self.setLayout(lyt)

        lot_num_label = QLabel(parent=self, text='Lot # (Optional):')
        self.lot_num_edit = QLineEdit(parent=self)
        rec_date_label = QLabel(parent=self, text='Rec. Date (MM/DD/YYYY):')
        self.rec_date_edit = QLineEdit(parent=self)
        self.rec_date_edit.editingFinished.connect(self.vet_date_edit)
        self.set_date_edit_to_today()
        init_mass_label = QLabel(parent=self, text='Initial Mass:')
        self.init_mass_edit = QLineEdit(parent=self)
        self.init_mass_edit.editingFinished.connect(self.vet_init_mass_edit)
        room_label = QLabel(parent=self, text='Room:')
        self.room_selector = QComboBox(parent=self)
        self.room_selector.currentIndexChanged.connect(self.load_loc_combo)
        loc_label = QLabel(parent=self, text='Location:')
        self.loc_selector = QComboBox(parent=self)
        self.loc_selector.currentIndexChanged.connect(self.loc_selected)

        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_clicked)

        lyt.addWidget(lot_num_label, 0, 0, 1, 1)
        lyt.addWidget(self.lot_num_edit, 0, 1, 1, 1)
        lyt.addWidget(rec_date_label, 1, 0, 1, 1)
        lyt.addWidget(self.rec_date_edit, 1, 1, 1, 1)
        lyt.addWidget(init_mass_label, 2, 0, 1, 1)
        lyt.addWidget(self.init_mass_edit, 2, 1, 1, 1)
        lyt.addWidget(room_label, 3, 0, 1, 1)
        lyt.addWidget(self.room_selector, 3, 1, 1, 1)
        lyt.addWidget(loc_label, 4, 0, 1, 1)
        lyt.addWidget(self.loc_selector, 4, 1, 1, 1)
        lyt.addWidget(self.submit_button, 5, 0, 1, 2)

        self.rooms = []
        self.rm_locations = []

        self.load_room_combo()

    def load_room_combo(self):

        self.room_selector.blockSignals(True)

        self.room_selector.clear()
        self.loc_selector.clear()
        rooms = self.PDBGUI.cnxn.exec_get_rooms()
        self.rooms = rooms
        rooms_list = [' ']

        for room in rooms:
            rooms_list.append(room[1])

        self.room_selector.addItems(rooms_list)

        self.room_selector.blockSignals(False)

    def load_loc_combo(self, i: int):

        self.loc_selector.blockSignals(True)

        self.loc_selector.clear()
        room_id = self.rooms[i - 1][0]
        self.rm_locations = self.PDBGUI.cnxn.exec_get_rm_locations(room_id)

        locs_list = [' ']

        for loc in self.rm_locations:
            locs_list.append(loc[2])

        self.loc_selector.addItems(locs_list)

        self.loc_selector.blockSignals(False)

    def loc_selected(self, _):

        self.check_enable_submit()

    @staticmethod
    def create_date_string(month: int, day: int, year: int) -> str:

        month_str = str(month)
        if month < 10:
            month_str = '0' + month_str
        day_str = str(day)
        if day < 10:
            day_str = '0' + day_str
        year_str = str(year)

        return '{}/{}/{}'.format(month_str, day_str, year_str)

    def set_date_edit_to_today(self):

        today = datetime.date.today()
        self.set_date_edit_to_date(today.month, today.day, today.year)

    def set_date_edit_to_date(self, month: int, day: int, year: int):

        self.rec_date_edit.blockSignals(True)
        self.rec_date_edit.setText(self.create_date_string(month, day, year))
        self.rec_date_edit.blockSignals(False)

    def vet_date_edit(self):

        date = self.rec_date_edit.text().split('/')
        if len(date) != 3:
            self.set_date_edit_to_today()
            return

        month = date[0]
        day = date[1]
        year = date[2]

        try:
            month = int(month)
            day = int(day)
            year = int(year)
            datetime.date(year, month, day)

        except ValueError:
            self.set_date_edit_to_today()
            return

        self.set_date_edit_to_date(month, day, year)

        self.check_enable_submit()

    def vet_init_mass_edit(self):

        txt = self.init_mass_edit.text()

        if not txt:
            return

        try:
            mass = int(txt)
            if mass < 0:
                raise ValueError

        except ValueError:
            self.init_mass_edit.blockSignals(True)
            self.init_mass_edit.setText('')
            self.init_mass_edit.blockSignals(False)
            self.check_enable_submit()
            return

        self.init_mass_edit.setText(str(mass))
        self.check_enable_submit()

    def check_enable_submit(self):

        self.submit_button.setEnabled(False)

        if not self.init_mass_edit.text():
            return

        if self.room_selector.currentIndex() < 1:
            return

        if self.loc_selector.currentIndex() < 1:
            return

        self.submit_button.setEnabled(True)

    def submit_clicked(self):

        self.PDBGUI.linked_main_window.run_login_with_functions(self.submit_polymer_inventory_item)
        self.close()

    def submit_polymer_inventory_item(self):

        i = self.PDBGUI.polymer_db_listbox.currentIndex().row()
        polymer_id = self.PDBGUI.polymer_search_results[i][0]

        lot_num = self.lot_num_edit.text()
        if not lot_num:
            lot_num = 'NULL'

        rec_date = self.rec_date_edit.text()
        init_mass = self.init_mass_edit.text()
        i = self.loc_selector.currentIndex()
        loc_id = self.rm_locations[i - 1][0]

        self.PDBGUI.cnxn.exec_add_polymer_inventory_by_id(polymer_id, lot_num, rec_date, init_mass, loc_id)


class MoveDialog(QDialog):

    def __init__(self, parent: PolymerDBGUI):
        super(MoveDialog, self).__init__(parent=parent)
        self.PDBGUI = parent
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 450), int(sf * 100))
        self.setWindowTitle('Move item')

        lyt = QGridLayout()
        self.setLayout(lyt)

        move_room_and_loc_label = QLabel(parent=self, text='To Room, at Location:')
        self.move_room_combo = QComboBox(parent=self)
        self.move_loc_combo = QComboBox(parent=self)
        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.clicked.connect(self.submit_clicked)

        lyt.addWidget(move_room_and_loc_label, 0, 0, 1, 1)
        lyt.addWidget(self.move_room_combo, 0, 1, 1, 1)
        lyt.addWidget(self.move_loc_combo, 0, 2, 1, 1)
        lyt.addWidget(self.submit_button, 1, 2, 1, 1)

        rooms = parent.cnxn.exec_get_rooms()
        self.rooms = rooms
        self.rm_locations = list()
        rooms_list = list()

        for room in rooms:
            rooms_list.append(room[1])

        self.move_room_combo.addItems(rooms_list)
        self.move_room_combo.currentIndexChanged.connect(self.room_index_changed)
        self.move_room_combo.currentIndexChanged.emit(0)

    def room_index_changed(self, ind: int):

        room_id = self.rooms[ind][0]
        rm_locations = self.parent().cnxn.exec_get_rm_locations(room_id=room_id)

        self.rm_locations = rm_locations
        rm_locations_list = list()

        for rm_location in rm_locations:
            rm_locations_list.append(rm_location[2])

        self.move_loc_combo.clear()
        self.move_loc_combo.addItems(rm_locations_list)

    def submit_clicked(self):

        self.parent().linked_main_window.run_login_with_functions(self.submit_move,
                                                                  lambda: self.PDBGUI.db_list_item_clicked(0))
        self.close()

    def submit_move(self):

        inv_ids = self.PDBGUI.inventory_search_results
        new_loc_id = self.rm_locations[self.move_loc_combo.currentIndex()][0]

        index = self.PDBGUI.inventory_listbox.currentIndex()

        inventory_id = inv_ids[index.row()][0]

        print(inventory_id, new_loc_id)
        self.parent().cnxn.exec_move_inventory_item(inventory_id, new_loc_id)
