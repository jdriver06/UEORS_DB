
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QListWidgetItem, QGridLayout, QFrame, QLineEdit, QComboBox, \
    QPushButton, QMessageBox, QDialog, QTextEdit, QHBoxLayout, QMainWindow, QFileDialog
from PyQt5.QtGui import QKeyEvent, QBrush, QPalette, QColor
from PyQt5.Qt import Qt, pyqtSignal
from PyQt5.QtCore import Qt as cQt
import db_tools
from db_tools import DBObjects
import win32clipboard
import decimal
import datetime
import copy
import pandas as pd
import numpy as np
from functools import partial


class SurfactantConnection:

    def __init__(self, cnxn: db_tools.pyodbc.Connection):
        self._cnxn = cnxn
        self._cursor = cnxn.cursor()

    def get_cursor(self):
        return self._cursor

    @staticmethod
    def check_column_and_table(column: DBObjects.Columns, table: DBObjects.Tables):

        if not DBObjects.is_column_in_table(column, table):
            raise(TypeError('The enumerated column is not in the enumerated table.'))

    def get_column_from_table(self, table: DBObjects.Tables, column: DBObjects.Columns):

        SurfactantConnection.check_column_and_table(column, table)
        return db_tools.select_column_from_table(self._cnxn, table.value, column.value).fetchall()

    def get_column_from_table_where(self, table: DBObjects.Tables, column: DBObjects.Columns,
                                    key: DBObjects.Columns, val: int):

        SurfactantConnection.check_column_and_table(column, table)
        SurfactantConnection.check_column_and_table(key, table)
        return db_tools.select_column_from_table_where_key_equals(self._cnxn, table.value, column.value,
                                                                  key.value, val).fetchall()

    def get_all_from_table_where(self, table: DBObjects.Tables, key: DBObjects.Columns, val: int):

        SurfactantConnection.check_column_and_table(key, table)
        return db_tools.select_all_from_table_where_key_equals(self._cnxn, table.value, key.value, val).fetchall()

    def set_column_where(self, table: DBObjects.Tables, column: DBObjects.Columns, set_val: str,
                         key: DBObjects.Columns, val: int):

        SurfactantConnection.check_column_and_table(key, table)
        return db_tools.update_table_set_column_where_key_equals(self._cnxn, table.value, column.value, set_val,
                                                                 key.value, val).fetchall()

    def insert_values_into_table(self, table: DBObjects.Tables, *values):

        return db_tools.insert_values_into_table(self._cnxn, table.value, list(values))

    def delete_from_table_where(self, table: DBObjects.Tables, key: DBObjects.Columns, value: int):

        return db_tools.delete_from_table_where_key_equals(self._cnxn, table.value, key.value, value)

    def get_all_surfactant_classes(self):

        return self.get_column_from_table(DBObjects.Tables.SCTable, DBObjects.Columns.SCName)

    def get_all_ionic_groups(self):

        return self.get_column_from_table(DBObjects.Tables.IGTable, DBObjects.Columns.IGName)

    def get_all_hydrophobes(self):

        return self.get_column_from_table(DBObjects.Tables.HTable, DBObjects.Columns.HName)

    def exec_get_rooms(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRooms, {})

    def exec_get_rm_locations(self, room_id: int):

        params = {DBObjects.Params.RoomID.value: room_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetRoomLocs, params)

    def get_all_uncertain_hydrophobes(self):

        return self.get_column_from_table(DBObjects.Tables.UHTable, DBObjects.Columns.UHFormula)

    def exec_get_uncertain_hydrophobes_where_company(self, c_name: str):

        params = {DBObjects.Params.CompName.value: c_name}

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetUHforCompany, params)

    def get_all_companies(self):

        return self.get_column_from_table(DBObjects.Tables.CompaniesTable, DBObjects.Columns.CompanyName)

    def get_projects_for_company_name(self, c_name: str):

        params = {DBObjects.Params.CompName.value: c_name}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SelectProjectsforCompanyName, params)

    def get_ionic_groups_where_class(self, val: int):

        return self.get_column_from_table_where(DBObjects.Tables.IGTable, DBObjects.Columns.IGName,
                                                DBObjects.Columns.SCID, val)

    def exec_stored_procedure_with_params(self, procedure: DBObjects.Procedures, params: dict):

        return db_tools.execute_stored_procedure_with_params(self._cnxn, procedure.value, params).fetchall()

    def exec_stored_procedure_with_params_no_fetchall(self, procedure: DBObjects.Procedures, params: dict):

        return db_tools.execute_stored_procedure_with_params(self._cnxn, procedure.value, params)

    def exec_select_surfactants(self, s_name: str='', c_name: str='', ig_name: str='', m_name: str='',
                                source_name: str='', po_min: int=-1, po_max: int=-1, eo_min: int=-1, eo_max: int=-1,
                                acn_min: int=-1, acn_max: int=-1, h_name: str='', loc_id: int=0):

        keys = list(DBObjects.PPDict[DBObjects.Procedures.SelectSurfactants])
        values = [s_name, c_name, ig_name, m_name, source_name, po_min, po_max,
                  eo_min, eo_max, acn_min, acn_max, h_name, loc_id]
        params = dict()

        for key, value in zip(keys, values):
            params[key.value] = value

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SelectSurfactants, params)

    def exec_select_surfactant_blends(self, s_name: str='', c_name: str='', ig_name: str='', m_name: str='',
                                      source_name: str='', po_min: int=-1, po_max: int=-1,
                                      eo_min: int=-1, eo_max: int=-1, acn_min: int=-1, acn_max: int=-1,
                                      h_name: str='', loc_id: int=0):

        keys = list(DBObjects.PPDict[DBObjects.Procedures.SelectSurfactantBlends])
        values = [s_name, c_name, ig_name, m_name, source_name, po_min, po_max,
                  eo_min, eo_max, acn_min, acn_max, h_name, loc_id]
        params = dict()

        for key, value in zip(keys, values):
            params[key.value] = value

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SelectSurfactantBlends, params)

    def exec_get_surfactant_structure(self, s_id: int):

        params = {DBObjects.Params.SID.value: s_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetSurfactantStructure, params)

    def exec_select_inv_items(self, c_name: str='', ig_name: str='', m_name: str='', s_name: str='',
                              po_min: int=-1, po_max: int=-1, eo_min: int=-1, eo_max: int=-1,
                              acn_min: int=-1, acn_max: int=-1, h_name: str='', loc_id: int=0,
                              rec_after_date: str='NULL', rec_before_date: str='NULL', syn_after_date: str='NULL',
                              syn_before_date: str='NULL'):

        keys = list(DBObjects.PPDict[DBObjects.Procedures.SelectInvItems])
        values = [c_name, ig_name, m_name, s_name, po_min, po_max, eo_min, eo_max, acn_min, acn_max, h_name, loc_id,
                  rec_after_date, rec_before_date, syn_after_date, syn_before_date]
        params = dict()

        for key, value in zip(keys, values):
            params[key.value] = value

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SelectInvItems, params)

    def get_surfactant_info(self, s_id: int):

        return self.get_all_from_table_where(DBObjects.Tables.SDBTable, DBObjects.Columns.SID, s_id)

    def exec_get_surfactant_project_tag(self, stock_id: int):

        params = {DBObjects.Params.StkID.value: stock_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetSurfProjTag, params)

    def exec_get_surfactant_blend_project_tag(self, stock_id: int):

        params = {DBObjects.Params.StkID.value: stock_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetSurfBlendProjTag, params)

    def exec_remove_surfactant_project_tag(self, stock_id: int):

        params = {DBObjects.Params.StkID.value: stock_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RemoveSurfPTag, params)

    def exec_remove_surfactant_blend_project_tag(self, blend_stock_id: int):

        params = {DBObjects.Params.BlendStkID.value: blend_stock_id}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RemoveSurfBlendPTag, params)

    def exec_add_surfactant_project_tag(self, stock_id: int, p_name: str):

        params = {DBObjects.Params.StkID.value: stock_id, DBObjects.Params.ProjName.value: p_name}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddSurfProjTag, params)

    def exec_add_surfactant_blend_project_tag(self, blend_stock_id: int, p_name: str):

        params = {DBObjects.Params.BlendStkID.value: blend_stock_id, DBObjects.Params.ProjName.value: p_name}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddSurfBlendProjTag, params)

    def exec_get_project_name_from_id(self, proj_id: int):

        params = {DBObjects.Params.ProjID.value: proj_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetProjectNamefromID, params)

    def exec_get_blend_info(self, blend_id: int):

        params = {DBObjects.Params.BlendID.value: blend_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetBlendInfo, params)

    def exec_get_blend_stock_composition(self, blend_stk_id):

        params = {DBObjects.Params.BlendStkID.value: blend_stk_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetBlendStkComp, params)

    def exec_add_surfactant(self, s_name: str, m_name: str, uh_name: str, h_name: str, n_eo: float, n_po: float,
                            ig_name: str, mw: float, n_ig: int, nre: bool, po_eo_rev: bool, n_poeochains: int):

        keys = list(DBObjects.PPDict[DBObjects.Procedures.AddSurfactant])
        values = [s_name, m_name, uh_name, h_name, n_eo, n_po, ig_name, mw, n_ig, nre, po_eo_rev, n_poeochains]
        params = dict()

        for key, value in zip(keys, values):
            params[key.value] = value

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddSurfactant, params)

    def exec_get_surfactant_name(self, s_id: int):

        params = {DBObjects.Params.SID.value: s_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SurfactantName, params)

    def exec_get_surfactant_manufacturer_name(self, s_id):

        params = {DBObjects.Params.SID.value: s_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.SurfactantManufacturerName, params)

    def exec_get_stock_or_dilution_info(self, sd_id: int, stock_or_dilution: bool):

        if stock_or_dilution:
            procedure = DBObjects.Procedures.StockInfo
        else:
            procedure = DBObjects.Procedures.DilInfo

        keys = list(DBObjects.PPDict[procedure])
        values = [sd_id]
        params = dict()

        for key, value in zip(keys, values):
            params[key.value] = value

        if stock_or_dilution:
            return self.exec_get_stock_info(params)
        else:
            return self.exec_get_dilution_info(params)

    def get_all_stock_data(self, stk_id: int):

        return self.get_all_from_table_where(DBObjects.Tables.StkTable, DBObjects.Columns.StkID, stk_id)

    def exec_get_blend_stock_info(self, blend_stk_id: int):

        params = {DBObjects.Params.BlendStkID.value: blend_stk_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetBlendStkInfo, params)

    def exec_get_stock_info(self, params: dict):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.StockInfo, params)

    def exec_get_dilution_info(self, params: dict):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.DilInfo, params)

    def get_stocks_and_dilutions(self, int_id: int) -> list:

        params = {DBObjects.Params.SID.value: int_id}
        stocks_and_dilutions = self.exec_stored_procedure_with_params(DBObjects.Procedures.GetStksDils, params)
        return stocks_and_dilutions

    def get_blend_stocks_and_dilutions(self, int_id: int) -> list:

        params = {DBObjects.Params.BlendID.value: int_id}
        stocks_and_dilutions = self.exec_stored_procedure_with_params(DBObjects.Procedures.GetBlendStksDils, params)
        return stocks_and_dilutions

    def exec_get_low_qty_stocks(self, qty: int):

        params = {DBObjects.Params.Qty.value: qty}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetLowQtyStocks, params)

    def exec_update_qty_if_changed(self, is_stock: bool, sd_id: int, qty: int):

        params = {DBObjects.Params.ISStk.value: is_stock, DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.Qty.value: qty}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.UpdateQtyIfChanged, params)

    def exec_update_stock_conv_perc(self, stock_id: int, conv_perc):

        params = {DBObjects.Params.StkID.value: stock_id, DBObjects.Params.ConvPerc.value: conv_perc}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.UpdateStkConvPerc, params)

    def exec_update_blend_stock_conv_perc(self, stock_id: int, conv_perc):

        params = {DBObjects.Params.StkID.value: stock_id, DBObjects.Params.ConvPerc.value: conv_perc}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.UpdateBlendStkConvPerc, params)

    def exec_get_location_string(self, loc_id: int):

        params = {DBObjects.Params.LocID.value: loc_id}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.LocationString, params)

    def exec_get_all_location_strings(self):

        return self.exec_stored_procedure_with_params(DBObjects.Procedures.AllLocationStrings, {})

    def get_all_mtt_names(self):

        return self.get_column_from_table(DBObjects.Tables.MTTTable, DBObjects.Columns.MTTName)

    def exec_get_measurements_and_treatments(self, sd_id: int, is_stock: bool):

        params = {DBObjects.Params.SDID.value: sd_id, DBObjects.Params.ISStk.value: is_stock}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetMTs, params)

    def exec_get_blend_measurements_and_treatments(self, sd_id: int, is_stock: bool):

        params = {DBObjects.Params.SDID.value: sd_id, DBObjects.Params.ISStk.value: is_stock}
        return self.exec_stored_procedure_with_params(DBObjects.Procedures.GetBlendMTs, params)

    def exec_get_stock_measurements_and_treatments(self, stock_id: int):

        return self.exec_get_measurements_and_treatments(stock_id, True)

    def exec_get_dilution_measurements_and_treatments(self, dil_id: int):

        return self.exec_get_measurements_and_treatments(dil_id, False)

    def exec_set_stock_or_dilution_qty(self, is_stock: bool, sd_id: int, qty: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.Qty.value: qty}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetSDQty, params)

    def exec_set_stock_or_dilution_notes(self, is_stock: bool, sd_id: int, notes: str):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.Notes.value: notes}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetSDNotes, params)

    def exec_set_stock_or_dilution_loc(self, is_stock: bool, sd_id: int, loc_id: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.LocID.value: loc_id}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetSDLoc, params)

    def exec_set_blend_stock_or_dilution_qty(self, is_stock: bool, sd_id: int, qty: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.Qty.value: qty}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetBlendSDQty, params)

    def exec_set_blend_stock_or_dilution_notes(self, is_stock: bool, sd_id: int, notes: str):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.Notes.value: notes}
        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetBlendSDNotes, params)

    def exec_set_blend_stock_or_dilution_loc(self, is_stock: bool, sd_id: int, loc_id: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.SDID.value: sd_id,
                  DBObjects.Params.LocID.value: loc_id}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SetBlendSDLoc, params)

    def exec_add_measurement_or_treatment(self, is_stock: bool, mtt_id: int, sd_id: int, val: float, mt_date: str):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.MTTID.value: mtt_id,
                  DBObjects.Params.SDID.value: sd_id, DBObjects.Params.MTVal.value: val,
                  DBObjects.Params.MTDate.value: mt_date}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddMTs, params)

    def exec_remove_measurement_or_treatment(self, is_stock: bool, mt_id: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.MTID.value: mt_id}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RemoveMT, params)

    def exec_add_blend_measurement_or_treatment(self, is_stock: bool, mtt_id: int, sd_id: int, val: float, mt_date: str):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.MTTID.value: mtt_id,
                  DBObjects.Params.SDID.value: sd_id, DBObjects.Params.MTVal.value: val,
                  DBObjects.Params.MTDate.value: mt_date}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.AddBlendMTs, params)

    def exec_remove_blend_measurement_or_treatment(self, is_stock: bool, mt_id: int):

        params = {DBObjects.Params.ISStk.value: int(is_stock), DBObjects.Params.MTID.value: mt_id}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.RemoveBlendMT, params)

    def exec_submit_stock(self, s_id: int, lot_num: str, rec_date, syn_date, act_perc: float, conv_perc, qty: int,
                          loc_id: int, notes: str):

        C = DBObjects.Columns
        params = {C.SID.value: s_id, C.LotN.value: lot_num, C.RecD.value: rec_date, C.SynD.value: syn_date,
                  C.ActP.value: act_perc, C.ConvP.value: conv_perc, C.Qty.value: qty, C.LocID.value: loc_id,
                  C.Notes.value: notes}

        return self.exec_stored_procedure_with_params_no_fetchall(DBObjects.Procedures.SubmitStk, params)

    def exec_submit_dilution(self, stock_id: int, act_perc: float, qty: int, date_made: str, loc_id: int, notes: str):

        return self.insert_values_into_table(DBObjects.Tables.DilTable, stock_id, act_perc, qty, date_made, loc_id,
                                             notes)

    def exec_delete_stock(self, stock_id: int):

        return self.delete_from_table_where(DBObjects.Tables.StkTable, DBObjects.Columns.StkID, stock_id)

    def exec_delete_dilution(self, dil_id: int):

        return self.delete_from_table_where(DBObjects.Tables.DilTable, DBObjects.Columns.DilID, dil_id)

    def close(self):

        self._cnxn.close()


class SurfactantDBGUI(QWidget):

    class ConversionFailure(ValueError):

        def __init__(self, cls_1: type, cls_2: type):
            ValueError.__init__(self, 'Cannot convert {} to {}.'.format(cls_1, cls_2))

    def __init__(self, cnxn: db_tools.pyodbc.Connection, linked_main_window: QMainWindow):
        super(SurfactantDBGUI, self).__init__()
        self.sf = 1.
        self.db_gui = linked_main_window
        if linked_main_window is not None:
            self.sf = linked_main_window.sf
        self.setFixedSize(int(self.sf * 770), int(self.sf * 650))

        lyt = QGridLayout()

        self.filter_frame = QFrame(parent=self)
        filter_lyt = QGridLayout()
        self.filter_frame.setLayout(filter_lyt)

        self.surf_name_filter_label = QLabel(parent=self, text='Surf. Name:')
        self.surf_name_filter_edit = QLineEdit(parent=self)
        self.class_filter_label = QLabel(parent=self, text='Surf. Class:')
        self.ig_filter_label = QLabel(parent=self, text='Ionic Group:')
        self.manufacturer_filter_label = QLabel(parent=self, text='Manufacturer:')
        self.source_filter_label = QLabel(parent=self, text='Source:')
        self.po_minmax_filter_label = QLabel(parent=self, text='PO Min/Max:')
        self.eo_minmax_filter_label = QLabel(parent=self, text='EO Min/Max:')
        self.acn_minmax_filter_label = QLabel(parent=self, text='ACN Min/Max:')
        self.hydrophobe_filter_label = QLabel(parent=self, text='Hydrophobe:')
        self.location_filter_label = QLabel(parent=self, text='Location:')
        self.search_btn = QPushButton(parent=self, text='Search')
        self.search_btn.clicked.connect(self.search_surfactant_database)

        self.class_filter_combo = QComboBox(parent=self)
        self.ig_filter_combo = QComboBox(parent=self)
        self.manufacturer_filter_edit = QLineEdit(parent=self)
        self.source_filter_edit = QLineEdit(parent=self)
        self.po_minmax_filter_edit = QLineEdit(parent=self)
        self.po_minmax_filter_edit.editingFinished.connect(
            lambda: SurfactantDBGUI.vet_min_max_text(self.po_minmax_filter_edit))
        self.eo_minmax_filter_edit = QLineEdit(parent=self)
        self.eo_minmax_filter_edit.editingFinished.connect(
            lambda: SurfactantDBGUI.vet_min_max_text(self.eo_minmax_filter_edit))
        self.acn_minmax_filter_edit = QLineEdit(parent=self)
        self.acn_minmax_filter_edit.editingFinished.connect(
            lambda: SurfactantDBGUI.vet_min_max_text(self.acn_minmax_filter_edit))
        self.hydrophobe_filter_combo = QComboBox(parent=self)
        self.location_filter_combo = QComboBox(parent=self)

        self.db_label = QLabel(parent=self, text='Database Options:')
        self.inventory_label = QLabel(parent=self, text='Inventory Listings:')

        self.surfactant_list = QListWidget(parent=self)
        inventory_font = self.surfactant_list.font()
        inventory_font.setFamily('Courier')
        self.surfactant_list.setFont(inventory_font)
        self.surfactant_list.itemClicked.connect(self.surfactant_selected)

        self.inventory_list = QListWidget(parent=self)
        self.inventory_list.setFont(inventory_font)
        self.inventory_list.itemClicked.connect(self.inventory_item_clicked)
        self.inventory_list.itemDoubleClicked.connect(self.inspect_inventory_item)

        self.db_add_btn = QPushButton(parent=self, text='Add')
        self.db_add_btn.clicked.connect(self.add_surfactant)
        self.db_export_btn = QPushButton(parent=self, text='Export')
        self.db_export_btn.clicked.connect(self.export_inventory)
        self.db_import_btn = QPushButton(parent=self, text='Import')
        self.db_import_btn.clicked.connect(self.import_inventory_update)
        self.db_low_stock_btn = QPushButton(parent=self, text='Low Stock')
        self.db_low_stock_btn.clicked.connect(self.export_low_stocks_clicked)
        self.stock_add_btn = QPushButton(parent=self, text='Add Stock')
        self.stock_add_btn.clicked.connect(self.add_stock)
        self.dil_add_btn = QPushButton(parent=self, text='Add Dilution')
        self.dil_add_btn.clicked.connect(self.add_dilution)
        self.inv_remove_btn = QPushButton(parent=self, text='Remove')
        self.inv_remove_btn.clicked.connect(self.remove_stock_or_dilution_clicked)

        filter_lyt.addWidget(self.surf_name_filter_label, 0, 0, 1, 1)
        filter_lyt.addWidget(self.surf_name_filter_edit, 0, 1, 1, 1)
        filter_lyt.addWidget(self.manufacturer_filter_label, 1, 0, 1, 1)
        filter_lyt.addWidget(self.manufacturer_filter_edit, 1, 1, 1, 1)
        filter_lyt.addWidget(self.class_filter_label, 2, 0, 1, 1)
        filter_lyt.addWidget(self.class_filter_combo, 2, 1, 1, 1)
        filter_lyt.addWidget(self.ig_filter_label, 3, 0, 1, 1)
        filter_lyt.addWidget(self.ig_filter_combo, 3, 1, 1, 1)
        filter_lyt.addWidget(self.hydrophobe_filter_label, 4, 0, 1, 1)
        filter_lyt.addWidget(self.hydrophobe_filter_combo, 4, 1, 1, 1)
        # filter_lyt.addWidget(self.source_filter_label, 3, 0, 1, 1)
        # filter_lyt.addWidget(self.source_filter_edit, 3, 1, 1, 1)
        filter_lyt.addWidget(self.po_minmax_filter_label, 0, 2, 1, 1)
        filter_lyt.addWidget(self.po_minmax_filter_edit, 0, 3, 1, 1)
        filter_lyt.addWidget(self.eo_minmax_filter_label, 1, 2, 1, 1)
        filter_lyt.addWidget(self.eo_minmax_filter_edit, 1, 3, 1, 1)
        filter_lyt.addWidget(self.acn_minmax_filter_label, 2, 2, 1, 1)
        filter_lyt.addWidget(self.acn_minmax_filter_edit, 2, 3, 1, 1)
        filter_lyt.addWidget(self.location_filter_label, 3, 2, 1, 1)
        filter_lyt.addWidget(self.location_filter_combo, 3, 3, 1, 1)
        filter_lyt.addWidget(self.search_btn, 4, 3, 1, 1)

        lyt.addWidget(self.filter_frame, 0, 0, 1, 4)
        lyt.addWidget(self.db_label, 1, 0, 1, 1)
        lyt.addWidget(self.surfactant_list, 2, 0, 1, 4)
        lyt.addWidget(self.db_add_btn, 3, 0, 1, 1)
        lyt.addWidget(self.db_export_btn, 3, 1, 1, 1)
        lyt.addWidget(self.db_import_btn, 3, 2, 1, 1)
        lyt.addWidget(self.db_low_stock_btn, 3, 3, 1, 1)
        lyt.addWidget(self.inventory_label, 4, 0, 1, 1)
        lyt.addWidget(self.inventory_list, 5, 0, 1, 4)
        lyt.addWidget(self.stock_add_btn, 6, 0, 1, 1)
        lyt.addWidget(self.dil_add_btn, 6, 1, 1, 1)
        lyt.addWidget(self.inv_remove_btn, 6, 2, 1, 1)

        self.login_dialog = None
        self.inventory_item_inspector = None
        self.cnxn = None
        self.set_connection(cnxn)
        self.surfactants = []
        self.surfactant_blends = []
        self.inventories = []
        self.rows_imported = np.nan

        self.setLayout(lyt)

        try:
            self.query_to_initialize_popups()

        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

        self.class_filter_combo.currentIndexChanged.connect(self.surfactant_class_combo_changed)
        self.source_filter_label.setVisible(False)
        self.source_filter_edit.setVisible(False)

        self.stock_add_btn.setEnabled(False)
        self.dil_add_btn.setEnabled(False)
        self.inv_remove_btn.setEnabled(False)

        self.control_pressed = False

        self.show()

        self.search_btn.click()

    def set_connection(self, cnxn: db_tools.pyodbc.Connection):

        self.cnxn = SurfactantConnection(cnxn)

    def add_surfactant(self):

        try:
            AddSurfactantGUI(parent=self).exec_()
        except Exception as e:
            print(e)

    def export_inventory(self):

        InventoryExportGUI(parent=self).exec_()

    def import_inventory_update(self):

        letter = self.db_gui.u_or_q

        f = QFileDialog.getOpenFileName(parent=self, caption='Get Import File',
                                        directory=letter + ':\\UEORLAB1\\Python Files\\UEORS_DB_GUI\\',
                                        filter='*.xlsx')
        if not f[0]:
            return

        self.db_gui.run_login_with_functions(lambda: self.import_inventory_func(f), self.rows_imported_from_sheet)

    def export_low_stocks_clicked(self):

        LowStockGUI(parent=self).exec_()

    def rows_imported_from_sheet(self):

        QMessageBox(parent=self, text='Imported {} rows from spreadsheet'.format(self.rows_imported)).exec_()

    def import_inventory_func(self, f: str):

        self.rows_imported = 0

        result = pd.read_excel(f[0])
        phs = np.array(result.values[:, 7])

        for i, ph in enumerate(phs):

            print('index: {}'.format(i))

            stock_ph_entry = ()
            dil_ph_entry = ()
            stock_filt_entry = ()
            dil_filt_entry = ()

            filtered = result.values[i, 10]

            # if np.isnan(ph) and not isinstance(filtered, str):
            #     self.rows_imported = i + 1
            #     continue

            stock_id = result.values[i, 2]
            dil_id = result.values[i, 3]
            qty = result.values[i, 6]

            if np.isnan(dil_id):
                self.cnxn.exec_update_qty_if_changed(is_stock=True, sd_id=stock_id, qty=qty)
            else:
                self.cnxn.exec_update_qty_if_changed(is_stock=False, sd_id=dil_id, qty=qty)

            adj = result.values[i, 8]
            date = result.values[i, 9]

            if not np.isnan(ph):

                if isinstance(adj, str) and adj.lower() == 'yes':
                    mtt_id = 2
                else:
                    mtt_id = 3

                if pd.isnull(date):
                    date = 'NULL'
                else:
                    date = date.date()
                    date = str(date.month) + '/' + str(date.day) + '/' + str(date.year)

                if np.isnan(dil_id):
                    stock_ph_entry = (mtt_id, int(stock_id), ph, date)
                else:
                    dil_ph_entry = (mtt_id, int(dil_id), ph, date)

            if isinstance(filtered, str) and filtered.lower() == 'yes':
                filt_date = result.values[i, 11]
                if pd.isnull(filt_date):
                    filt_date = 'NULL'
                else:
                    filt_date = filt_date.date()
                    filt_date = str(filt_date.month) + '/' + str(filt_date.day) + '/' + str(filt_date.year)

                if np.isnan(dil_id):
                    stock_filt_entry = (4, int(stock_id), 'NULL', filt_date)
                else:
                    dil_filt_entry = (4, int(dil_id), 'NULL', filt_date)

            if stock_ph_entry:
                self.cnxn.exec_add_measurement_or_treatment(is_stock=True, mtt_id=stock_ph_entry[0],
                                                            sd_id=stock_ph_entry[1], val=stock_ph_entry[2],
                                                            mt_date=stock_ph_entry[3])
            elif dil_ph_entry:
                self.cnxn.exec_add_measurement_or_treatment(is_stock=False, mtt_id=dil_ph_entry[0],
                                                            sd_id=dil_ph_entry[1], val=dil_ph_entry[2],
                                                            mt_date=dil_ph_entry[3])

            if stock_filt_entry:
                self.cnxn.exec_add_measurement_or_treatment(is_stock=True, mtt_id=stock_filt_entry[0],
                                                            sd_id=stock_filt_entry[1], val=stock_filt_entry[2],
                                                            mt_date=stock_filt_entry[3])
            elif dil_filt_entry:
                self.cnxn.exec_add_measurement_or_treatment(is_stock=False, mtt_id=dil_filt_entry[0],
                                                            sd_id=dil_filt_entry[1], val=dil_filt_entry[2],
                                                            mt_date=dil_filt_entry[3])

            self.rows_imported = i + 1

    @staticmethod
    def set_popup_from_query_result(popup: QComboBox, items: list):

        final_list = ['']

        for item in items:
            final_list.append(item[0])

        popup.clear()
        popup.addItems(final_list)

    @staticmethod
    def convert_string_to_int(val: str) -> int:

        if not val:
            return -1

        else:

            try:

                val = int(val)

                if val < -1:
                    val = -1

                return val

            except ValueError:
                raise SurfactantDBGUI.ConversionFailure(str, int)

    @staticmethod
    def parse_min_max_text(txt: str):

        if not txt:
            return -1, -1, None

        i = txt.find('/')

        if i == -1:
            return -1, -1, None

        try:

            n_min = txt[:i]
            n_max = txt[i+1:]

            n_min = SurfactantDBGUI.convert_string_to_int(n_min)
            n_max = SurfactantDBGUI.convert_string_to_int(n_max)

            return n_min, n_max, None

        except SurfactantDBGUI.ConversionFailure as e:

            return -1, -1, e

    @staticmethod
    def vet_min_max_text(edit: QLineEdit):

        txt = edit.text()
        i = txt.find('/')

        if i == -1:
            edit.setText('')

        _, _, e = SurfactantDBGUI.parse_min_max_text(txt)

        if e is not None:
            edit.setText('')

    def query_to_initialize_popups(self):

        SurfactantDBGUI.set_popup_from_query_result(self.class_filter_combo, self.cnxn.get_all_surfactant_classes())
        SurfactantDBGUI.set_popup_from_query_result(self.ig_filter_combo, self.cnxn.get_all_ionic_groups())
        SurfactantDBGUI.set_popup_from_query_result(self.hydrophobe_filter_combo, self.cnxn.get_all_hydrophobes())
        SurfactantDBGUI.set_popup_from_query_result(self.location_filter_combo,
                                                    self.cnxn.exec_get_all_location_strings())

    def surfactant_class_combo_changed(self):

        i = self.class_filter_combo.currentIndex()

        if i == 0:
            result = self.cnxn.get_all_ionic_groups()
        else:
            result = self.cnxn.get_ionic_groups_where_class(i)

        SurfactantDBGUI.set_popup_from_query_result(self.ig_filter_combo, result)

    def search_surfactant_database(self):

        if self.inventory_item_inspector is not None:
            self.inventory_item_inspector.close()

        self.stock_add_btn.setEnabled(False)
        self.dil_add_btn.setEnabled(False)
        self.inv_remove_btn.setEnabled(False)

        s_name = self.surf_name_filter_edit.text()
        c_name = self.class_filter_combo.currentText()
        ig_name = self.ig_filter_combo.currentText()
        m_name = self.manufacturer_filter_edit.text()
        h_name = self.hydrophobe_filter_combo.currentText()
        loc_id = self.location_filter_combo.currentIndex()

        po_min, po_max, _ = SurfactantDBGUI.parse_min_max_text(self.po_minmax_filter_edit.text())
        eo_min, eo_max, _ = SurfactantDBGUI.parse_min_max_text(self.eo_minmax_filter_edit.text())
        acn_min, acn_max, _ = SurfactantDBGUI.parse_min_max_text(self.acn_minmax_filter_edit.text())

        try:

            self.surfactants = self.cnxn.exec_select_surfactants(s_name, c_name, ig_name, m_name, '', po_min, po_max,
                                                                 eo_min, eo_max, acn_min, acn_max, h_name, loc_id)
            self.surfactant_blends = self.cnxn.exec_select_surfactant_blends(s_name, c_name, ig_name, m_name, '',
                                                                             po_min, po_max, eo_min, eo_max, acn_min,
                                                                             acn_max, h_name, loc_id)
            self.populate_surfactant_list()

        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

    def populate_surfactant_list(self):

        self.surfactant_list.clear()
        self.inventory_list.clear()
        s_list = []

        for surfactant in self.surfactants:
            name_string = surfactant[1]
            structure = self.cnxn.exec_get_surfactant_structure(surfactant[0])[0][0]
            structure_string = 'Structure: ' + structure
            manufacturer_string = 'Manufacturer: ' + surfactant[2]
            s_string = name_string.ljust(30) + structure_string.ljust(50) + manufacturer_string
            s_list.append(s_string)

        self.surfactant_list.addItems(s_list)

        s_list = []

        for surfactant in self.surfactant_blends:
            name_string = surfactant[1]
            structure = '***BLEND***'
            structure_string = 'Structure: ' + structure
            manufacturer_string = 'Manufacturer: ' + surfactant[2]
            s_string = name_string.ljust(30) + structure_string.ljust(50) + manufacturer_string
            s_list.append(s_string)

        self.surfactant_list.addItems(s_list)

    def populate_inventory_list(self):

        self.inventory_list.clear()
        i_list = []
        i_tags = []
        quantities = []

        for result in self.inventories:

            if result[2] is None:
                if not self.current_surfactant_is_blend():
                    project_tag = self.cnxn.exec_get_surfactant_project_tag(result[0])
                else:
                    project_tag = self.cnxn.exec_get_surfactant_blend_project_tag(result[0])

                if project_tag:
                    i_tags.append(project_tag[0][0])
                else:
                    i_tags.append(-1)

                lot_string = 'Lot #: ' + result[1]
                act_string = 'Act. %: ' + str(result[5])
                loc_string = 'Loc.: ' + str(result[8])
                quantities.append(result[7])

                if result[4] is None:
                    syn_string = 'Syn. Date: ' + str(result[3])
                    if result[6] is not None:
                        conv_string = 'Conv. %: ' + str(result[6])
                    else:
                        conv_string = 'Conv. %: Unk.'

                    i_string = lot_string.ljust(20) + syn_string.ljust(24) + \
                               act_string.ljust(16) + conv_string.ljust(16) + loc_string

                else:
                    rec_string = 'Rec. Date: ' + str(result[4])
                    conv_string = ''
                    i_string = lot_string.ljust(20) + rec_string.ljust(24) + \
                               act_string.ljust(16) + conv_string.ljust(16) + loc_string

            else:
                i_tags.append(i_tags[-1])
                lot_string = ''
                dil_string = ''
                act_string = 'Act. %: ' + str(result[5])
                conv_string = ''
                loc_string = 'Loc.: ' + str(result[8])
                quantities.append(result[7])

                i_string = lot_string.ljust(20) + dil_string.ljust(24) + act_string.ljust(16) + \
                           conv_string.ljust(16) + loc_string

            i_list.append(i_string)

        self.inventory_list.addItems(i_list)

        if not i_list:
            return

        font = self.inventory_list.item(0).font()
        font.setBold(True)
        brush = QBrush()
        brush.setColor(cQt.lightGray)
        brush_red = QBrush()
        brush_red.setColor(cQt.red)

        for i in range(len(i_list)):
            txt = self.inventory_list.item(i).text()
            if txt[:6] == 'Lot #:':
                self.inventory_list.item(i).setFont(font)
            if quantities[i] == 0:
                self.inventory_list.item(i).setForeground(brush)
            elif i_tags[i] != -1:
                self.inventory_list.item(i).setForeground(brush_red)

    def surfactant_selected(self, item: QListWidgetItem):

        i = self.surfactant_list.indexFromItem(item).row()
        if i <= len(self.surfactants) - 1:
            is_blend = False
            key = self.surfactants[i][0]
        else:
            is_blend = True
            key = self.surfactant_blends[i - len(self.surfactants)][0]

        try:
            if not is_blend:
                self.inventories = self.cnxn.get_stocks_and_dilutions(key)
            else:
                self.inventories = self.cnxn.get_blend_stocks_and_dilutions(key)
            self.populate_inventory_list()
            self.stock_add_btn.setEnabled(True)

        except Exception as e:
            self.stock_add_btn.setEnabled(False)
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

        self.dil_add_btn.setEnabled(False)
        self.inv_remove_btn.setEnabled(False)

    def current_surfactant_is_blend(self) -> bool:

        if self.surfactant_list.currentIndex().row() > len(self.surfactants) - 1:
            return True

        return False

    def inventory_item_selected(self, item: QListWidgetItem):

        if item is None:
            return

        i = self.inventory_list.indexFromItem(item).row()
        inventory_item = self.inventories[i]
        stock_or_dilution = False
        if inventory_item[2] is None:
            sd_id = inventory_item[0]
            stock_or_dilution = True
            self.dil_add_btn.setEnabled(True)
        else:
            sd_id = inventory_item[2]
            self.dil_add_btn.setEnabled(False)

        self.inv_remove_btn.setEnabled(True)

        info = self.cnxn.exec_get_stock_or_dilution_info(sd_id, stock_or_dilution)[0]

        txt = ''
        j = 0

        for item in info:

            if j > 0:
                txt += '\t'

            if j == 2:
                txt += str(float(item) / 100.)
            else:
                txt += str(item)
            j += 1

        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(txt)
            win32clipboard.CloseClipboard()
        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

    def inventory_item_clicked(self, item: QListWidgetItem):

        if item is None:
            return

        i = self.inventory_list.indexFromItem(item).row()
        inventory_item = self.inventories[i]

        if inventory_item[2] is None:
            self.dil_add_btn.setEnabled(True)
        else:
            self.dil_add_btn.setEnabled(False)

        self.inv_remove_btn.setEnabled(True)

    def keyPressEvent(self, a0: QKeyEvent):

        if a0.key() == Qt.Key_Control:
            self.control_pressed = True

        elif a0.key() == Qt.Key_C and self.control_pressed:
            item = self.inventory_list.currentItem()

            if item is None:
                return

            try:
                self.inventory_item_selected(item)
            except Exception as e:
                QMessageBox(parent=self, text=str(e)).exec_()

    def keyReleaseEvent(self, a0: QKeyEvent):

        if a0.key() == Qt.Key_Control:
            self.control_pressed = False

    def inspect_inventory_item(self, item: QListWidgetItem):

        if item is None:
            return

        i = self.inventory_list.indexFromItem(item).row()
        inventory_item = self.inventories[i]

        if self.inventory_item_inspector is None:
            self.inventory_item_inspector = SurfactantInventoryItemInspector(self, inventory_item)
        else:
            self.inventory_item_inspector.load_item(inventory_item)

    def add_stock(self):

        if not self.current_surfactant_is_blend():
            AddStockGUI(parent=self).exec_()

    def add_dilution(self):

        AddDilutionGUI(parent=self).exec_()

    def remove_stock_or_dilution_clicked(self):

        self.db_gui.run_login_with_functions(self.remove_stock_or_dilution, self.reload_inventory)

    def remove_stock_or_dilution(self):

        i = self.inventory_list.currentIndex().row()
        inventory_item = self.inventories[i]
        stock_or_dilution = False

        if inventory_item[2] is None:
            sd_id = inventory_item[0]
            stock_or_dilution = True
        else:
            sd_id = inventory_item[2]

        if stock_or_dilution:
            self.cnxn.exec_delete_stock(sd_id)
        else:
            self.cnxn.exec_delete_dilution(sd_id)

    def reload_inventory(self):

        s = self.surfactant_list.currentItem()
        self.surfactant_list.itemClicked.emit(s)

    def closeEvent(self, _):

        if self.login_dialog is not None:
            self.login_dialog.close()

        if self.inventory_item_inspector is not None:
            self.inventory_item_inspector.close()

        if self.cnxn is not None:
            self.cnxn.close()


class LowStockGUI(QDialog):

    def __init__(self, parent: SurfactantDBGUI):
        super(LowStockGUI, self).__init__(parent=parent)
        self.SDBGUI = parent
        self.sf = parent.sf
        self.setFixedSize(int(self.sf * 250), int(self.sf * 50))
        self.setWindowTitle('Low Qty UEORS Stocks')

        lyt = QGridLayout()
        self.setLayout(lyt)

        qty_label = QLabel(parent=self, text='Cutoff Qty [mL]:')
        self.qty_edit = QLineEdit(parent=self)
        self.qty_edit.setText('100')
        self.qty_edit.editingFinished.connect(self.vet_qty)
        self.export_button = QPushButton(parent=self, text='Export')
        self.export_button.clicked.connect(self.export_low_stocks_clicked)

        lyt.addWidget(qty_label, 0, 0, 1, 1)
        lyt.addWidget(self.qty_edit, 0, 1, 1, 1)
        lyt.addWidget(self.export_button, 0, 2, 1, 1)

    def vet_qty(self):

        txt = self.qty_edit.text()

        try:
            val = round(float(txt), 0)
            val = int(val)
            if val < 1:
                raise ValueError

        except ValueError:
            val = 100

        finally:
            self.qty_edit.blockSignals(True)
            self.qty_edit.setText(str(val))
            self.qty_edit.blockSignals(False)

    def export_low_stocks_clicked(self):

        letter = self.SDBGUI.db_gui.u_or_q

        f = QFileDialog.getSaveFileName(parent=self, caption='Set Export File',
                                        directory=letter + ':\\UEORLAB1\\Python Files\\UEORS_DB_GUI\\',
                                        filter='*.xlsx')
        if not f[0]:
            return

        self.SDBGUI.db_gui.run_login_with_functions(self.export_low_stocks, f)

    def export_low_stocks(self, f):

        qty = int(self.qty_edit.text())

        try:

            low_stock_items = self.SDBGUI.cnxn.exec_get_low_qty_stocks(qty=qty)

            if not low_stock_items:
                QMessageBox(parent=self, text='No items to export.').exec_()
                return

            export_list = []
            j = 0
            for item in low_stock_items:
                j += 1
                print(item)
                export_list.append(list(item[:6]))

            df = pd.DataFrame(export_list, columns=['Surfactant Name', 'Dilution Qty', 'Lot #', 'Synthesis Date',
                                                    'Non-Ionic Qty', 'Non-Ionic Lot #'])

            writer = pd.ExcelWriter(f[0])
            df.to_excel(writer)

            QMessageBox(parent=self, text='Exported {} item(s).'.format(j)).exec_()

        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

        finally:
            self.close()


class AddSurfactantGUI(QDialog):

    def __init__(self, parent: SurfactantDBGUI):
        super(AddSurfactantGUI, self).__init__(parent=parent)
        self.SDBGUI = parent
        self.sf = parent.sf
        self.setFixedSize(int(self.sf * 300), int(self.sf * 400))
        self.setWindowTitle('Add New Surfactant')

        lyt = QGridLayout()

        self.m_label = QLabel(parent=self, text='Manufacturer:')
        self.name_label = QLabel(parent=self, text='Surfactant Name:')
        self.ig_label = QLabel(parent=self, text='Ionic Group:')
        self.n_ig_label = QLabel(parent=self, text='I.G. #:')
        self.h_label = QLabel(parent=self, text='Hydrophobe:')
        self.uh_label = QLabel(parent=self, text='Uncertain Hydrophobe:')
        self.po_label = QLabel(parent=self, text='PO #:')
        self.eo_label = QLabel(parent=self, text='EO #:')
        self.po_eo_rev_label = QLabel(parent=self, text='PO/EO Order:')
        self.nre_label = QLabel(parent=self, text='N.R.E.?:')
        self.n_poeochains_label = QLabel(parent=self, text='PO/EO Chain #:')
        self.mw_label = QLabel(parent=self, text='Molecular Weight:')

        labels = [self.m_label, self.name_label, self.ig_label, self.n_ig_label, self.h_label, self.uh_label,
                  self.po_label, self.eo_label, self.po_eo_rev_label, self.nre_label, self.n_poeochains_label,
                  self.mw_label]

        self.m_combo = QComboBox(parent=self)
        self.name_edit = QLineEdit(parent=self)
        self.ig_combo = QComboBox(parent=self)
        self.n_ig_combo = QComboBox(parent=self)
        self.h_combo = QComboBox(parent=self)
        self.uh_combo = QComboBox(parent=self)
        self.po_edit = QLineEdit(parent=self)
        self.eo_edit = QLineEdit(parent=self)
        self.po_eo_rev_combo = QComboBox(parent=self)
        self.nre_combo = QComboBox(parent=self)
        self.n_poeochains_combo = QComboBox(parent=self)
        self.mw_edit = QLineEdit(parent=self)

        combos_edits = [self.m_combo, self.name_edit, self.ig_combo, self.n_ig_combo, self.h_combo, self.uh_combo,
                        self.po_edit, self.eo_edit, self.po_eo_rev_combo, self.nre_combo, self.n_poeochains_combo,
                        self.mw_edit]

        required_combos = [self.ig_combo, self.n_ig_combo, self.h_combo, self.po_eo_rev_combo, self.nre_combo,
                           self.n_poeochains_combo]

        not_special_required_combos = [self.h_combo, self.uh_combo]

        for r_combo in required_combos:
            r_combo.currentIndexChanged.connect(partial(self.required_combo_index_changed, r_combo))

        self.ig_combo.currentIndexChanged.connect(partial(self.ig_n_ig_index_changed, self.ig_combo))
        self.n_ig_combo.currentIndexChanged.connect(partial(self.ig_n_ig_index_changed, self.n_ig_combo))
        self.name_edit.editingFinished.connect(self.check_name)
        self.mw_edit.editingFinished.connect(self.mw_edited)

        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.clicked.connect(self.submit_clicked)

        r = 0
        for label, combo_edit in zip(labels, combos_edits):
            lyt.addWidget(label, r, 0, 1, 1)
            lyt.addWidget(combo_edit, r, 1, 1, 1)
            r += 1

        lyt.addWidget(self.submit_button, r, 0, 1, 2)

        self.setLayout(lyt)
        self.combos_edits = combos_edits
        self.required_combos = required_combos
        self.not_special_required_combos = not_special_required_combos

        self.initialize_combos()
        self.enable_ui(False)

        self.m_combo.currentIndexChanged.connect(self.manufacturer_index_changed)
        self.h_combo.currentIndexChanged.connect(partial(self.h_uh_index_changed, self.uh_combo))
        self.uh_combo.currentIndexChanged.connect(partial(self.h_uh_index_changed, self.h_combo))
        self.po_edit.editingFinished.connect(lambda: self.po_eo_editing_finished(self.po_edit))
        self.eo_edit.editingFinished.connect(lambda: self.po_eo_editing_finished(self.eo_edit))

        self.show()

    def initialize_combos(self):

        SurfactantDBGUI.set_popup_from_query_result(self.m_combo, self.SDBGUI.cnxn.get_all_companies())
        SurfactantDBGUI.set_popup_from_query_result(self.ig_combo, self.SDBGUI.cnxn.get_all_ionic_groups())
        SurfactantDBGUI.set_popup_from_query_result(self.h_combo, self.SDBGUI.cnxn.get_all_hydrophobes())
        SurfactantDBGUI.set_popup_from_query_result(self.uh_combo, self.SDBGUI.cnxn.get_all_uncertain_hydrophobes())
        self.uh_combo.setEnabled(False)

        n_ig_options = ['', '0', '1', '2', '3']
        self.n_ig_combo.addItems(n_ig_options)
        po_eo_rev_options = ['', 'Normal (PO/EO)', 'Reverse (EO/PO)']
        self.po_eo_rev_combo.addItems(po_eo_rev_options)
        nre_options = ['', 'no', 'yes']
        self.nre_combo.addItems(nre_options)
        n_poeochains_options = ['', '1', '2', '3']
        self.n_poeochains_combo.addItems(n_poeochains_options)

    def is_manufacturer_special(self) -> bool:

        return self.m_combo.currentText() in ['Harcros Chemicals Incorporated', 'Ultimate EOR Services']

    def enable_ui(self, enable: bool):

        for i, combo_edit in enumerate(self.combos_edits):
            if i > 0:
                combo_edit.setEnabled(enable)

        required_combos = [self.ig_combo, self.n_ig_combo, self.h_combo, self.po_eo_rev_combo, self.nre_combo,
                           self.n_poeochains_combo]

        if enable:

            if self.is_manufacturer_special():

                self.name_edit.setText('')
                self.name_edit.setStyleSheet('QLineEdit{background: white};')
                self.name_edit.setEnabled(False)

                self.uh_combo.setCurrentIndex(0)
                self.uh_combo.setStyleSheet('QComboBox{background: white};')
                self.uh_combo.setEnabled(False)

                self.po_eo_editing_finished(self.po_edit)
                self.po_eo_editing_finished(self.eo_edit)

                self.mw_edit.setText('')
                self.mw_edit.setEnabled(False)

                for r_combo in required_combos:
                    self.required_combo_index_changed(r_combo, r_combo.currentIndex())

            else:

                self.name_edit.editingFinished.emit()

                for r_combo in required_combos:
                    r_combo.setStyleSheet('QComboBox{background: white};')

                if self.h_combo.currentIndex():
                    self.h_combo.setCurrentIndex(self.h_combo.currentIndex())
                elif self.uh_combo.currentIndex():
                    self.uh_combo.setCurrentIndex(self.uh_combo.currentIndex())
                else:
                    self.h_combo.setStyleSheet('QComboBox{background: red};')
                    self.uh_combo.setStyleSheet('QComboBox{background: red};')

                self.po_edit.setStyleSheet('QLineEdit{background: white};')
                self.eo_edit.setStyleSheet('QLineEdit{background: white};')

        else:
            self.po_edit.setStyleSheet('QLineEdit{background: white};')
            self.eo_edit.setStyleSheet('QLineEdit{background: white};')
            self.h_combo.setStyleSheet('QComboBox{background: white};')
            self.uh_combo.setStyleSheet('QComboBox{background: white};')

        self.submit_button.setEnabled(False)

    def manufacturer_index_changed(self, i: int):

        self.enable_ui(True)

        if i == 0:
            self.n_poeochains_combo.setCurrentIndex(0)
            self.po_eo_rev_combo.setCurrentIndex(0)
            self.nre_combo.setCurrentIndex(0)
            self.enable_ui(False)
        else:
            c_name = self.m_combo.currentText()
            cnxn = self.SDBGUI.cnxn
            self.n_poeochains_combo.setCurrentIndex(1)
            self.po_eo_rev_combo.setCurrentIndex(1)
            self.nre_combo.setCurrentIndex(1)
            self.SDBGUI.set_popup_from_query_result(self.uh_combo,
                                                    cnxn.exec_get_uncertain_hydrophobes_where_company(c_name=c_name))

    def check_name(self):

        if self.name_edit.text():
            self.name_edit.setStyleSheet('QLineEdit{background: white};')

        else:
            self.name_edit.setStyleSheet('QLineEdit{background: red};')

        self.update_enable_submit()

    def check_enable_submit(self) -> bool:

        if self.is_manufacturer_special():

            required_combos = [self.ig_combo, self.n_ig_combo, self.h_combo, self.po_eo_rev_combo, self.nre_combo,
                               self.n_poeochains_combo]

            for r_combo in required_combos:
                if r_combo.currentIndex() == 0:
                    return False

            if not self.eo_edit.text() or not self.po_edit.text():
                return False

            return True

        else:

            if not self.name_edit.text():
                return False

            if not self.h_combo.currentIndex() and not self.uh_combo.currentIndex():
                return False

            return True

    def update_enable_submit(self):

        self.submit_button.setEnabled(self.check_enable_submit())

    def po_eo_editing_finished(self, edit: QLineEdit):

        try:
            txt = edit.text()
            val = float(txt)
            if val < 0.:
                raise ValueError

        except ValueError:
            edit.setText('')

        edit.setStyleSheet('QLineEdit{background: white};')

        if self.is_manufacturer_special():
            if not edit.text():
                edit.setStyleSheet('QLineEdit{background: red};')

        self.update_enable_submit()

    def required_combo_index_changed(self, combo: QComboBox, i: int):

        if not self.is_manufacturer_special():
            return

        if i == 0:
            combo.setStyleSheet('QComboBox{background: red};')
        else:
            combo.setStyleSheet('QComboBox{background: white};')

        self.update_enable_submit()

    def ig_n_ig_index_changed(self, combo: QComboBox, i: int):

        if i == 0:
            return

        if combo == self.ig_combo:

            if self.ig_combo.currentText() == 'None' and self.n_ig_combo.currentIndex() != 1:
                self.n_ig_combo.setCurrentIndex(1)

            elif self.ig_combo.currentText() != 'None' and self.n_ig_combo.currentIndex() != 2:
                self.n_ig_combo.setCurrentIndex(2)

        else:

            j = self.ig_combo.findText('None')

            if i == 1 and self.ig_combo.currentIndex() != j:
                self.ig_combo.setCurrentIndex(j)

            elif i > 1 and self.ig_combo.currentIndex() == j:
                self.ig_combo.setCurrentIndex(0)

        self.update_enable_submit()

    def h_uh_index_changed(self, combo: QComboBox, i: int):

        if combo.isEnabled() and i:
            combo.blockSignals(True)
            combo.setCurrentIndex(0)
            combo.blockSignals(False)

        if not self.is_manufacturer_special():

            if self.h_combo.currentIndex() == 0 and self.uh_combo.currentIndex() == 0:
                self.h_combo.setStyleSheet('QComboBox{background: red};')
                self.uh_combo.setStyleSheet('QComboBox{background: red};')

            else:
                self.h_combo.setStyleSheet('QComboBox{background: white};')
                self.uh_combo.setStyleSheet('QComboBox{background: white};')

        self.update_enable_submit()

    def mw_edited(self):

        txt = self.mw_edit.text()
        if not txt:
            return

        try:
            val = float(txt)
            if val <= 0:
                raise ValueError

        except ValueError:
            self.mw_edit.setText('')

    def submit_clicked(self):

        self.SDBGUI.db_gui.run_login_with_functions(self.submit_surfactant)

    def submit_surfactant(self):

        def convert_to_null(var: str) -> str:

            if not var.strip():
                return 'NULL'

            return var

        m_name = self.m_combo.currentText()
        s_name = convert_to_null(self.name_edit.text())
        ig_name = convert_to_null(self.ig_combo.currentText())
        n_ig = self.n_ig_combo.currentIndex() - 1
        if n_ig == -1:
            n_ig = 'NULL'
        h_name = convert_to_null(self.h_combo.currentText())
        uh_name = convert_to_null(self.uh_combo.currentText())
        n_po = self.po_edit.text()
        if n_po:
            n_po = float(n_po)
        else:
            n_po = 'NULL'
        n_eo = self.eo_edit.text()
        if n_eo:
            n_eo = float(n_eo)
        else:
            n_eo = 'NULL'

        po_eo_rev = self.po_eo_rev_combo.currentIndex() - 1
        if po_eo_rev == -1:
            po_eo_rev = 'NULL'

        nre = self.nre_combo.currentIndex() - 1
        if nre == -1:
            nre = 'NULL'

        n_poeochains = convert_to_null(self.n_poeochains_combo.currentText())
        if n_poeochains != 'NULL':
            n_poeochains = int(n_poeochains)

        mw = self.mw_edit.text()
        if mw:
            mw = float(mw)
        else:
            mw = 'NULL'

        args = (s_name, m_name, uh_name, h_name, n_eo, n_po, ig_name, mw, n_ig, nre, po_eo_rev, n_poeochains)

        self.SDBGUI.cnxn.exec_add_surfactant(*args)
        self.SDBGUI.search_btn.clicked.emit()

        self.close()


class InventoryExportGUI(QDialog):

    def __init__(self, parent: SurfactantDBGUI):
        super(InventoryExportGUI, self).__init__(parent=parent)
        self.sf = parent.sf
        self.SDBGUI = parent
        self.setFixedSize(int(self.sf * 400.), int(self.sf * 200.))
        self.setWindowTitle('Export Inventory')
        lyt = QGridLayout()
        self.setLayout(lyt)

        received_filter_label = QLabel(parent=self, text='Received Date Filter (may leave blank)')
        received_after_label = QLabel(parent=self, text='After (MM/DD/YYYY):')
        self.received_after_edit = QLineEdit(parent=self)
        self.received_after_edit.editingFinished.connect(lambda: self.vet_date(self.received_after_edit))
        received_before_label = QLabel(parent=self, text='Before (MM/DD/YYYY):')
        self.received_before_edit = QLineEdit(parent=self)
        self.received_before_edit.editingFinished.connect(lambda: self.vet_date(self.received_before_edit))

        synthesized_filter_label = QLabel(parent=self, text='Synthesized Date Filter (may leave blank)')
        synthesized_after_label = QLabel(parent=self, text='After (MM/DD/YYYY):')
        self.synthesized_after_edit = QLineEdit(parent=self)
        self.synthesized_after_edit.editingFinished.connect(lambda: self.vet_date(self.synthesized_after_edit))
        synthesized_before_label = QLabel(parent=self, text='Before: (MM/DD/YYYY)')
        self.synthesized_before_edit = QLineEdit(parent=self)
        self.synthesized_before_edit.editingFinished.connect(lambda: self.vet_date(self.synthesized_before_edit))

        self.okay_button = QPushButton(parent=self, text='Okay')
        self.okay_button.clicked.connect(self.export_inventory)

        lyt.addWidget(received_filter_label, 0, 0, 1, 4)
        lyt.addWidget(received_after_label, 1, 0, 1, 1)
        lyt.addWidget(self.received_after_edit, 1, 1, 1, 1)
        lyt.addWidget(received_before_label, 1, 2, 1, 1)
        lyt.addWidget(self.received_before_edit, 1, 3, 1, 1)
        lyt.addWidget(synthesized_filter_label, 2, 0, 1, 4)
        lyt.addWidget(synthesized_after_label, 3, 0, 1, 1)
        lyt.addWidget(self.synthesized_after_edit, 3, 1, 1, 1)
        lyt.addWidget(synthesized_before_label, 3, 2, 1, 1)
        lyt.addWidget(self.synthesized_before_edit, 3, 3, 1, 1)
        lyt.addWidget(QLabel(parent=self, text=''), 4, 0, 1, 1)
        lyt.addWidget(self.okay_button, 5, 1, 1, 2)

        self.show()

    @staticmethod
    def vet_date(edit: QLineEdit):

        txt = edit.text().strip().split('/')

        if len(txt) != 3:
            edit.setText('')
            return

        mm = txt[0]
        dd = txt[1]
        yyyy = txt[2]

        for part in [mm, dd, yyyy]:

            try:
                part = float(part)
                if part != int(part) or part <= 0:
                    raise ValueError

            except ValueError:
                edit.setText('')
                edit.setStyleSheet('QLineEdit{background: white};')
                return

        mm = int(mm)
        dd = int(dd)
        yyyy = int(yyyy)

        if mm > 12 or dd > 31 or yyyy < 1900 or yyyy > 2100:
            edit.setText('')

        edit.setStyleSheet('QLineEdit{background: white};')

    def export_inventory(self):

        letter = self.SDBGUI.db_gui.u_or_q

        f = QFileDialog.getSaveFileName(parent=self, caption='Set Export File',
                                        directory=letter + ':\\UEORLAB1\\Python Files\\UEORS_DB_GUI\\',
                                        filter='*.xlsx')
        if not f[0]:
            return

        c_name = self.SDBGUI.class_filter_combo.currentText()
        ig_name = self.SDBGUI.ig_filter_combo.currentText()
        m_name = self.SDBGUI.manufacturer_filter_edit.text()
        h_name = self.SDBGUI.hydrophobe_filter_combo.currentText()
        loc_id = self.SDBGUI.location_filter_combo.currentIndex()

        po_min, po_max, _ = SurfactantDBGUI.parse_min_max_text(self.SDBGUI.po_minmax_filter_edit.text())
        eo_min, eo_max, _ = SurfactantDBGUI.parse_min_max_text(self.SDBGUI.eo_minmax_filter_edit.text())
        acn_min, acn_max, _ = SurfactantDBGUI.parse_min_max_text(self.SDBGUI.acn_minmax_filter_edit.text())

        syn_after_date = self.synthesized_after_edit.text()
        if not syn_after_date:
            syn_after_date = 'NULL'
        else:
            mmddyyyy = syn_after_date.split('/')
            syn_after_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        syn_before_date = self.synthesized_before_edit.text()
        if not syn_before_date:
            syn_before_date = 'NULL'
        else:
            mmddyyyy = syn_before_date.split('/')
            syn_before_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        rec_after_date = self.received_after_edit.text()
        if not rec_after_date:
            rec_after_date = 'NULL'
        else:
            mmddyyyy = rec_after_date.split('/')
            rec_after_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        rec_before_date = self.received_before_edit.text()
        if not rec_before_date:
            rec_before_date = 'NULL'
        else:
            mmddyyyy = rec_before_date.split('/')
            rec_before_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        try:

            inv_items = self.SDBGUI.cnxn.exec_select_inv_items(c_name, ig_name, m_name, '', po_min, po_max, eo_min,
                                                               eo_max, acn_min, acn_max, h_name, loc_id,
                                                               rec_after_date, rec_before_date, syn_after_date,
                                                               syn_before_date)

            if not inv_items:
                QMessageBox(parent=self, text='No items to export.').exec_()
                return

            export_list = []
            j = 0
            for item in inv_items:
                j += 1
                print(item)
                export_list.append(list(item[:7]))
                for i in range(5):
                    export_list[-1].append(None)

            df = pd.DataFrame(export_list, columns=['Name', 'Structure', 'Stock ID', 'Dilution ID', 'Lot #', 'Act. %',
                                                    'Qty [mL]', 'pH', 'adjusted?', 'Date', 'Filtered?', 'F. Date'])

            writer = pd.ExcelWriter(f[0])
            df.to_excel(writer)

            QMessageBox(parent=self, text='Exported {} item(s).'.format(j)).exec_()

        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

        finally:
            self.close()

    def submit_clicked(self):

        self.SDBGUI.db_gui.run_login_with_functions(self.submit_stock)

    def submit_stock(self):

        s_id = self.s_id
        lot_num = self.lot_edit.text()
        act = float(self.act_edit.text())
        qty = int(self.qty_edit.text())
        loc_id = self.loc_combo.currentIndex()

        conv = self.conv_edit.text()
        if conv:
            conv = float(conv)
        else:
            conv = 'NULL'

        syn_date = self.syn_edit.text()
        if not syn_date:
            syn_date = 'NULL'
        else:
            mmddyyyy = syn_date.split('/')
            syn_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        rec_date = self.rec_edit.text()
        if not rec_date:
            rec_date = 'NULL'
        else:
            mmddyyyy = rec_date.split('/')
            rec_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        data_str = 's_id = {}, lot_num = {}, act % = {:.1f}, conv % = {}, syn_date = {}, rec_date = {}, qty = {}'
        data_str += ', loc_id = {}'

        self.SDBGUI.cnxn.exec_submit_stock(s_id=s_id, lot_num=lot_num, act_perc=act, conv_perc=conv, syn_date=syn_date,
                                           rec_date=rec_date, qty=qty, loc_id=loc_id)


class LotLabel(QLabel):

    lotCopied = pyqtSignal()

    def __init__(self, parent, text: str, color: str):
        super(LotLabel, self).__init__(parent=parent, text=text)
        self.color = color

    def run_func_and_reset_font(self, func):

        ps = self.font().pointSize()
        func()
        f = self.font()
        f.setPointSize(ps)
        self.setFont(f)

    def enterEvent(self, a0):
        super(LotLabel, self).enterEvent(a0)

        self.run_func_and_reset_font(lambda: self.setStyleSheet('QLabel {color: blue};'))

    def leaveEvent(self, a0):
        super(LotLabel, self).leaveEvent(a0)

        self.run_func_and_reset_font(lambda: self.setStyleSheet('QLabel {color: ' + self.color + '};'))

    def mouseDoubleClickEvent(self, a0):
        super(LotLabel, self).mouseDoubleClickEvent(a0)

        self.lotCopied.emit()


class SurfactantInventoryItemInspector(QDialog):

    def __init__(self, parent: SurfactantDBGUI, inv_item: tuple):
        super(SurfactantInventoryItemInspector, self).__init__(parent=parent)
        self.SDBGUI = parent
        self.sf = parent.sf
        self.setFixedSize(int(self.sf * 350.), int(self.sf * 500.))
        self.setWindowTitle(' ')
        self.mts = []

        lyt = QGridLayout()

        self.name_label = QLabel(parent=self, text='')
        self.manufacturer_label = QLabel(parent=self, text='')
        self.structure_label = QLabel(parent=self, text='')

        self.lot_label = LotLabel(parent=self, text='', color='black')
        self.lot_label.lotCopied.connect(self.copy_lot)
        self.project_label = LotLabel(parent=self, text='Project:', color='black')
        self.project_label.lotCopied.connect(self.set_project_tag)
        self.date_label = QLabel(parent=self, text='')
        self.conversion_label = QLabel(parent=self, text='Conversion %:')
        self.conversion_edit = QLineEdit(parent=self)
        self.conversion_edit.editingFinished.connect(self.check_conversion)
        self.activity_conversion_label = QLabel(parent=self, text='')
        self.quantity_label = QLabel(parent=self, text='Quantity [mL]:')
        self.quantity_edit = QLineEdit(parent=self)
        self.quantity_edit.editingFinished.connect(self.check_qty)

        self.location_label = QLabel(parent=self, text='Location:')
        self.location_combo = QComboBox(parent=self)
        self.notes_label = QLabel(parent=self, text='Notes:')
        self.notes_edit = QTextEdit(parent=self)
        self.notes_edit.textChanged.connect(self.check_notes)

        self.submit_changes_button = QPushButton(parent=self, text='Submit Changes')
        self.submit_changes_button.clicked.connect(self.submit_changes)

        self.mts_label = QLabel(parent=self, text='Measurements and Treatments:')
        self.mts_list = QListWidget(parent=self)
        self.mts_list.itemClicked.connect(self.mt_selected)
        add_remove_widget = QWidget()
        self.add_mt_button = QPushButton(parent=add_remove_widget, text='Add')
        self.add_mt_button.clicked.connect(self.add_mt)
        self.remove_mt_button = QPushButton(parent=add_remove_widget, text='Remove')
        add_remove_widget.setLayout(QHBoxLayout())
        add_remove_widget.layout().addWidget(self.add_mt_button)
        add_remove_widget.layout().addWidget(self.remove_mt_button)

        lyt.addWidget(self.name_label, 0, 0, 1, 2)
        lyt.addWidget(self.manufacturer_label, 1, 0, 1, 2)
        lyt.addWidget(self.structure_label, 2, 0, 1, 2)
        lyt.addWidget(self.lot_label, 3, 0, 1, 2)
        lyt.addWidget(self.project_label, 4, 0, 1, 2)
        lyt.addWidget(self.date_label, 5, 0, 1, 2)
        lyt.addWidget(self.activity_conversion_label, 6, 0, 1, 2)
        lyt.addWidget(self.conversion_label, 7, 0, 1, 1)
        lyt.addWidget(self.conversion_edit, 7, 1, 1, 1)
        lyt.addWidget(self.quantity_label, 8, 0, 1, 1)
        lyt.addWidget(self.quantity_edit, 8, 1, 1, 1)
        lyt.addWidget(self.location_label, 9, 0, 1, 1)
        lyt.addWidget(self.location_combo, 9, 1, 1, 1)
        lyt.addWidget(self.notes_label, 10, 0, 1, 1)
        lyt.addWidget(self.notes_edit, 11, 0, 1, 2)
        lyt.addWidget(self.submit_changes_button, 12, 1, 1, 1)
        lyt.addWidget(self.mts_label, 13, 0, 1, 2)
        lyt.addWidget(self.mts_list, 14, 0, 3, 2)
        lyt.addWidget(add_remove_widget, 17, 1, 1, 1)

        self.remove_mt_button.setEnabled(False)
        self.remove_mt_button.clicked.connect(self.remove_mt)

        self.setLayout(lyt)

        self.surfactant = None
        self.inv_item = None
        self.stock_item = None
        self.is_blend = False
        self.current_surf_i = -1
        self.current_inv_i = -1
        self.initialize_location_combo()

        self.original_conversion = -1
        self.original_qty = -1
        self.original_location = -1
        self.original_notes = ''
        try:
            self.load_item(inv_item)
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

        self.show()

        self.location_combo.currentIndexChanged.connect(self.check_location)
        self.mt_dlg = None

    def mt_selected(self, _):
        self.remove_mt_button.setEnabled(True)

    def initialize_location_combo(self):

        locations = [' ']
        result = self.SDBGUI.cnxn.exec_get_all_location_strings()

        for loc in result:
            locations.append(loc[0])

        self.location_combo.clear()
        self.location_combo.addItems(locations)

    def copy_lot(self):

        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(self.stock_item[2])
            win32clipboard.CloseClipboard()
        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()

    def set_project_tag(self):

        try:
            ProjectTagDlg(self).exec_()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    @staticmethod
    def set_widget_background(widget, color: str):

        widget.setStyleSheet('{}'.format(widget.__class__.__name__) + '{' + 'background: {}'.format(color) + '};')

    def check_conversion(self):

        txt = self.conversion_edit.text()
        color = 'white'

        try:

            if txt:
                conv = round(float(txt), 1)
                self.conversion_edit.setText(str(conv))

                if conv < 0.:
                    raise ValueError

                if conv != self.original_conversion:
                    color = 'yellow'

            elif self.original_conversion is not None:
                    color = 'yellow'

        except ValueError:
            if self.original_conversion is not None:
                self.conversion_edit.setText(str(self.original_conversion))
            else:
                self.conversion_edit.setText('')

        finally:
            self.set_widget_background(self.conversion_edit, color)

    def check_qty(self):

        txt = self.quantity_edit.text()
        color = 'white'

        try:
            qty = float(txt)
            if qty != int(qty):
                raise ValueError

            if qty != self.original_qty:
                color = 'yellow'

        except ValueError:
            self.quantity_edit.setText(str(self.original_qty))

        finally:
            self.set_widget_background(self.quantity_edit, color)

    def check_notes(self):

        txt = self.notes_edit.toPlainText()
        if len(txt) > 240:
            self.notes_edit.setText(txt[:240])
            QMessageBox(parent=self, text='You have exceeded the 240 character limit.').exec_()
            return
        color = 'white'

        if txt != self.original_notes:
            color = 'yellow'

        self.set_widget_background(self.notes_edit, color)

    def check_location(self, _):

        loc = self.location_combo.currentIndex()
        pallete = self.location_combo.palette()

        if loc != self.original_location:
            pallete.setColor(QPalette.Button, QColor(255, 255, 0))
        else:
            pallete.setColor(QPalette.Button, QColor(255, 255, 255))

        self.location_combo.setPalette(pallete)

    def populate_mts_list(self, inv_item: tuple):

        self.mts_list.clear()

        is_stock = False
        sd_id = inv_item[2]
        if inv_item[2] is None:
            is_stock = True
            sd_id = inv_item[0]

        if not self.is_blend:
            mts = self.SDBGUI.cnxn.exec_get_measurements_and_treatments(sd_id, is_stock)
        else:
            mts = self.SDBGUI.cnxn.exec_get_blend_measurements_and_treatments(sd_id, is_stock)

        self.mts = copy.copy(mts)

        for mt in mts:
            mt_string = mt[2]
            mt_val = mt[3]
            mt_date = mt[4]
            if mt_date is not None:
                mt_date = str(mt_date)

            try:
                item = QListWidgetItem('{}, val = {}, date = {}'.format(mt_string, mt_val, mt_date))
                self.mts_list.addItem(item)
            except Exception as e:
                print('Exception: {}'.format(e))

    def load_item(self, inv_item: tuple):

        loc_string = inv_item[-1]
        ans = self.location_combo.findText(loc_string)
        self.original_location = ans

        if ans > -1:
            self.location_combo.setCurrentIndex(ans)
        else:
            self.location_combo.setCurrentIndex(0)

        self.inv_item = inv_item

        self.is_blend = self.SDBGUI.current_surfactant_is_blend()
        self.current_surf_i = self.SDBGUI.surfactant_list.currentIndex().row()
        self.current_inv_i = self.SDBGUI.inventory_list.currentIndex().row()

        self.update_stock()
        self.update_surfactant()

        name = self.surfactant[1]
        if name is None:
            name = 'UEOR ' + self.SDBGUI.cnxn.exec_get_surfactant_name(self.surfactant[0])[0][0]

        manufacturer = self.SDBGUI.cnxn.exec_get_surfactant_manufacturer_name(self.surfactant[0])[0][0]

        self.name_label.setText('Name: {}'.format(name))
        self.manufacturer_label.setText('Manufacturer: {}'.format(manufacturer))

        self.lot_label.setText('Lot #: {}'.format(self.stock_item[2]))

        project = None

        if not self.is_blend:
            project_tag = self.SDBGUI.cnxn.exec_get_surfactant_project_tag(self.inv_item[0])
        else:
            project_tag = self.SDBGUI.cnxn.exec_get_surfactant_blend_project_tag(self.inv_item[0])

        if project_tag:
            project_tag = project_tag[0][0]
            project = self.SDBGUI.cnxn.exec_get_project_name_from_id(project_tag)[0][0]

        self.project_label.setText('Project: {}'.format(project))
        font = self.project_label.font()
        color = 'black'
        if project is None:
            font.setBold(False)
        else:
            color = 'red'
            font.setBold(True)

        self.project_label.setFont(font)
        self.project_label.color = color
        self.project_label.setStyleSheet('QLabel{color: ' + color + '};')
        self.date_label.setText('Received Date: {}  |  Synthesis Date: {}'.format(str(self.stock_item[3]),
                                                                                  str(self.stock_item[4])))

        if self.stock_item[6] is not None:
            self.activity_conversion_label.setText('Activity %: {:.1f}'.format(float(self.inv_item[5])))
        else:
            self.activity_conversion_label.setText('Activity %: {:.1f}'.format(float(self.inv_item[5])))

        if not self.is_blend:
            uh_id = self.surfactant[3]
            h_id = self.surfactant[4]
            n_eo = self.surfactant[5]
            if n_eo is not None:
                if n_eo == int(n_eo):
                    n_eo = int(n_eo)
            else:
                n_eo = '??'
            n_po = self.surfactant[6]
            if n_po is not None:
                if n_po == int(n_po):
                    n_po = int(n_po)
            else:
                n_po = '??'
            ig_id = self.surfactant[7]

            if uh_id is None:
                table = DBObjects.Tables.HTable
                column = DBObjects.Columns.HName
                key = DBObjects.Columns.HID
                value = h_id
            else:
                table = DBObjects.Tables.UHTable
                column = DBObjects.Columns.UHFormula
                key = DBObjects.Columns.UHID
                value = uh_id

            h_name = self.SDBGUI.cnxn.get_column_from_table_where(table, column, key, value)[0][0]
            ig_name = self.SDBGUI.cnxn.get_column_from_table_where(DBObjects.Tables.IGTable, DBObjects.Columns.IGName,
                                                                   DBObjects.Columns.IGID, ig_id)[0][0]
            n_ig = self.surfactant[12]
            if n_ig > 1:
                ig_name = str(n_ig) + 'x' + ig_name
            if ig_name == 'None':
                ig_name = 'OH'

            nre = self.surfactant[13]
            if nre:
                nre_name = ' (N.R.E.)'
            else:
                nre_name = ''

            if self.surfactant[-2] == 0:
                self.structure_label.setText(
                    'Structure: {}-{}PO-{}EO-{}{}'.format(h_name, n_po, n_eo, ig_name, nre_name))
            else:
                self.structure_label.setText(
                    'Structure: {}-{}EO-{}PO-{}{}'.format(h_name, n_eo, n_po, ig_name, nre_name))

        else:
            composition = self.SDBGUI.cnxn.exec_get_blend_stock_composition(self.stock_item[0])[0]
            s_ids = composition[:5]
            percs = composition[5:]
            structure = ''
            for s_id, perc in zip(s_ids, percs):
                if s_id is None:
                    break
                s_name_i = self.SDBGUI.cnxn.exec_get_surfactant_name(s_id)[0][0]
                if perc is None:
                    structure += '{}, '.format(s_name_i)
                else:
                    structure += '{:.1f}% {}, '.format(perc, s_name_i)

            structure = structure[:-2]
            self.structure_label.setText('Structure: {}'.format(structure))

        if self.inv_item[2] is None:
            if not self.is_blend:
                table = DBObjects.Tables.StkTable
                key = DBObjects.Columns.StkID
            else:
                table = DBObjects.Tables.BlendStkTable
                key = DBObjects.Columns.BlendStkID
            value = self.inv_item[0]
        else:
            if not self.is_blend:
                table = DBObjects.Tables.DilTable
                key = DBObjects.Columns.DilID
            else:
                table = DBObjects.Tables.BlendDilTable
                key = DBObjects.Columns.BlendDilID
            value = self.inv_item[2]

        notes = self.SDBGUI.cnxn.get_column_from_table_where(table, DBObjects.Columns.Notes, key, value)[0][0]

        self.original_qty = self.inv_item[7]
        self.original_conversion = self.stock_item[6]
        self.original_notes = notes
        if self.original_conversion is not None:
            self.conversion_edit.setText('{:.1f}'.format(self.original_conversion))
        else:
            self.conversion_edit.setText('')
        if self.inv_item[2] is None:
            self.conversion_edit.setEnabled(True)
        else:
            self.conversion_edit.setEnabled(False)
        self.quantity_edit.setText('{}'.format(self.inv_item[7]))
        self.notes_edit.setText(notes)

        self.populate_mts_list(inv_item)

        self.notes_edit.setStyleSheet('QTextEdit{background: white};')
        self.quantity_edit.setStyleSheet('QLineEdit{background: white};')
        self.conversion_edit.setStyleSheet('QLineEdit{background: white};')
        pallete = self.location_combo.palette()
        pallete.setColor(QPalette.Button, QColor(255, 255, 255))
        self.location_combo.setPalette(pallete)

    def update_stock(self):

        if not self.is_blend:
            self.stock_item = self.SDBGUI.cnxn.get_all_stock_data(self.inv_item[0])[0]
        else:
            self.stock_item = self.SDBGUI.cnxn.exec_get_blend_stock_info(self.inv_item[0])[0]

    def update_surfactant(self):

        if not self.is_blend:
            self.surfactant = self.SDBGUI.cnxn.get_surfactant_info(self.stock_item[1])[0]
        else:
            self.surfactant = self.SDBGUI.cnxn.exec_get_blend_info(self.stock_item[1])[0]

    def run_login_with_functions(self, func, func_finally):

        ueors_db_gui = self.parent().parent().parent().parent().parent()
        ueors_db_gui.run_login_with_functions(func, func_finally)

        # try:
        #
        #     if ueors_db_gui.login_dialog is None:
        #         dlg = db_tools.LoginDialog(parent=self)
        #         ueors_db_gui.link_login_dialog(dlg)
        #         dlg.exec()
        #
        #         if not ueors_db_gui.current_user_is_default():
        #
        #             func()
        #
        # except Exception as e:
        #     QMessageBox(parent=self, text=str(e)).exec_()
        #
        # finally:
        #     ueors_db_gui.login_default()
        #     if func_finally is not None:
        #         func_finally()

    def submit_changes(self):

        print(self.inv_item)

        is_stock = True

        if self.inv_item[2] is not None:
            is_stock = False

        update_location = False
        update_conversion = False
        update_qty = False
        update_notes = False

        loc_id = self.location_combo.currentIndex()
        if loc_id != self.original_location:
            update_location = True
            print('Submitting new location; old = {}, new = {}'.format(self.original_location, loc_id))

        conv = self.conversion_edit.text()
        if not conv and self.original_conversion is not None:
            update_conversion = True
            conv = 'NULL'
            print('Submitting new conv; old = {}, new = Unknown'.format(self.original_conversion))
        elif conv:
            conv = float(conv)
            if self.original_conversion is None or conv != self.original_conversion:
                update_conversion = True
                print('Submitting new conv; old = {}, new = {}'.format(self.original_conversion, conv))

        qty = int(self.quantity_edit.text())
        if qty != self.original_qty:
            update_qty = True
            print('Submitting new qty; old = {}, new = {}'.format(self.original_qty, qty))

        notes = self.notes_edit.toPlainText()
        if notes != self.original_notes:
            update_notes = True
            print('Submitting new notes; old = {}, new = {}'.format(self.original_notes, notes))

        if not any([update_location, update_conversion, update_qty, update_notes]):
            QMessageBox(parent=self, text='No changes to submit.').exec_()
            return

        if not update_location:
            loc_id = -1
        if not update_conversion:
            conv = -1
        if not update_qty:
            qty = -1

        self.run_login_with_functions(lambda: self.submit_changes_func(is_stock=is_stock, loc_id=loc_id, conv=conv,
                                                                       qty=qty, notes=notes,
                                                                       update_notes=update_notes), None)

    def submit_changes_func(self, is_stock: bool, loc_id: int, conv, qty: float, notes: str, update_notes: bool):

        if is_stock:
            sd_id = self.inv_item[0]
        else:
            sd_id = self.inv_item[2]

        if loc_id != -1:
            if not self.is_blend:
                self.SDBGUI.cnxn.exec_set_stock_or_dilution_loc(is_stock=is_stock, sd_id=sd_id, loc_id=loc_id)
            else:
                self.SDBGUI.cnxn.exec_set_blend_stock_or_dilution_loc(is_stock=is_stock, sd_id=sd_id, loc_id=loc_id)

        if isinstance(conv, str) or conv != -1:
            if not self.is_blend:
                self.SDBGUI.cnxn.exec_update_stock_conv_perc(stock_id=sd_id, conv_perc=conv)
            else:
                self.SDBGUI.cnxn.exec_update_blend_stock_conv_perc(stock_id=sd_id, conv_perc=conv)

        if qty != -1:
            if not self.is_blend:
                self.SDBGUI.cnxn.exec_set_stock_or_dilution_qty(is_stock=is_stock, sd_id=sd_id, qty=qty)
            else:
                print('setting blend stock or dilution qty')
                self.SDBGUI.cnxn.exec_set_blend_stock_or_dilution_qty(is_stock=is_stock, sd_id=sd_id, qty=qty)

        if update_notes:
            if not self.is_blend:
                self.SDBGUI.cnxn.exec_set_stock_or_dilution_notes(is_stock=is_stock, sd_id=sd_id, notes=notes)
            else:
                self.SDBGUI.cnxn.exec_set_blend_stock_or_dilution_notes(is_stock=is_stock, sd_id=sd_id, notes=notes)

        self.SDBGUI.surfactant_list.setCurrentRow(self.current_surf_i)
        item = self.SDBGUI.surfactant_list.currentItem()
        self.SDBGUI.surfactant_list.itemClicked.emit(item)

        self.SDBGUI.inventory_list.setCurrentRow(self.current_inv_i)
        item = self.SDBGUI.inventory_list.currentItem()
        self.SDBGUI.inventory_list.itemDoubleClicked.emit(item)

    def add_mt(self):

        if self.mt_dlg is None:
            dlg = AddMTDlg(self)
            self.mt_dlg = dlg
            dlg.exec_()

    def remove_mt(self):

        is_stock = True

        if self.inv_item[2] is not None:
            is_stock = False

        mt = self.mts[self.mts_list.currentIndex().row()]
        mt_id = mt[0]

        self.run_login_with_functions(lambda: self.remove_mt_func(is_stock=is_stock, mt_id=mt_id),
                                      self.remove_mt_finally_func)

    def remove_mt_func(self, is_stock: bool, mt_id: int):

        if not self.is_blend:
            self.SDBGUI.cnxn.exec_remove_measurement_or_treatment(is_stock=is_stock, mt_id=mt_id)
        else:
            self.SDBGUI.cnxn.exec_remove_blend_measurement_or_treatment(is_stock=is_stock, mt_id=mt_id)

    def remove_mt_finally_func(self):

        self.populate_mts_list(self.inv_item)

    def closeEvent(self, _):

        self.SDBGUI.inventory_item_inspector = None

        if self.mt_dlg is not None:
            self.mt_dlg.close()


class ProjectTagDlg(QDialog):

    def __init__(self, parent: SurfactantInventoryItemInspector):
        super(ProjectTagDlg, self).__init__(parent=parent)
        sf = parent.sf
        self.SIII = parent
        self.sf = sf
        self.setFixedSize(int(sf * 350), int(sf * 200))
        self.setWindowTitle('Add/Remove project tag')

        self.project = None

        lyt = QGridLayout()
        self.setLayout(lyt)

        self.project_tag_text = QLabel(parent=self)
        self.remove_tag_button = QPushButton(parent=self, text='Remove')
        self.remove_tag_button.clicked.connect(self.remove_project_tag_clicked)
        self.company_combo = QComboBox(parent=self)
        self.company_combo.currentTextChanged.connect(self.company_combo_current_text_changed)
        self.project_listbox = QListWidget(parent=self)
        self.project_listbox.currentRowChanged.connect(self.project_clicked)
        self.add_tag_button = QPushButton(parent=self, text='Add')
        self.add_tag_button.clicked.connect(self.add_tag_clicked)

        lyt.addWidget(self.project_tag_text, 0, 0, 1, 1)
        lyt.addWidget(self.remove_tag_button, 0, 1, 1, 1)
        lyt.addWidget(self.company_combo, 1, 0, 1, 2)
        lyt.addWidget(self.project_listbox, 2, 0, 1, 2)
        lyt.addWidget(self.add_tag_button, 3, 1, 1, 1)

        self.load_company_combo()
        self.refresh_project_tag_text()

    def load_company_combo(self):

        self.company_combo.clear()
        companies = self.SIII.SDBGUI.cnxn.get_all_companies()
        companies_list = list()

        for company in companies:
            companies_list.append(company[0])

        self.company_combo.addItems(companies_list)
        self.company_combo.currentTextChanged.emit(self.company_combo.currentText())

    def company_combo_current_text_changed(self, company_name: str):

        self.project_listbox.clear()
        self.add_tag_button.setEnabled(False)
        projects = self.SIII.SDBGUI.cnxn.get_projects_for_company_name(company_name)

        projects_list = list()

        for project in projects:
            projects_list.append(project[0])

        self.project_listbox.addItems(projects_list)

    def refresh_project_tag_text(self):

        project = None
        self.remove_tag_button.setEnabled(False)

        if not self.SIII.is_blend:
            project_tag = self.SIII.SDBGUI.cnxn.exec_get_surfactant_project_tag(self.SIII.inv_item[0])
        else:
            project_tag = self.SIII.SDBGUI.cnxn.exec_get_surfactant_blend_project_tag(self.SIII.inv_item[0])

        if project_tag:
            project_tag = project_tag[0][0]
            project = self.SIII.SDBGUI.cnxn.exec_get_project_name_from_id(project_tag)[0][0]

        self.project = project

        self.project_tag_text.setText('Project: {}'.format(project))

        if project is not None:
            self.remove_tag_button.setEnabled(True)

    def remove_project_tag_clicked(self):

        self.SIII.SDBGUI.db_gui.run_login_with_functions(self.remove_project_tag, self.refresh_project_tag_text)

    def remove_project_tag(self):

        if self.SIII.is_blend:
            self.SIII.SDBGUI.cnxn.exec_remove_surfactant_blend_project_tag(self.SIII.inv_item[0])

        else:
            self.SIII.SDBGUI.cnxn.exec_remove_surfactant_project_tag(self.SIII.inv_item[0])

    def project_clicked(self, _):

        self.add_tag_button.setEnabled(True)

    def add_tag_clicked(self):

        self.SIII.SDBGUI.db_gui.run_login_with_functions(self.add_project_tag, self.refresh_project_tag_text)

    def add_project_tag(self):

        p_name = self.project_listbox.currentItem().text()
        stock_id = self.SIII.inv_item[0]

        if self.SIII.is_blend:
            self.SIII.SDBGUI.cnxn.exec_add_surfactant_blend_project_tag(stock_id, p_name)

        else:
            self.SIII.SDBGUI.cnxn.exec_add_surfactant_project_tag(stock_id, p_name)

    def closeEvent(self, _):

        self.SIII.load_item(self.SIII.inv_item)


class AddMTDlg(QDialog):

    def __init__(self, parent: SurfactantInventoryItemInspector):
        super(AddMTDlg, self).__init__(parent=parent)
        sf = parent.sf
        self.SIII = parent
        self.inv_item = copy.copy(self.SIII.inv_item)
        self.sf = sf
        self.setFixedSize(int(sf * 350), int(sf * 200))
        self.setWindowTitle('Add measurement or treatment')

        date_widget = QWidget(parent=self)
        date_widget.setLayout(QHBoxLayout())

        today = str(datetime.date.today())
        today = today.split('-')

        self.year_edit = QLineEdit(parent=date_widget)
        self.year_edit.setText(today[0])
        self.year_edit.editingFinished.connect(lambda: self.check_date_edit(self.year_edit, 1900, 2100))
        self.month_edit = QLineEdit(parent=date_widget)
        self.month_edit.setText(today[1])
        self.month_edit.editingFinished.connect(lambda: self.check_date_edit(self.month_edit, 1, 12))
        self.day_edit = QLineEdit(parent=date_widget)
        self.day_edit.setText(today[2])
        self.day_edit.editingFinished.connect(lambda: self.check_date_edit(self.day_edit, 1, 31))

        date_widget.layout().addWidget(self.year_edit)
        date_widget.layout().addWidget(QLabel(text='/'))
        date_widget.layout().addWidget(self.month_edit)
        date_widget.layout().addWidget(QLabel(text='/'))
        date_widget.layout().addWidget(self.day_edit)

        self.type_combo = QComboBox(parent=self)
        self.type_combo.currentIndexChanged.connect(self.set_value_edit_active)
        self.value_label = QLabel(parent=self, text='Value:')
        self.value_edit = QLineEdit(parent=self)
        self.value_edit.setEnabled(False)

        self.add_button = QPushButton(parent=self, text='Add')
        self.add_button.clicked.connect(self.add_mt)
        self.remove_button = QPushButton(parent=self, text='Remove')
        self.remove_button.setEnabled(False)
        self.remove_button.clicked.connect(self.remove_mt)

        self.mt_list = QListWidget(parent=self)
        self.mt_list.itemClicked.connect(self.set_remove_button_enabled)

        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_mts)

        lyt = QGridLayout()
        lyt.addWidget(date_widget, 0, 0, 1, 2)
        lyt.addWidget(self.type_combo, 0, 2, 1, 1)
        lyt.addWidget(self.value_label, 0, 3, 1, 1)
        lyt.addWidget(self.value_edit, 0, 4, 1, 1)
        lyt.addWidget(self.add_button, 1, 0, 1, 1)
        lyt.addWidget(self.remove_button, 1, 1, 1, 1)
        lyt.addWidget(self.mt_list, 2, 0, 1, 5)
        lyt.addWidget(self.submit_button, 3, 0, 1, 1)
        self.setLayout(lyt)

        self.populate_mtt_selector()
        self.mts = []

        self.setWindowModality(Qt.ApplicationModal)

        self.show()

    @staticmethod
    def check_date_edit(edit: QLineEdit, minimum: int, maximum: int):

        txt = edit.text()

        if not txt:
            return

        try:
            ymd = float(txt)
            if int(ymd) != ymd:
                raise ValueError
            elif ymd < minimum or ymd > maximum:
                raise ValueError

        except ValueError:
            edit.setText('')

    def populate_mtt_selector(self):

        self.type_combo.clear()

        names_list = [' ']
        try:
            mtt_names = self.SIII.SDBGUI.cnxn.get_all_mtt_names()
        except Exception as e:
            QMessageBox(parent=self.parent(), text=str(e)).exec_()
            return

        for name in mtt_names:
            names_list.append(name[0])

        self.type_combo.addItems(names_list)

    def set_remove_button_enabled(self, _):

        self.remove_button.setEnabled(True)

    def remove_mt(self):

        i = self.mt_list.currentIndex().row()
        self.mts.pop(i)

        self.mt_list.takeItem(i)
        if not self.mts:
            self.remove_button.setEnabled(False)
            self.set_submit_active()

    def add_mt(self):

        year = self.year_edit.text()
        month = self.month_edit.text()
        day = self.day_edit.text()

        if not year or not month or not day:
            date = 'NULL'
        else:
            try:
                date = datetime.date(int(year), int(month), int(day))
            except Exception as e:
                QMessageBox(parent=self, text=str(e)).exec_()
                return

        mtt = self.type_combo.currentText()
        mtt_id = self.type_combo.currentIndex()
        if not mtt_id:
            return

        val = self.value_edit.text()
        if not val:
            if mtt_id in [2, 3]:
                return
            val = 'NULL'
        else:
            val = float(val)

        if date == 'NULL':
            mt = (mtt_id, mtt, val, 'NULL')
        else:
            mt = (mtt_id, mtt, val, month + '/' + day + '/' + year)

        self.mts.append(mt)
        self.mt_list.addItem('{}, val = {}, date = {}'.format(mt[1], mt[2], date))
        self.set_submit_active()

    def set_value_edit_active(self, i: int):

        if i in [2, 3]:
            self.value_edit.setEnabled(True)

        else:
            self.value_edit.setText('')
            self.value_edit.setEnabled(False)

    def set_submit_active(self):

        if self.mts:
            self.submit_button.setEnabled(True)
        else:
            self.submit_button.setEnabled(False)

    def submit_mts(self):

        is_stock = True
        sd_id = self.inv_item[0]
        if self.inv_item[2] is not None:
            is_stock = False
            sd_id = self.inv_item[2]

        self.SIII.run_login_with_functions(lambda: self.submit_mts_func(is_stock=is_stock, sd_id=sd_id), None)

    def submit_mts_func(self, is_stock: bool, sd_id: int):

        for mt in self.mts:
            mtt_id = mt[0]
            val = mt[2]
            date = mt[3]
            if not self.SIII.is_blend:
                self.SIII.SDBGUI.cnxn.exec_add_measurement_or_treatment(is_stock=is_stock, mtt_id=mtt_id,
                                                                        sd_id=sd_id, val=val, mt_date=date)
            else:
                self.SIII.SDBGUI.cnxn.exec_add_blend_measurement_or_treatment(is_stock=is_stock, mtt_id=mtt_id,
                                                                              sd_id=sd_id, val=val, mt_date=date)
        self.SIII.populate_mts_list(self.SIII.inv_item)
        self.close()

    def closeEvent(self, _):

        try:
            self.parent().mt_dlg = None
        except Exception as e:
            print(e)


class AddStockGUI(QDialog):

    def __init__(self, parent: SurfactantDBGUI):
        super(AddStockGUI, self).__init__(parent=parent)
        self.SDBGUI = parent
        i = parent.surfactant_list.currentIndex().row()
        self.i = i
        self.s_id = parent.surfactants[i][0]

        self.setWindowTitle('Add Stock')
        self.sf = parent.sf
        self.setFixedSize(int(self.sf * 300), int(self.sf * 400))

        self.rooms = list()
        self.locations = list()

        lyt = QGridLayout()
        self.setLayout(lyt)

        s_label = QLabel(parent=self, text='Surfactant:')
        s_edit = QLineEdit(parent=self)
        s_edit.setText(self.SDBGUI.surfactants[i][1])
        s_edit.setEnabled(False)

        man_label = QLabel(parent=self, text='Manufacturer:')
        man_edit = QLineEdit(parent=self)
        man_edit.setText(self.SDBGUI.surfactants[i][2])
        man_edit.setEnabled(False)

        lot_label = QLabel(parent=self, text='Lot #:')
        self.lot_edit = QLineEdit(parent=self)
        self.lot_edit.textChanged.connect(lambda: self.edit_text_changed(self.lot_edit))
        self.lot_edit.editingFinished.connect(self.vet_lot)
        self.lot_edit.setStyleSheet('QLineEdit{background: red};')

        act_label = QLabel(parent=self, text='Act. %:')
        self.act_edit = QLineEdit(parent=self)
        self.act_edit.editingFinished.connect(self.vet_act)
        self.act_edit.textChanged.connect(lambda: self.edit_text_changed(self.act_edit))
        self.act_edit.setStyleSheet('QLineEdit{background: red};')

        conv_label = QLabel(parent=self, text='Conv. %:')
        self.conv_edit = QLineEdit(parent=self)
        self.conv_edit.textChanged.connect(lambda: self.edit_text_changed(self.conv_edit))
        self.conv_edit.editingFinished.connect(self.vet_conv)

        syn_label = QLabel(parent=self, text='Syn. Date (MM/DD/YYYY):')
        self.syn_edit = QLineEdit(parent=self)
        self.syn_edit.textChanged.connect(lambda: self.edit_text_changed(self.syn_edit))
        self.syn_edit.editingFinished.connect(lambda: self.vet_date(self.syn_edit))

        rec_label = QLabel(parent=self, text='Rec. Date (MM/DD/YYYY):')
        self.rec_edit = QLineEdit(parent=self)
        self.rec_edit.textChanged.connect(lambda: self.edit_text_changed(self.rec_edit))
        self.rec_edit.editingFinished.connect(lambda: self.vet_date(self.rec_edit))

        qty_label = QLabel(parent=self, text='Quantity [mL]:')
        self.qty_edit = QLineEdit(parent=self)
        self.qty_edit.textChanged.connect(lambda: self.edit_text_changed(self.qty_edit))
        self.qty_edit.editingFinished.connect(self.vet_qty)
        self.qty_edit.setStyleSheet('QLineEdit{background: red};')

        room_label = QLabel(parent=self, text='Room:')
        self.room_combo = QComboBox(parent=self)
        self.initialize_room_combo()
        self.room_combo.currentIndexChanged.connect(self.initialize_location_combo)
        self.room_combo.setStyleSheet('QComboBox{background: red};')

        loc_label = QLabel(parent=self, text='Location:')
        self.loc_combo = QComboBox(parent=self)
        # self.initialize_location_combo()
        self.loc_combo.currentIndexChanged.connect(self.vet_loc)
        self.loc_combo.setStyleSheet('QComboBox{background: red};')

        notes_label = QLabel(parent=self, text='Notes:')
        self.notes_textedit = QTextEdit(parent=self)

        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.setEnabled(False)
        self.submit_button.clicked.connect(self.submit_clicked)

        lyt.addWidget(s_label, 0, 0, 1, 1)
        lyt.addWidget(s_edit, 0, 1, 1, 1)

        lyt.addWidget(man_label, 1, 0, 1, 1)
        lyt.addWidget(man_edit, 1, 1, 1, 1)

        lyt.addWidget(lot_label, 2, 0, 1, 1)
        lyt.addWidget(self.lot_edit, 2, 1, 1, 1)

        lyt.addWidget(act_label, 3, 0, 1, 1)
        lyt.addWidget(self.act_edit, 3, 1, 1, 1)

        lyt.addWidget(conv_label, 4, 0, 1, 1)
        lyt.addWidget(self.conv_edit, 4, 1, 1, 1)

        lyt.addWidget(syn_label, 5, 0, 1, 1)
        lyt.addWidget(self.syn_edit, 5, 1, 1, 1)

        lyt.addWidget(rec_label, 6, 0, 1, 1)
        lyt.addWidget(self.rec_edit, 6, 1, 1, 1)

        lyt.addWidget(qty_label, 7, 0, 1, 1)
        lyt.addWidget(self.qty_edit, 7, 1, 1, 1)

        lyt.addWidget(room_label, 8, 0, 1, 1)
        lyt.addWidget(self.room_combo, 8, 1, 1, 1)

        lyt.addWidget(loc_label, 9, 0, 1, 1)
        lyt.addWidget(self.loc_combo, 9, 1, 1, 1)

        lyt.addWidget(notes_label, 10, 0, 1, 1)
        lyt.addWidget(self.notes_textedit, 11, 0, 1, 2)

        lyt.addWidget(self.submit_button, 12, 0, 1, 2)

        self.setWindowModality(Qt.ApplicationModal)
        self.show()

        self.rec_label = rec_label
        self.syn_label = syn_label

    def initialize_room_combo(self):

        rooms = [' ']
        result = self.SDBGUI.cnxn.exec_get_rooms()
        self.rooms = result

        for room in result:
            rooms.append(room[1])

        self.room_combo.clear()
        self.room_combo.addItems(rooms)

    def initialize_location_combo(self, ind: int):

        self.loc_combo.clear()
        if not ind:
            self.room_combo.setStyleSheet('QComboBox{background: red};')
            self.loc_combo.setStyleSheet('QComboBox{background: red};')
            return

        self.room_combo.setStyleSheet('QComboBox{background: white};')

        room_id = self.rooms[ind - 1][0]

        locations = [' ']
        result = self.SDBGUI.cnxn.exec_get_rm_locations(room_id=room_id)
        self.locations = result

        for loc in result:
            locations.append(loc[2])

        self.loc_combo.addItems(locations)

    @staticmethod
    def edit_text_changed(edit: QLineEdit):

        edit.setStyleSheet('QLineEdit{background: yellow};')

    def vet_lot(self):

        if self.lot_edit.text():
            self.lot_edit.setStyleSheet('QLineEdit{background: white};')

        else:
            self.lot_edit.setStyleSheet('QLineEdit{background: red};')

        self.check_submit_enabled()

    def vet_act(self):

        txt = self.act_edit.text()

        try:
            act = float(txt)
            if act < 0. or act > 100:
                raise ValueError
            act = round(act, 1)
            self.act_edit.setText(str(act))
            self.act_edit.setStyleSheet('QLineEdit{background: white};')

        except ValueError:
            self.act_edit.setText('')
            self.act_edit.setStyleSheet('QLineEdit{background: red};')

        finally:
            self.check_submit_enabled()

    def vet_conv(self):

        txt = self.conv_edit.text()

        try:
            conv = float(txt)
            conv = round(conv, 1)
            if conv < 0.:
                raise ValueError
            self.conv_edit.setText(str(conv))

        except ValueError:
            self.conv_edit.setText('')

        finally:
            self.conv_edit.setStyleSheet('QLineEdit{background: white};')

    def vet_qty(self):

        txt = self.qty_edit.text()

        try:
            qty = float(txt)
            if qty != int(qty) or qty < 0:
                raise ValueError
            self.qty_edit.setStyleSheet('QLineEdit{background: white};')

        except ValueError:
            self.qty_edit.setText('')
            self.qty_edit.setStyleSheet('QLineEdit{background: red};')

        finally:
            self.check_submit_enabled()

    @staticmethod
    def vet_date(edit: QLineEdit):

        txt = edit.text().strip().split('/')

        if len(txt) == 1 and len(txt[0]) == 8:
            old_txt = txt[0]
            txt = list()
            txt.append(old_txt[:2])
            txt.append(old_txt[2:4])
            txt.append(old_txt[4:])
            print(txt)
            edit.blockSignals(True)
            try:
                edit.setText('{:02d}/{:02d}/{:4d}'.format(int(txt[0]), int(txt[1]), int(txt[2])))
            except Exception as e:
                print(e)
            edit.blockSignals(False)

        if len(txt) != 3:
            edit.setText('')
            return

        mm = txt[0]
        dd = txt[1]
        yyyy = txt[2]

        for part in [mm, dd, yyyy]:

            try:
                part = float(part)
                if part != int(part) or part <= 0:
                    raise ValueError

            except ValueError:
                edit.setText('')
                edit.setStyleSheet('QLineEdit{background: white};')
                return

        mm = int(mm)
        dd = int(dd)
        yyyy = int(yyyy)

        if mm > 12 or dd > 31 or yyyy < 1900 or yyyy > 2100:
            edit.setText('')

        edit.setStyleSheet('QLineEdit{background: white};')

    def vet_loc(self, i: int):

        if i:
            self.loc_combo.setStyleSheet('QComboBox{background: white};')
        else:
            self.loc_combo.setStyleSheet('QComboBox{background: red};')

        self.check_submit_enabled(i)

    def check_submit_enabled(self, *args):

        if args:
            loc = args[0]
        else:
            loc = self.loc_combo.currentIndex()

        if self.act_edit.text() and self.lot_edit.text() and self.qty_edit.text() and \
                loc:

            self.submit_button.setEnabled(True)

        else:
            self.submit_button.setEnabled(False)

    def submit_clicked(self):

        self.SDBGUI.db_gui.run_login_with_functions(self.submit_stock)

    def submit_stock(self):

        s_id = self.s_id
        lot_num = self.lot_edit.text()
        act = float(self.act_edit.text())
        qty = int(self.qty_edit.text())
        loc_id = self.loc_combo.currentIndex()
        loc_id = self.locations[loc_id - 1][0]
        notes = self.notes_textedit.toPlainText()

        conv = self.conv_edit.text()
        if conv:
            conv = float(conv)
        else:
            conv = 'NULL'

        syn_date = self.syn_edit.text()
        if not syn_date:
            syn_date = 'NULL'
        else:
            mmddyyyy = syn_date.split('/')
            syn_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        rec_date = self.rec_edit.text()
        if not rec_date:
            rec_date = 'NULL'
        else:
            mmddyyyy = rec_date.split('/')
            rec_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        data_str = 's_id = {}, lot_num = {}, act % = {:.1f}, conv % = {}, syn_date = {}, rec_date = {}, qty = {}'
        data_str += ', loc_id = {}'

        self.SDBGUI.cnxn.exec_submit_stock(s_id=s_id, lot_num=lot_num, act_perc=act, conv_perc=conv, syn_date=syn_date,
                                           rec_date=rec_date, qty=qty, loc_id=loc_id, notes=notes)

        self.refresh_inventory_list_and_close()

    def refresh_inventory_list_and_close(self):

        item = self.SDBGUI.surfactant_list.item(self.i)
        self.SDBGUI.surfactant_list.itemClicked.emit(item)

        self.close()


class AddDilutionGUI(AddStockGUI):

    def __init__(self, parent: SurfactantDBGUI):
        super(AddDilutionGUI, self).__init__(parent=parent)
        self.setWindowTitle('Add Dilution')

        j = self.SDBGUI.inventory_list.currentIndex().row()
        self.stock = self.SDBGUI.inventories[j]

        self.lot_edit.setText(self.stock[1])
        self.lot_edit.setStyleSheet('QLineEdit{background: white};')
        self.lot_edit.setEnabled(False)
        self.conv_edit.setText(str(self.stock[6]))
        self.conv_edit.setStyleSheet('QLineEdit{background: white};')
        self.conv_edit.setEnabled(False)
        self.rec_edit.setVisible(False)
        self.rec_label.setVisible(False)
        self.syn_label.setText('Dilution Date (MM/DD/YYYY):')

    def submit_stock(self):
        # Actually submits dilution, but so-named to be compatible with inheritance from AddStockGUI.

        stock_id = self.stock[0]
        act_perc = float(self.act_edit.text())
        qty = int(self.qty_edit.text())
        loc_id = self.loc_combo.currentIndex()
        notes = self.notes_textedit.toPlainText()

        dil_date = self.syn_edit.text()
        if not dil_date:
            dil_date = 'NULL'
        else:
            mmddyyyy = dil_date.split('/')
            dil_date = mmddyyyy[2] + '/' + mmddyyyy[0] + '/' + mmddyyyy[1]

        self.SDBGUI.cnxn.exec_submit_dilution(stock_id=stock_id, act_perc=act_perc, qty=qty, date_made=dil_date,
                                              loc_id=loc_id, notes=notes)

        self.refresh_inventory_list_and_close()
