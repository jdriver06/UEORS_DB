
from PyQt5.QtWidgets import QWidget, QMainWindow, QGridLayout, QListWidget, QLabel, QListWidgetItem, QLineEdit, QDialog,\
    QTextEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QCheckBox
from PyQt5.QtGui import QPixmap, QKeyEvent
from PyQt5.Qt import pyqtSignal, Qt
import db_tools
from db_tools import DBObjects
from os import startfile
import datetime


class OSHAConnection:

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

    def exec_get_chemical_hazards_and_ppe(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetChemHazards, params)[0]

    def exec_search_chemicals(self, search_str: str):

        params = {DBObjects.Params.SearchStr.value: search_str}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SearchChems, params)

    def exec_get_avoid_notes_safety(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.AvoidNotesSafety, params)[0]

    def exec_change_avoid_notes_safety(self, chemical_name: str, avoid: str, notes: str, safety: str):

        P = DBObjects.Params
        params = {P.ChemName.value: chemical_name, P.Avoid.value: avoid, P.Notes.value: notes, P.Safety.value: safety}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.ChangeAvoidNotesSafety, params)

    def exec_set_sds_file_path(self, chemical_name: str, sds_file_path: str):

        params = {DBObjects.Params.ChemName.value: chemical_name, DBObjects.Params.SDSFPath.value: sds_file_path}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetSDSFPath, params)

    def exec_get_sds_file_path(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetSDSFPath, params)[0]

    def exec_get_chemical_id_for_name(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.ChemIDforName, params)[0][0]

    def exec_get_chemical_synonyms_and_cas_1_perc_1(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetSynsCAS, params)[0]

    def exec_get_additional_cas_nums(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetAddCAS, params)

    def exec_get_chemical_inventory(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetInvforChemName, params)

    def exec_get_empty_chemical_inventory(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetEmptyInvforChemName, params)

    def update_inventory_quantity(self, inventory_id: int, qty: float):

        return self.update_table_key_value(DBObjects.Tables.ChemInv, DBObjects.Columns.Qty,
                                           DBObjects.Columns.InvID.value, inventory_id, str(qty))

    def reduce_inventory_quantity(self, inventory_id: int, red: float):

        params = {DBObjects.Params.InvID.value: inventory_id, DBObjects.Params.Red.value: red}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RedInvQty, params)

    def reduce_empty_inventory_quantity(self, inventory_id: int, red: float):

        params = {DBObjects.Params.EmptyInvID.value: inventory_id, DBObjects.Params.Red.value: red}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RedEmptyInvQty, params)

    def exec_add_item_to_watchlist(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddItemtoWatchlist, params)

    def exec_get_user_watchlist(self, username: str):

        params = {DBObjects.Params.UserName.value: username}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetUserWatchlist, params)

    def exec_remove_item_from_watchlist(self, username: str, chemical_name: str):

        params = {DBObjects.Params.UserName.value: username, DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RemoveItemfromWatchlist, params)

    def exec_add_order_request_by_chemical_name(self, chemical_name: str, qty: int, urgency_id: int, notes: str):

        DBO = DBObjects
        params = {DBO.Params.ChemName.value: chemical_name, DBO.Params.Qty.value: qty,
                  DBO.Params.UrgencyID.value: urgency_id, DBO.Params.Notes.value: notes}
        return self.exec_stored_procedure_with_params_no_fetchall(DBO.Procedures.AddOrderReqbyChemNameFull, params)

    def exec_get_active_order_requests(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetActiveReq, {})

    def exec_get_all_orders(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetAllOrders, {})

    def exec_place_chemical_order(self, container_id: int, qty: int, order_date: str):

        params = {DBObjects.Params.ContID.value: container_id, DBObjects.Params.Qty.value: qty,
                  DBObjects.Params.OrderDate.value: order_date}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.PlaceChemOrder, params)

    def exec_get_containers_for_chemical_name(self, chemical_name: str):

        params = {DBObjects.Params.ChemName.value: chemical_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetContinersforChemName, params)

    def get_all_units(self):

        return db_tools.select_column_from_table(self._cnxn, DBObjects.Tables.InvUnits.value,
                                                 DBObjects.Columns.UnitAbbr.value)

    def insert_new_container(self, chemical_id: int, unit_abbrev: str, size: float):

        values = [chemical_id, unit_abbrev, size, 0]
        return db_tools.insert_values_into_table(self._cnxn, DBObjects.Tables.ChemContainers.value, values)

    def insert_new_order(self, container_id: int, qty: int, date: str):

        values = [container_id, qty, date]
        return db_tools.insert_values_into_table(self._cnxn, DBObjects.Tables.ChemOrders.value, values)

    def exec_get_rooms(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRooms, {})

    def exec_get_rm_locations(self, room_id: int):

        params = {DBObjects.Params.RoomID.value: room_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRoomLocs, params)

    def exec_chemical_order_received(self, order_id: int, qty: int, order_received_date: str, loc_id: int):

        params = {DBObjects.Params.OrderID.value: order_id, DBObjects.Params.Qty.value: qty,
                  DBObjects.Params.OrderRecDate.value: order_received_date, DBObjects.Params.LocID.value: loc_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.ChemOrderRec, params)

    def get_received_for_order(self, order_id: int):

        return db_tools.select_all_from_table_where_key_equals(self._cnxn, DBObjects.Tables.ChemOrdersRec.value,
                                                               DBObjects.Columns.OrderID.value, order_id).fetchall()

    def exec_move_inventory_item(self, inventory_id: int, move_qty: float, new_loc_id: int):

        params = {DBObjects.Params.InvID.value: inventory_id, DBObjects.Params.MoveQty.value: move_qty,
                  DBObjects.Params.NewLocID.value: new_loc_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.MoveInvItem, params)

    def exec_move_empty_inventory_item(self, inventory_id: int, move_qty: float, new_loc_id: int):

        params = {DBObjects.Params.EmptyInvID.value: inventory_id, DBObjects.Params.MoveQty.value: move_qty,
                  DBObjects.Params.NewLocID.value: new_loc_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.MoveEmptyInvItem, params)


class EnterEdit(QLineEdit):

    enterPressed = pyqtSignal()

    def __init__(self, parent):
        super(EnterEdit, self).__init__(parent=parent)

    def keyPressEvent(self, a0: QKeyEvent):
        super(EnterEdit, self).keyPressEvent(a0)
        if a0.key() == Qt.Key_Return:
            self.enterPressed.emit()


class OSHADBGUI(QWidget):

    new_order_requests = pyqtSignal()

    def __init__(self, cnxn: db_tools.pyodbc.Connection, linked_main_window: QMainWindow):
        super(OSHADBGUI, self).__init__()
        self.cnxn = None
        self.linked_main_window = linked_main_window
        lyt = QGridLayout()
        self.setLayout(lyt)

        self.search_edit = EnterEdit(parent=self)
        self.search_edit.enterPressed.connect(self.search_for_chemicals)
        lyt.addWidget(self.search_edit, 0, 0, 1, 1)

        database_label = QLabel(parent=self, text='Chemical Database:')
        lyt.addWidget(database_label, 1, 0, 1, 1)
        self.chemical_db_list = QListWidget(parent=self)
        inventory_font = self.chemical_db_list.font()
        inventory_font.setFamily('Courier')
        self.chemical_db_list.setFont(inventory_font)
        lyt.addWidget(self.chemical_db_list, 2, 0, 1, 1)
        inventory_label = QLabel(parent=self, text='Inventory:')
        lyt.addWidget(inventory_label, 4, 0, 1, 1)
        self.chemical_inv_list = QListWidget(parent=self)
        self.chemical_inv_list.setFont(inventory_font)
        self.chemical_inv_list.setFixedHeight(int(linked_main_window.sf * 70))
        lyt.addWidget(self.chemical_inv_list, 5, 0, 1, 1)

        self.adjust_inv_qty_widget = QWidget(parent=self)
        a_lyt = QGridLayout()
        self.adjust_inv_qty_widget.setLayout(a_lyt)

        self.watch_button = QPushButton(parent=self, text='Watch')
        self.watch_button.clicked.connect(self.watch_button_clicked)
        self.view_watchlist_button = QPushButton(parent=self, text='View Watchlist')
        self.view_watchlist_button.clicked.connect(self.view_watchlist_clicked)
        self.request_button = QPushButton(parent=self, text='Request')
        self.request_button.clicked.connect(self.add_order_request)
        self.view_requests_button = QPushButton(parent=self, text='View Requests')
        self.view_requests_button.clicked.connect(self.get_active_order_requests)
        self.order_button = QPushButton(parent=self, text='Order')
        self.order_button.clicked.connect(self.order_form)
        self.view_orders_button = QPushButton(parent=self, text='View Orders')
        self.view_orders_button.clicked.connect(self.view_orders)
        self.watch_button.setEnabled(False)
        self.request_button.setEnabled(False)
        self.order_button.setEnabled(False)

        a_lyt.addWidget(self.watch_button, 0, 0, 1, 1)
        a_lyt.addWidget(self.view_watchlist_button, 1, 0, 1, 1)
        a_lyt.addWidget(self.request_button, 0, 1, 1, 1)
        a_lyt.addWidget(self.view_requests_button, 1, 1, 1, 1)
        a_lyt.addWidget(self.order_button, 0, 2, 1, 1)
        a_lyt.addWidget(self.view_orders_button, 1, 2, 1, 1)

        self.adjust_inv_qty_widget_2 = QWidget(parent=self)
        a_lyt_2 = QGridLayout()
        self.adjust_inv_qty_widget_2.setLayout(a_lyt_2)

        self.move_inv_button = QPushButton(parent=self, text='Move...')
        self.move_inv_button.clicked.connect(self.move_inventory_clicked)
        reduce_qty_label = QLabel(parent=self, text='Reduce quantity by:')
        reduce_qty_label.setAlignment(Qt.AlignRight)
        self.adjust_qty_edit = QLineEdit(parent=self.adjust_inv_qty_widget)
        self.adjust_qty_edit.setFixedWidth(int(linked_main_window.sf * 50))
        self.adjust_qty_button = QPushButton(parent=self.adjust_inv_qty_widget, text='Submit')
        self.adjust_qty_button.setFixedWidth(int(linked_main_window.sf * 100))
        self.adjust_qty_button.clicked.connect(self.adjust_inv_qty)
        a_lyt_2.addWidget(self.move_inv_button, 0, 0, 1, 1)
        a_lyt_2.addWidget(reduce_qty_label, 0, 1, 1, 1)
        a_lyt_2.addWidget(self.adjust_qty_edit, 0, 2, 1, 1)
        a_lyt_2.addWidget(self.adjust_qty_button, 0, 3, 1, 1)
        self.move_inv_button.setEnabled(False)
        self.adjust_qty_button.setEnabled(False)
        self.adjust_qty_edit.setEnabled(False)

        self.chemical_inv_list.itemClicked.connect(self.init_adjust_qty)

        self.inventory_ids = []
        self.empty_inventory_ids = []

        lyt.addWidget(self.adjust_inv_qty_widget, 3, 0, 1, 1)
        lyt.addWidget(self.adjust_inv_qty_widget_2, 6, 0, 1, 1)

        self.hazards_widget = QWidget(parent=self)
        w_lyt = QGridLayout()
        self.hazards_widget.setLayout(w_lyt)
        self.hazards_widget.setFixedWidth(330)
        # self.hazards_widget.setFixedHeight(550)
        lyt.addWidget(self.hazards_widget, 0, 1, 6, 1)

        self.hazards_labels = []
        self.hazards_pictures = ['flammable_symbol.jpg',
                                 'caustic_symbol.jpg',
                                 'oxidizer_symbol.jpg',
                                 'reducer_symbol.jpg',
                                 'explosive_symbol.jpg',
                                 'toxic_symbol.jpg',
                                 'health_hazard_symbol.jpg',
                                 'warning.jpg',
                                 'gas_cylinder_symbol.jpg']

        self.ppe_labels = []
        self.ppe_pictures = ['6 mil nitrile.jpg',
                             '8 mil nitrile.jpg',
                             '15 mil nitrile.jpg',
                             'viton.jpg',
                             'butyl.jpg',
                             'white chem.jpg',
                             'face shield.jpg',
                             'apron.jpg',
                             'hood.jpg']

        self.pixmaps = []
        self.ppe_pixmaps = []
        self.blank_pixmap = QPixmap('blank_symbol.jpg')

        for i, pic in enumerate(self.hazards_pictures):

            pixmap = QPixmap(pic)
            self.pixmaps.append(pixmap)
            label = QLabel(parent=self.hazards_widget)
            label.setPixmap(self.blank_pixmap)
            label.setScaledContents(True)
            label.setFixedSize(100, 100)
            self.hazards_labels.append(label)
            if i < 3:
                w_lyt.addWidget(label, 0, i, 1, 1)
            elif i < 6:
                w_lyt.addWidget(label, 1, i - 3, 1, 1)
            else:
                w_lyt.addWidget(label, 2, i - 6, 1, 1)

        for i, pic in enumerate(self.ppe_pictures):

            pixmap = QPixmap(pic)
            self.ppe_pixmaps.append(pixmap)
            if i < 4:
                label = QLabel(parent=self.hazards_widget)
                label.setPixmap(self.blank_pixmap)
                label.setScaledContents(True)
                label.setFixedSize(100, 100)
                self.ppe_labels.append(label)
            if i < 3:
                w_lyt.addWidget(label, 3, i, 1, 1)
            elif i < 4:
                w_lyt.addWidget(label, 4, i - 3, 1, 1)
            else:
                pass

        self.chemical_db_list.itemClicked.connect(self.chemical_clicked)
        self.chemical_db_list.itemDoubleClicked.connect(self.chemical_double_clicked)
        self.set_connection(cnxn=cnxn)

        self.db_inspector = None
        self.request_dialog = None
        self.watchlist_dialog = None

        self.search_for_chemicals()
        self.current_order_requests = list()

        self.live_updates = False

    def set_connection(self, cnxn: db_tools.pyodbc.Connection):

        self.cnxn = OSHAConnection(cnxn=cnxn)

    def set_live_updates(self, live_updates: bool):

        self.live_updates = live_updates

    def chemical_clicked(self, item: QListWidgetItem):

        c_item = self.chemical_db_list.currentItem()

        activate = False
        if c_item == item:
            activate = True

        self.watch_button.setEnabled(activate)
        self.request_button.setEnabled(activate)
        self.order_button.setEnabled(activate)

        self.adjust_qty_edit.clear()
        self.adjust_qty_edit.setEnabled(False)
        self.adjust_qty_button.setEnabled(False)
        self.move_inv_button.setEnabled(False)

        chem_name = item.text()
        hazards = self.cnxn.exec_get_chemical_hazards_and_ppe(chemical_name=chem_name)

        for label in self.hazards_labels:
            label.clear()
            label.setPixmap(self.blank_pixmap)

        hazard_dict = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7}

        i = 0
        for key, value in hazard_dict.items():
            if hazards[key]:
                self.hazards_labels[i].clear()
                self.hazards_labels[i].setPixmap(self.pixmaps[value])
                i += 1

        if hazards[8] == 'gas':
            self.hazards_labels[i].clear()
            self.hazards_labels[i].setPixmap(self.pixmaps[8])

        try:

            for j in range(4):
                self.ppe_labels[j].clear()
                self.ppe_labels[j].setPixmap(self.blank_pixmap)

            glove_code = hazards[9]
            self.ppe_labels[0].setPixmap(self.ppe_pixmaps[glove_code - 1])
            i = 1
            if hazards[10]:
                self.ppe_labels[i].setPixmap(self.ppe_pixmaps[6])
                i += 1
            if hazards[11]:
                self.ppe_labels[i].setPixmap(self.ppe_pixmaps[7])
                i += 1
            if hazards[12]:
                self.ppe_labels[i].setPixmap(self.ppe_pixmaps[8])
        except Exception as e:
            print(e)

        inventory = self.cnxn.exec_get_chemical_inventory(chemical_name=chem_name)
        empty_inventory = self.cnxn.exec_get_empty_chemical_inventory(chemical_name=chem_name)

        self.chemical_inv_list.clear()
        self.inventory_ids = []
        self.empty_inventory_ids = []

        if not inventory and not empty_inventory:
            return

        for entry in inventory:
            self.inventory_ids.append(entry[0])
            container_size = entry[3]
            units = entry[2]
            qty = entry[4]
            room = entry[6]
            room_loc = entry[7]

            inv_item = QListWidgetItem(parent=self.chemical_inv_list)
            inv_item.setText('{} x {} {} in {}, {}'.format(qty, container_size, units, room, room_loc))
            # self.chemical_inv_list.addItem(inv_item)

        for entry in empty_inventory:
            self.empty_inventory_ids.append(entry[0])
            container_size = entry[3]
            units = entry[2]
            qty = entry[4]
            room = entry[6]
            room_loc = entry[7]

            inv_item = QListWidgetItem(parent=self.chemical_inv_list)
            inv_item.setText('{} x {} {} (EMPTY) in {}, {}'.format(qty, container_size, units, room, room_loc))

    def chemical_double_clicked(self, item: QListWidgetItem):

        if self.db_inspector is None:
            self.db_inspector = OSHADBItemInspector(self, item)
            self.db_inspector.show()
            self.chemical_db_list.itemClicked.connect(self.db_inspector.load_item)

    def search_for_chemicals(self):

        txt = self.search_edit.text()
        if len(txt) > 98:
            txt = txt[:98]

        search_str = '%' + txt + '%'

        chemicals = self.cnxn.exec_search_chemicals(search_str)
        self.load_from_search(chemicals)

        self.watch_button.setEnabled(False)
        self.request_button.setEnabled(False)
        self.order_button.setEnabled(False)

        self.adjust_qty_edit.clear()
        self.adjust_qty_edit.setEnabled(False)
        self.adjust_qty_button.setEnabled(False)
        self.move_inv_button.setEnabled(False)

    def load_from_search(self, chemicals: list):

        self.chemical_db_list.clear()

        for chemical in chemicals:
            item = QListWidgetItem(chemical[0])
            self.chemical_db_list.addItem(item)
            if chemical[1]:
                item.setForeground(Qt.red)

    def init_adjust_qty(self, _):

        # self.adjust_qty_edit.clear()
        # qty = item.text().split('x')[0].rstrip()
        self.adjust_qty_edit.setText('1')
        self.adjust_qty_edit.setEnabled(True)
        self.adjust_qty_button.setEnabled(True)
        self.move_inv_button.setEnabled(True)

    def watch_button_clicked(self):

        self.linked_main_window.run_login_with_functions(self.watch_item, self.refresh_watchlist)

    def watch_item(self):

        chemical_name = self.chemical_db_list.currentItem().text()
        self.cnxn.exec_add_item_to_watchlist(chemical_name=chemical_name)

    def refresh_watchlist(self):

        if self.watchlist_dialog is not None:
            self.watchlist_dialog.load_watchlist()
        
    def view_watchlist_clicked(self):

        if self.watchlist_dialog is not None:
            return

        dlg = ViewWatchlistDialog(parent=self)
        self.watchlist_dialog = dlg
        dlg.show()

    def add_order_request(self):

        CreateRequestDialog(parent=self).exec_()

        # self.linked_main_window.run_login_with_functions(self.connection_add_order_request, self.refresh_inventory)

    def connection_add_order_request(self, chemical_name: str, qty: int, urgency_id: int, notes: str):

        self.cnxn.exec_add_order_request_by_chemical_name(chemical_name=chemical_name, qty=qty, urgency_id=urgency_id,
                                                          notes=notes)

    def get_active_order_requests(self):

        if self.request_dialog is not None:
            return

        self.request_dialog = RequestDialog(parent=self)
        self.current_order_requests = self.request_dialog.current_order_requests
        self.new_order_requests.connect(self.request_dialog.load_requests)
        self.request_dialog.show()

    def check_active_orders(self):

        order_requests = self.cnxn.exec_get_active_order_requests()
        no_new_requests = True
        for order in order_requests:
            if order not in self.current_order_requests:
                no_new_requests = False

        self.current_order_requests = order_requests

        if not self.live_updates:
            return

        if not no_new_requests:
            if self.request_dialog is None:
                self.request_dialog = RequestDialog(parent=self)
                self.new_order_requests.connect(self.request_dialog.load_requests)
                self.request_dialog.show()

            self.new_order_requests.emit()
        else:
            print('No new requests.')

    def order_form(self):

        try:
            OrderDialog(parent=self).exec_()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def view_orders(self):

        try:
            ViewOrdersDialog(parent=self).exec_()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def move_inventory_clicked(self):

        MoveDialog(self).exec_()

    def adjust_inv_qty(self):

        self.linked_main_window.run_login_with_functions(self.connection_update_quantity, self.refresh_inventory)

    def connection_update_quantity(self):

        red = self.adjust_qty_edit.text()
        red = float(red)
        if red < 0.:
            raise ValueError('Quantity must be non-negative.')

        i = self.chemical_inv_list.currentRow()
        if i < len(self.inventory_ids):
            inv_id = self.inventory_ids[i]
            self.cnxn.reduce_inventory_quantity(inv_id, red)
        else:
            if int(red) != red:
                raise ValueError('Empty quantity must be an integer')
            i -= len(self.inventory_ids)
            inv_id = self.empty_inventory_ids[i]
            self.cnxn.reduce_empty_inventory_quantity(inv_id, int(red))

    def refresh_inventory(self):

        try:
            self.chemical_db_list.clicked.emit(self.chemical_db_list.currentIndex())
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def closeEvent(self, a0):
        dbi = self.db_inspector
        rd = self.request_dialog
        super(OSHADBGUI, self).closeEvent(a0)
        if dbi is not None:
            dbi.close()
        if rd is not None:
            rd.close()


class OSHADBItemInspector(QDialog):

    def __init__(self, parent: OSHADBGUI, item: QListWidgetItem):
        super(OSHADBItemInspector, self).__init__(parent=parent)

        self.parent = parent
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 600), int(sf * 300))
        self.item = item

        lyt = QGridLayout()
        self.setLayout(lyt)

        self.syn_1_label = QLabel(parent=self, text='Synonym 1:')
        self.syn_2_label = QLabel(parent=self, text='Synonym 2:')
        self.syn_3_label = QLabel(parent=self, text='Synonym 3:')
        spacer_label = QLabel(parent=self, text=' ')

        self.composition_list = QListWidget(parent=self)
        # self.composition_list.setReadOnly(True)

        avoid_label = QLabel(parent=self, text='Avoid:')
        notes_label = QLabel(parent=self, text='Notes:')
        safety_label = QLabel(parent=self, text='Safety Details:')

        self.avoid_tedit = QTextEdit(parent=self)
        self.notes_tedit = QTextEdit(parent=self)
        self.safety_tedit = QTextEdit(parent=self)

        self.avoid_tedit.textChanged.connect(lambda: self.set_tedit_color(self.avoid_tedit))
        self.notes_tedit.textChanged.connect(lambda: self.set_tedit_color(self.notes_tedit))
        self.safety_tedit.textChanged.connect(lambda: self.set_tedit_color(self.safety_tedit))

        self.avoid_notes = ''
        self.notes = ''
        self.safety_notes = ''

        self.notes_changed = [False, False, False]

        self.submit_changes_button = QPushButton(parent=self, text='Submit Changes')
        self.submit_changes_button.clicked.connect(self.submit_changes_clicked)

        self.sds_button = QPushButton(parent=self, text='Select SDS')
        self.sds_button.clicked.connect(self.select_sds)

        self.open_sds_button = QPushButton(parent=self, text='Open SDS')
        self.open_sds_button.clicked.connect(self.open_sds)

        lyt.addWidget(self.syn_1_label, 0, 0, 1, 2)
        lyt.addWidget(self.syn_2_label, 1, 0, 1, 2)
        lyt.addWidget(self.syn_3_label, 2, 0, 1, 2)
        lyt.addWidget(spacer_label, 3, 0, 1, 1)
        lyt.addWidget(self.composition_list, 0, 2, 3, 1)

        lyt.addWidget(avoid_label, 4, 0, 1, 1)
        lyt.addWidget(notes_label, 4, 1, 1, 1)
        lyt.addWidget(safety_label, 4, 2, 1, 1)

        lyt.addWidget(self.avoid_tedit, 5, 0, 1, 1)
        lyt.addWidget(self.notes_tedit, 5, 1, 1, 1)
        lyt.addWidget(self.safety_tedit, 5, 2, 1, 1)

        lyt.addWidget(self.submit_changes_button, 6, 0, 1, 1)
        lyt.addWidget(self.sds_button, 6, 1, 1, 1)
        lyt.addWidget(self.open_sds_button, 6, 2, 1, 1)
        self.sds_file_path = ''

        try:
            self.load_item(item)
        except Exception as e:
            print(e)

    def load_item(self, item: QListWidgetItem):

        self.setWindowTitle('DB Inspector: {}'.format(item.text()))

        ans = self.parent.cnxn.exec_get_avoid_notes_safety(item.text())
        avoid = ''
        notes = ''
        safety = ''
        if ans[0] is not None:
            avoid = ans[0]
        if ans[1] is not None:
            notes = ans[1]
        if ans[2] is not None:
            safety = ans[2]

        self.avoid_notes = avoid
        self.notes = notes
        self.safety_notes = safety

        self.avoid_tedit.setStyleSheet('QTextEdit {background: white};')
        self.notes_tedit.setStyleSheet('QTextEdit {background: white};')
        self.safety_tedit.setStyleSheet('QTextEdit {background: white};')

        self.set_tedit_text(self.avoid_tedit, avoid)
        self.set_tedit_text(self.notes_tedit, notes)
        self.set_tedit_text(self.safety_tedit, safety)

        self.notes_changed = [False, False, False]
        self.submit_changes_button.setEnabled(False)

        syns_and_cas_1 = self.parent.cnxn.exec_get_chemical_synonyms_and_cas_1_perc_1(item.text())
        self.syn_1_label.setText('Synonym 1: {}'.format(syns_and_cas_1[0]))
        self.syn_2_label.setText('Synonym 2: {}'.format(syns_and_cas_1[1]))
        self.syn_3_label.setText('Synonym 3: {}'.format(syns_and_cas_1[2]))

        self.composition_list.clear()
        list_item = QListWidgetItem()
        perc_1 = syns_and_cas_1[5]
        chem_name = syns_and_cas_1[4]
        cas_1 = syns_and_cas_1[3]
        add_cas_nums = True
        if perc_1 is None:
            perc_1 = 100.
            add_cas_nums = False
        list_item.setText('{}% {} ({})'.format(perc_1, chem_name, cas_1))
        self.composition_list.addItem(list_item)
        self.item = item

        if not add_cas_nums:
            return

        try:
            cas_and_percs = self.parent.cnxn.exec_get_additional_cas_nums(item.text())
        except db_tools.pyodbc.ProgrammingError as e:
            print(e, type(e))
            return

        if not cas_and_percs:
            return

        for cas_and_perc in cas_and_percs:
            perc = cas_and_perc[2]
            chem_name = cas_and_perc[1]
            cas_num = cas_and_perc[0]
            list_item = QListWidgetItem()
            list_item.setText('{}% {} ({})'.format(perc, chem_name, cas_num))
            self.composition_list.addItem(list_item)

    @staticmethod
    def set_tedit_text(tedit: QTextEdit, text: str):

        tedit.blockSignals(True)
        tedit.setText(text)
        tedit.blockSignals(False)

    def set_tedit_color(self, tedit: QTextEdit):

        notes = tedit.toPlainText()
        highlighted = False

        if (tedit == self.avoid_tedit and notes != self.avoid_notes) or \
            (tedit == self.notes_tedit and notes != self.notes) or \
            (tedit == self.safety_tedit and notes != self.safety_notes):
            tedit.setStyleSheet('QTextEdit {background: yellow};')
            highlighted = True
        else:
            tedit.setStyleSheet('QTextEdit {background: white};')

        if tedit == self.avoid_tedit:
            self.notes_changed[0] = highlighted
        elif tedit == self.notes_tedit:
            self.notes_changed[1] = highlighted
        else:
            self.notes_changed[2] = highlighted

        self.check_submit_enabled()

    def check_submit_enabled(self):

        if any(self.notes_changed):
            self.submit_changes_button.setEnabled(True)
        else:
            self.submit_changes_button.setEnabled(False)

    def submit_changes_clicked(self):

        self.parent.linked_main_window.run_login_with_functions(self.submit_changes, lambda: self.load_item(self.item))

    def submit_changes(self):

        avoid = self.avoid_tedit.toPlainText()
        notes = self.notes_tedit.toPlainText()
        safety = self.safety_tedit.toPlainText()

        chemical_name = self.item.text()

        self.parent.cnxn.exec_change_avoid_notes_safety(chemical_name, avoid, notes, safety)

    def select_sds(self):

        u_or_q = self.parent.linked_main_window.u_or_q
        file_name = QFileDialog.getOpenFileName(self, directory=u_or_q +
                                                ':\\UEORLAB1\\SDS - Chem Haz Profiles\\GHS_SDS\\',
                                                filter='*.pdf', caption=self.item.text())

        self.sds_file_path = file_name[0]

        if file_name[0]:
            self.parent.linked_main_window.run_login_with_functions(self.set_sds)

    def set_sds(self):

        self.parent.cnxn.exec_set_sds_file_path(self.item.text(), self.sds_file_path)

    def open_sds(self):

        sds_file_path = self.parent.cnxn.exec_get_sds_file_path(self.item.text())
        if not sds_file_path:
            return

        u_or_q = self.parent.linked_main_window.u_or_q

        try:
            startfile(u_or_q + sds_file_path[0][1:])
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def closeEvent(self, a0):
        self.parent.db_inspector = None
        super(OSHADBItemInspector, self).closeEvent(a0)


class ViewWatchlistDialog(QDialog):
    
    def __init__(self, parent: OSHADBGUI):
        super(ViewWatchlistDialog, self).__init__(parent=parent)
        self.ODBGUI = parent
        self.setWindowTitle('Watch List Viewer')
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 300), int(sf * 450))
        lyt = QGridLayout()
        self.setLayout(lyt)
        
        username_label = QLabel(parent=self, text='Username:')
        self.username_edit = QLineEdit(parent=self)
        self.username_edit.editingFinished.connect(self.load_watchlist)
        self.watchlist = QListWidget(parent=self)
        self.watchlist.itemClicked.connect(self.watchlist_item_clicked)
        self.watchlist.itemDoubleClicked.connect(self.watchlist_item_double_clicked)
        self.remove_button = QPushButton(parent=self, text='Remove from Watchlist')
        self.remove_button.clicked.connect(self.remove_button_clicked)
        self.remove_button.setEnabled(False)
        
        lyt.addWidget(username_label, 0, 0, 1, 1)
        lyt.addWidget(self.username_edit, 1, 0, 1, 1)
        lyt.addWidget(self.watchlist, 2, 0, 1, 1)
        lyt.addWidget(self.remove_button, 3, 0, 1, 1)

        self.username = ''

    @staticmethod
    def extract_chemical_name_from_item(item: QListWidgetItem) -> str:

        return item.text().split(']')[1][1:]
        
    def load_watchlist(self):

        self.watchlist.clear()
        self.remove_button.setEnabled(False)
        username = self.username_edit.text()
        self.username = username

        try:
            watchlist = self.parent().cnxn.exec_get_user_watchlist(username)
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()
            return

        watchlist_list = list()
        for item in watchlist:
            watchlist_list.append('[{}] {}'.format(item[1], item[0]))

        self.watchlist.addItems(watchlist_list)

    def watchlist_item_clicked(self):

        self.remove_button.setEnabled(True)

    def watchlist_item_double_clicked(self, item: QListWidgetItem):

        chemical_name = self.extract_chemical_name_from_item(item)
        new_item = QListWidgetItem()
        new_item.setText(chemical_name)
        self.ODBGUI.chemical_clicked(new_item)
        self.ODBGUI.watch_button.setEnabled(False)
        self.ODBGUI.request_button.setEnabled(False)
        self.ODBGUI.order_button.setEnabled(False)

    def remove_button_clicked(self):

        self.ODBGUI.linked_main_window.run_login_with_functions(self.remove_chemical_from_watchlist,
                                                                  self.load_watchlist)

    def remove_chemical_from_watchlist(self):

        chemical_name = self.extract_chemical_name_from_item(self.watchlist.currentItem())
        self.ODBGUI.cnxn.exec_remove_item_from_watchlist(self.username, chemical_name)
        
    def closeEvent(self, a0):
        
        try:
            self.ODBGUI.watchlist_dialog = None
        except Exception as e:
            print(e)
            
        super(ViewWatchlistDialog, self).closeEvent(a0)


class CreateRequestDialog(QDialog):

    def __init__(self, parent: OSHADBGUI):
        super(CreateRequestDialog, self).__init__(parent=parent)
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 350), int(120))
        self.setWindowTitle('Request {}'.format(parent.chemical_db_list.currentItem().text()))
        lyt = QGridLayout()
        self.setLayout(lyt)

        qty_label = QLabel(parent=self, text='Qty:')
        self.qty_edit = QLineEdit(parent=self)
        self.qty_edit.setText('1')
        self.qty_edit.editingFinished.connect(self.vet_qty)
        urgency_label = QLabel(parent=self, text='Urgency:')
        self.urgency_combo = QComboBox(parent=self)
        urgencies = [' ', 'Low', 'Standard', 'ASAP']
        self.urgency_combo.addItems(urgencies)
        self.urgency_combo.currentIndexChanged.connect(self.check_submit_enable)
        notes_label = QLabel(parent=self, text='   Notes:')
        self.notes_edit = QTextEdit(parent=self)
        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.clicked.connect(self.submit_clicked)
        self.submit_button.setEnabled(False)

        lyt.addWidget(qty_label, 0, 0, 1, 1)
        lyt.addWidget(self.qty_edit, 0, 1, 1, 1)
        lyt.addWidget(urgency_label, 1, 0, 1, 1)
        lyt.addWidget(self.urgency_combo, 1, 1, 1, 1)
        lyt.addWidget(self.submit_button, 2, 0, 1, 2)
        lyt.addWidget(notes_label, 0, 2, 1, 1)
        lyt.addWidget(self.notes_edit, 0, 3, 3, 1)

    def vet_qty(self):

        txt = self.qty_edit.text()

        try:
            val = int(txt)
            if val <= 0:
                raise ValueError

        except ValueError:

            self.qty_edit.blockSignals(True)
            self.qty_edit.setText('1')
            self.qty_edit.blockSignals(False)

    def check_submit_enable(self, i: int):

        if i == 0:
            self.submit_button.setEnabled(False)
        else:
            self.submit_button.setEnabled(True)

    def submit_clicked(self):

        qty = int(self.qty_edit.text())
        urgency = self.urgency_combo.currentIndex()
        notes = self.notes_edit.toPlainText()
        chemical = self.windowTitle()[8:]

        print(chemical, qty, urgency, notes)

        odbgui = self.parent()
        lmw = odbgui.linked_main_window

        lmw.run_login_with_functions(lambda: odbgui.connection_add_order_request(chemical, qty, urgency, notes),
                                     odbgui.refresh_inventory)

        self.close()


class RequestDialog(QDialog):

    def __init__(self, parent: OSHADBGUI):
        super(RequestDialog, self).__init__(parent=parent)
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 600), int(sf * 300))
        self.setWindowTitle('Active Order Requests')
        lyt = QGridLayout()
        self.setLayout(lyt)

        self.live_update_checkbox = QCheckBox(parent=self)
        self.live_update_checkbox.setText('Live Updates?')
        self.live_update_checkbox.setChecked(parent.live_updates)
        self.live_update_checkbox.clicked.connect(parent.set_live_updates)
        # self.live_update_checkbox.clicked.connect(self.report_check_state)
        lyt.addWidget(self.live_update_checkbox, 0, 0, 1, 1)
        self.order_request_list = QListWidget(parent=self)
        self.order_request_list.itemClicked.connect(self.order_request_clicked)
        lyt.addWidget(self.order_request_list, 1, 0, 1, 1)
        self.order_notes = QTextEdit(parent=self)
        self.order_notes.setReadOnly(True)
        lyt.addWidget(self.order_notes)

        self.current_order_requests = list()
        self.load_requests()

    def load_requests(self):

        self.order_request_list.clear()
        self.order_notes.clear()

        active_orders = self.parent().cnxn.exec_get_active_order_requests()
        active_orders_list = list()
        for order in active_orders:
            date = order[1]
            chemical = order[0]
            requestor = order[2]
            urgency = order[3]
            qty = order[6]
            active_orders_list.append(chemical)
            item = QListWidgetItem(parent=self.order_request_list)
            disp_txt = 'Date: {}, Chemical: {}, Qty: {}, Requestor: {}, Urgency: {}'
            item.setText(disp_txt.format(date, chemical, qty, requestor, urgency))
            if urgency == 'ASAP':
                item.setForeground(Qt.red)
                font = item.font()
                item.setFont(font)

        self.current_order_requests = active_orders

    def report_check_state(self, *args):
        print(self, args)

    def order_request_clicked(self, _):

        i = self.order_request_list.currentIndex().row()
        order = self.current_order_requests[i]
        notes = order[4]

        self.order_notes.setText(notes)

    def closeEvent(self, a0):
        self.parent().request_dialog = None
        super(RequestDialog, self).closeEvent(a0)


class ViewOrdersDialog(QDialog):

    def __init__(self, parent: OSHADBGUI):
        super(ViewOrdersDialog, self).__init__(parent=parent)
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 500), int(sf * 500))
        self.setWindowTitle('Orders')
        lyt = QGridLayout()
        self.setLayout(lyt)

        self.order_list = QListWidget(parent=self)
        lyt.addWidget(self.order_list, 0, 0, 1, 5)
        self.received_list = QListWidget(parent=self)
        lyt.addWidget(self.received_list, 1, 0, 1, 5)
        received_form_label = QLabel(parent=self, text='Received Form:')
        qty_label = QLabel(parent=self, text='Qty:')
        self.qty_edit = QLineEdit(parent=self)
        self.qty_edit.editingFinished.connect(self.vet_qty)
        date_label = QLabel(parent=self, text='Date (MM/DD/YYYY):')
        self.date_edit = QLineEdit(parent=self)
        today = datetime.date.today()
        self.set_date_to(today.month, today.day, today.year)
        self.date_edit.editingFinished.connect(self.vet_date)
        self.received_button = QPushButton(parent=self, text='Received')
        self.received_button.clicked.connect(self.order_received_clicked)

        room_label = QLabel(parent=self, text='Room:')
        self.room_combo = QComboBox(parent=self)
        loc_label = QLabel(parent=self, text='Location:')
        self.loc_combo = QComboBox(parent=self)

        rooms = parent.cnxn.exec_get_rooms()
        self.rooms = rooms
        self.rm_locations = list()
        room_list = list()

        for room in rooms:
            room_list.append(room[1])

        self.room_combo.addItems(room_list)

        lyt.addWidget(received_form_label, 2, 0, 1, 1)
        lyt.addWidget(qty_label, 3, 0, 1, 1)
        lyt.addWidget(self.qty_edit, 3, 1, 1, 1)
        lyt.addWidget(date_label, 3, 2, 1, 1)
        lyt.addWidget(self.date_edit, 3, 3, 1, 1)
        lyt.addWidget(self.received_button, 3, 4, 2, 1)
        lyt.addWidget(room_label, 4, 0, 1, 1)
        lyt.addWidget(self.room_combo, 4, 1, 1, 1)
        lyt.addWidget(loc_label, 4, 2, 1, 1)
        lyt.addWidget(self.loc_combo, 4, 3, 1, 1)

        orders = parent.cnxn.exec_get_all_orders()
        self.orders = orders
        orders_list = list()
        for order in orders:
            date = order[1]
            chemical_name = order[2]
            qty = order[3]
            received = qty - order[6]
            size = order[4]
            unit = order[5]
            order_id = order[0]
            orders_list.append(order_id)
            item = QListWidgetItem(parent=self.order_list)
            item.setText('Date: {}, Chemical: {}, {} x {} {}, {}/{} received'.format(date, chemical_name, qty, size,
                                                                                     unit, received, qty))

        self.remaining = 0
        self.order_list.itemClicked.connect(self.item_clicked)
        self.room_combo.currentIndexChanged.connect(self.get_rm_locations)
        if self.orders:
            self.order_list.setCurrentRow(0)
            self.order_list.itemClicked.emit(self.order_list.item(0))
            self.room_combo.currentIndexChanged.emit(0)
        else:
            self.order_list.setEnabled(False)
            self.received_list.setEnabled(False)
            self.qty_edit.setEnabled(False)
            self.room_combo.setEnabled(False)
            self.loc_combo.setEnabled(False)
            self.received_button.setEnabled(False)
            self.date_edit.setEnabled(False)

    def item_clicked(self, _):

        self.remaining = self.orders[self.order_list.currentIndex().row()][6]
        self.qty_edit.setText(str(self.remaining))

        order_id = self.orders[self.order_list.currentIndex().row()][0]

        orders_received = self.parent().cnxn.get_received_for_order(order_id)

        orders_receieved_list = list()

        for order_received in orders_received:
            orders_receieved_list.append('Date: {}, Qty: {}'.format(order_received[3], order_received[2]))

        self.received_list.clear()
        self.received_list.addItems(orders_receieved_list)

    def set_date_to(self, month: int, day: int, year: int):

        if month > 9 and day > 9:
            self.date_edit.setText('{}/{}/{}'.format(month, day, year))

        elif month > 9:
            self.date_edit.setText('{}/0{}/{}'.format(month, day, year))

        elif day > 9:
            self.date_edit.setText('0{}/{}/{}'.format(month, day, year))

        else:
            self.date_edit.setText('0{}/0{}/{}'.format(month, day, year))

    def vet_qty(self):

        val = self.remaining
        txt = self.qty_edit.text()

        try:
            val = int(txt)
            if val <= 0 or val > self.remaining:
                raise ValueError

        except ValueError:
            val = self.remaining

        finally:
            self.qty_edit.setText(str(val))

    def vet_date(self):

        today = datetime.date.today()

        date_str = self.date_edit.text()
        date = date_str.split('/')

        months = ['0{}'.format(i) if i < 10 else str(i) for i in range(1, 13)]
        days = ['0{}'.format(i) if i < 10 else str(i) for i in range(1, 32)]
        years = [str(i) for i in range(1990, today.year + 1)]

        if date[0] not in months or date[1] not in days or date[2] not in years:
            self.set_date_to(today.month, today.day, today.year)

    def get_rm_locations(self, ind: int):

        room_id = self.rooms[ind][0]
        rm_locations = self.parent().cnxn.exec_get_rm_locations(room_id)
        self.rm_locations = rm_locations
        locs = list()
        for rm_location in rm_locations:
            locs.append(rm_location[2])
        self.loc_combo.clear()
        self.loc_combo.addItems(locs)

    def order_received_clicked(self):

        self.parent().linked_main_window.run_login_with_functions(self.order_received)
        self.close()

    def order_received(self):

        order_id = self.orders[self.order_list.currentIndex().row()][0]
        qty = int(self.qty_edit.text())
        order_date = self.date_edit.text()
        loc_id = self.rm_locations[self.loc_combo.currentIndex()][0]

        self.parent().cnxn.exec_chemical_order_received(order_id, qty, order_date, loc_id)


class OrderDialog(QDialog):

    def __init__(self, parent: OSHADBGUI):
        super(OrderDialog, self).__init__(parent=parent)
        sf = parent.linked_main_window.sf
        self.sf = sf
        self.setFixedSize(int(sf * 450), int(sf * 150))
        chemical_name = parent.chemical_db_list.currentItem().text()
        self.setWindowTitle('Order Chemical: {}'.format(chemical_name))
        lyt = QGridLayout()
        self.setLayout(lyt)

        self.chemical_name = chemical_name
        self.chemical_id = parent.cnxn.exec_get_chemical_id_for_name(chemical_name=chemical_name)

        containers_label = QLabel(parent=self, text='Containers:')
        containers_label.setFixedHeight(int(sf * 10))
        lyt.addWidget(containers_label, 0, 0, 1, 1)
        self.containers = list()
        self.containers_list = QListWidget(parent=self)
        lyt.addWidget(self.containers_list, 1, 0, 2, 1)

        self.add_container_button = QPushButton(parent=self, text='Add Container')
        self.add_container_button.clicked.connect(self.add_container_dialog)
        lyt.addWidget(self.add_container_button, 3, 0, 1, 1)

        qty_label = QLabel('Quantity:')
        self.qty_edit = QLineEdit(parent=self)
        self.qty_edit.setText('1')
        self.qty_edit.editingFinished.connect(self.vet_qty)
        lyt.addWidget(qty_label, 1, 1, 1, 1)
        lyt.addWidget(self.qty_edit, 1, 2, 1, 1)
        date_label = QLabel('Date (MM/DD/YYYY):')
        self.date_edit = QLineEdit(parent=self)
        today = datetime.date.today()
        self.set_date_to(today.month, today.day, today.year)
        self.date_edit.editingFinished.connect(self.vet_date)
        self.submit_order_button = QPushButton(parent=self, text='Submit Order')
        self.submit_order_button.clicked.connect(self.submit_order_clicked)
        lyt.addWidget(date_label, 2, 1, 1, 1)
        lyt.addWidget(self.date_edit, 2, 2, 1, 1)
        lyt.addWidget(self.submit_order_button, 3, 1, 1, 2)

        self.container_ids = list()

        self.load_containers()

    def load_containers(self):

        self.container_ids = []
        self.containers_list.clear()
        self.containers = self.parent().cnxn.exec_get_containers_for_chemical_name(chemical_name=self.chemical_name)

        for container in self.containers:
            self.container_ids.append(container[0])
            item = QListWidgetItem(parent=self.containers_list)
            item.setText('{} {}'.format(container[1], container[2]))

    def set_date_to(self, month: int, day: int, year: int):

        if month > 9 and day > 9:
            self.date_edit.setText('{}/{}/{}'.format(month, day, year))

        elif month > 9:
            self.date_edit.setText('{}/0{}/{}'.format(month, day, year))

        elif day > 9:
            self.date_edit.setText('0{}/{}/{}'.format(month, day, year))

        else:
            self.date_edit.setText('0{}/0{}/{}'.format(month, day, year))

    def vet_qty(self):

        val = 1
        txt = self.qty_edit.text()

        try:
            val = int(txt)
            if val <= 0:
                raise ValueError

        except ValueError:
            val = 1

        finally:
            self.qty_edit.setText(str(val))

    def vet_date(self):

        today = datetime.date.today()

        date_str = self.date_edit.text()
        date = date_str.split('/')

        months = ['0{}'.format(i) if i < 10 else str(i) for i in range(1, 13)]
        days = ['0{}'.format(i) if i < 10 else str(i) for i in range(1, 32)]
        years = [str(i) for i in range(1990, today.year + 1)]

        if date[0] not in months or date[1] not in days or date[2] not in years:
            self.set_date_to(today.month, today.day, today.year)

    def add_container_dialog(self):

        AddContainerDialog(parent=self).exec_()

    def submit_order_clicked(self):

        self.parent().linked_main_window.run_login_with_functions(self.submit_order)

    def submit_order(self):

        container_id = self.container_ids[self.containers_list.currentIndex().row()]
        qty = int(self.qty_edit.text())
        order_date = self.date_edit.text()

        self.parent().cnxn.exec_place_chemical_order(container_id, qty, order_date)

        self.close()


class AddContainerDialog(QDialog):

    def __init__(self, parent: OrderDialog):
        super(AddContainerDialog, self).__init__(parent=parent)
        self.setFixedSize(int(parent.sf * 250), int(parent.sf * 70))
        self.setWindowTitle('Add Container')
        lyt = QGridLayout()
        self.setLayout(lyt)

        container_size_label = QLabel(parent=self, text='Size:')
        self.container_size_edit = QLineEdit(parent=self)
        self.container_size_edit.editingFinished.connect(self.vet_container_size_edit)
        container_units_label = QLabel(parent=self, text='Units:')
        self.container_units_combo = QComboBox(parent=self)
        self.container_units_combo.currentIndexChanged.connect(self.check_ready_to_add)
        self.add_button = QPushButton(parent=self, text='Add')
        self.add_button.clicked.connect(self.add_container_clicked)
        self.add_button.setEnabled(False)

        lyt.addWidget(container_size_label, 0, 0, 1, 1)
        lyt.addWidget(self.container_size_edit, 0, 1, 1, 1)
        lyt.addWidget(container_units_label, 0, 2, 1, 1)
        lyt.addWidget(self.container_units_combo, 0, 3, 1, 1)
        lyt.addWidget(self.add_button, 0, 4, 1, 1)

        units = parent.parent().cnxn.get_all_units()
        self.container_units_combo.addItem(' ')

        for unit in units:
            self.container_units_combo.addItem(unit[0])

    def vet_container_size_edit(self):

        txt = self.container_size_edit.text()

        try:
            val = round(float(txt), 3)
            if val <= 0.:
                raise ValueError

            self.container_size_edit.setText(str(val))

        except ValueError:
            self.container_size_edit.setText('')

        finally:

            self.check_ready_to_add(0)

    def check_ready_to_add(self, _):

        ready_to_add = True
        if self.container_units_combo.currentText() == ' ':
            ready_to_add = False
        if not self.container_size_edit.text():
            ready_to_add = False

        if ready_to_add:
            self.add_button.setEnabled(True)
        else:
            self.add_button.setEnabled(False)

    def add_container_clicked(self):

        self.parent().parent().linked_main_window.run_login_with_functions(self.add_container,
                                                                           self.parent().load_containers)
        self.close()

    def add_container(self):

        chemical_id = self.parent().chemical_id
        unit_abbrev = self.container_units_combo.currentText()
        container_size = float(self.container_size_edit.text())

        self.parent().parent().cnxn.insert_new_container(chemical_id=chemical_id, unit_abbrev=unit_abbrev,
                                                         size=container_size)


class MoveDialog(QDialog):

    def __init__(self, parent: OSHADBGUI):
        super(MoveDialog, self).__init__(parent=parent)
        sf = parent.linked_main_window.sf
        self.setFixedSize(int(sf * 450), int(sf * 100))
        self.setWindowTitle('Move item')

        lyt = QGridLayout()
        self.setLayout(lyt)

        move_qty_label = QLabel(parent=self, text='Qty:')
        self.move_qty_edit = QLineEdit(parent=self)
        self.move_qty_edit.setText('1.0')
        self.move_qty_edit.editingFinished.connect(self.vet_qty)
        move_room_and_loc_label = QLabel(parent=self, text='To Room, at Location:')
        self.move_room_combo = QComboBox(parent=self)
        self.move_loc_combo = QComboBox(parent=self)
        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.clicked.connect(self.submit_clicked)

        lyt.addWidget(move_qty_label, 0, 0, 1, 1)
        lyt.addWidget(self.move_qty_edit, 0, 1, 1, 1)
        lyt.addWidget(move_room_and_loc_label, 0, 2, 1, 1)
        lyt.addWidget(self.move_room_combo, 0, 3, 1, 1)
        lyt.addWidget(self.move_loc_combo, 0, 4, 1, 1)
        lyt.addWidget(self.submit_button, 1, 4, 1, 1)

        rooms = parent.cnxn.exec_get_rooms()
        self.rooms = rooms
        self.rm_locations = list()
        rooms_list = list()

        for room in rooms:
            rooms_list.append(room[1])

        self.move_room_combo.addItems(rooms_list)
        self.move_room_combo.currentIndexChanged.connect(self.room_index_changed)
        self.move_room_combo.currentIndexChanged.emit(0)

    def vet_qty(self):

        val = 1.
        txt = self.move_qty_edit.text()

        try:
            val = float(txt)
            val = round(val, 1)
            if val <= 0.:
                raise ValueError

        except ValueError:
            val = 1.

        finally:
            self.move_qty_edit.setText(str(val))

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

        self.parent().linked_main_window.run_login_with_functions(self.submit_move, self.parent().refresh_inventory)
        self.close()

    def submit_move(self):

        inv_ids = self.parent().inventory_ids
        move_qty = float(self.move_qty_edit.text())
        new_loc_id = self.rm_locations[self.move_loc_combo.currentIndex()][0]

        index = self.parent().chemical_inv_list.currentIndex()

        if index.row() < len(inv_ids):
            inventory_id = inv_ids[index.row()]
            self.parent().cnxn.exec_move_inventory_item(inventory_id=inventory_id, move_qty=move_qty,
                                                        new_loc_id=new_loc_id)
        else:
            empty_inv_ids = self.parent().empty_inventory_ids
            empty_inv_id = empty_inv_ids[index.row() - len(inv_ids)]
            print('moving empty inventory item: {}'.format(empty_inv_id))
            self.parent().cnxn.exec_move_empty_inventory_item(inventory_id=empty_inv_id,
                                                              move_qty=move_qty,
                                                              new_loc_id=new_loc_id)
