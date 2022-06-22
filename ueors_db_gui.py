
from sys import argv, exit
from PyQt5.Qt import QApplication, QIcon, QThread, QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QTabWidget, QWidget, QMessageBox, QLabel, QDialog, QTextEdit, \
    QPushButton, QGridLayout, QHBoxLayout, QListWidget, QCheckBox, QComboBox
import surfactant_database
import brine_database
import OSHA_database
import polymer_database
import db_tools
from os.path import isdir
from os import startfile, getcwd
from time import sleep

__version__ = '0.6.6'


class TimerWorker(QObject):

    started = pyqtSignal()
    times_up = pyqtSignal()
    finished = pyqtSignal()

    max_recursion = 100

    def __init__(self, total_sec: int):
        super(TimerWorker, self).__init__()
        self.re_start = False
        self.auto_restart = False
        self.total_sec = total_sec
        self.recursion_depth = 0

    def start_timer(self):

        self.started.emit()
        self.start_timer_func()

    def start_timer_func(self):

        for i in range(self.total_sec):
            sleep(1)
            print('Elapsed Time: {}s'.format(i + 1))
            if self.re_start:
                break
            if i == self.total_sec - 1:
                self.times_up.emit()
                if self.auto_restart:
                    self.re_start = True
                else:
                    self.finished.emit()

        if self.recursion_depth >= TimerWorker.max_recursion - 1:
            self.finished.emit()
            return

        if self.re_start:
            self.re_start = False
            self.recursion_depth += 1
            self.start_timer_func()


class ClickableLabel(QLabel):

    clicked = pyqtSignal()

    def __init__(self, parent, text: str):
        super(ClickableLabel, self).__init__(parent=parent, text=text)
        self.active = False

    def mousePressEvent(self, ev):
        super(ClickableLabel, self).mousePressEvent(ev)
        if self.active:
            print('Label clicked!')
            self.clicked.emit()


class UEORS_DB_GUI(QMainWindow):

    server = 'UEORS-DB\\'
    database = 'UEORS_MAIN_DB'
    default_user = 'ueors_user'
    default_password = 'ueor101'

    login_success = pyqtSignal()
    login_failed = pyqtSignal()

    def __init__(self, cnxn):
        super(UEORS_DB_GUI, self).__init__()
        self.setWindowTitle('UEORS Inventory Client v{}'.format(__version__))
        self.setWindowIcon(QIcon('UEORS_logo_DB.jpg'))
        self.sf = 1.
        self.setFixedSize(int(self.sf * 800), int(self.sf * 725))
        self.cnxn = cnxn

        self.u_or_q = 'U'
        if not isdir('U:\\'):
            self.u_or_q = 'Q'

        lyt = QGridLayout()

        self.update_text = ClickableLabel(parent=self, text='This app is up to date.')
        # self.update_text.setAlignment(Qt.AlignRight)
        lyt.addWidget(self.update_text, 0, 0, 1, 1)

        btn_widget = QWidget()
        btn_lyt = QHBoxLayout()
        btn_widget.setLayout(btn_lyt)
        lyt.addWidget(btn_widget, 0, 1, 1, 1)
        btn_lyt.setContentsMargins(0, 0, 0, 0)

        self.request_button = QPushButton(parent=self, text='General Request')
        # self.request_button.setFixedWidth(int(self.sf * 150))
        self.request_button.clicked.connect(self.general_request_clicked)
        btn_lyt.addWidget(self.request_button)

        self.view_requests_button = QPushButton(parent=self, text='View Requests')
        # self.view_requests_button.setFixedWidth(int(self.sf * 150))
        self.view_requests_button.clicked.connect(self.view_general_requests_clicked)
        btn_lyt.addWidget(self.view_requests_button)

        self.main_widget = QTabWidget(parent=self)
        self.osha_db = OSHA_database.OSHADBGUI(cnxn=cnxn, linked_main_window=self)
        self.surf_db = surfactant_database.SurfactantDBGUI(cnxn=cnxn, linked_main_window=self)
        self.brine_db = brine_database.BrineDatabaseGUI(cnxn=cnxn, linked_main_window=self)
        self.polymer_db = polymer_database.PolymerDBGUI(cnxn=cnxn, linked_main_window=self)
        self.main_widget.addTab(self.osha_db, 'OSHA')
        self.main_widget.addTab(self.brine_db, 'Brine Compositions')
        font = self.surf_db.font()
        font.setPointSize(10)
        self.surf_db.setFont(font)
        self.brine_db.setFont(font)
        self.main_widget.addTab(self.polymer_db, 'Polymers')
        self.main_widget.addTab(self.surf_db, 'Surfactants')
        self.main_widget.addTab(QWidget(), 'Reservoir Materials')
        self.main_widget.setCurrentIndex(0)
        # self.main_widget.setTabEnabled(0, False)
        # self.main_widget.setTabEnabled(1, False)
        # self.main_widget.setTabEnabled(2, False)
        self.main_widget.setTabEnabled(4, False)

        widget = QWidget()
        widget.setLayout(lyt)

        lyt.addWidget(self.main_widget, 1, 0, 1, 2)
        self.setCentralWidget(widget)

        self.privileged_user = ''
        self.current_user = self.default_user
        self.login_dialog = None
        self.view_general_requests_dlg = None

        self.current_active_requests = list()
        self.live_updates = False

        self.login_timer = None
        self.login_thread = None
        self.reset_login_timer()

        self.inventory_notification_timer = None
        self.inventory_notification_thread = None
        self.reset_inventory_notification_timer()
        self.inventory_notification_thread.start()

        self.show()

    def set_connection(self, cnxn: db_tools.pyodbc.Connection):

        self.cnxn = cnxn
        self.surf_db.set_connection(cnxn)
        self.brine_db.set_connection(cnxn)
        self.osha_db.set_connection(cnxn)
        self.polymer_db.set_connection(cnxn)

    def reset_login_timer(self):

        self.login_timer = TimerWorker(60)
        # self.login_timer.finished.connect(lambda: print('Timer done!'))
        self.login_timer.finished.connect(self.login_default)
        self.login_thread = QThread()
        self.login_timer.moveToThread(self.login_thread)
        self.login_thread.started.connect(self.login_timer.start_timer)
        self.login_timer.finished.connect(self.login_thread.quit)
        self.login_timer.finished.connect(self.login_timer.deleteLater)
        self.login_thread.finished.connect(self.login_thread.deleteLater)
        self.login_thread.finished.connect(self.reset_login_timer)

    def reset_inventory_notification_timer(self):

        self.inventory_notification_timer = TimerWorker(60)
        self.inventory_notification_timer.auto_restart = True
        self.inventory_notification_timer.times_up.connect(self.osha_db.check_active_orders)
        self.inventory_notification_timer.times_up.connect(self.check_for_update)
        self.inventory_notification_timer.times_up.connect(self.check_for_new_active_requests)
        # self.inventory_notification_timer.finished.connect(self.login_default)
        self.inventory_notification_thread = QThread()
        self.inventory_notification_timer.moveToThread(self.inventory_notification_thread)
        self.inventory_notification_thread.started.connect(self.inventory_notification_timer.start_timer)
        self.inventory_notification_timer.finished.connect(self.inventory_notification_thread.quit)
        self.inventory_notification_timer.finished.connect(self.inventory_notification_timer.deleteLater)
        self.inventory_notification_thread.finished.connect(self.inventory_notification_thread.deleteLater)

        self.inventory_notification_timer.finished.connect(self.reset_and_restart_inventory_notification_timer)

    def reset_and_restart_inventory_notification_timer(self):

        self.reset_inventory_notification_timer()
        self.inventory_notification_thread.start()

    def check_for_update(self):

        dummy = __version__.split('.')
        my_ver = list()
        for part in dummy:
            my_ver.append(int(part))

        results = db_tools.execute_stored_procedure_with_params(self.cnxn, 'dbo.is_newer_db_gui_version_available',
                                                                {'v1': my_ver[0], 'v2': my_ver[1], 'v3': my_ver[2]})

        results = results.fetchall()[0]
        if results[0] is not None:
            self.update_text.setText('A newer version of this app ({}.{}.{}) is available. Click here to update.'
                                     .format(*results))
            self.update_text.setStyleSheet('QLabel{color: red}')
            font = self.update_text.font()
            font.setBold(True)
            self.update_text.setFont(font)
            self.update_text.active = True
            self.update_text.clicked.connect(self.launch_update_tool)

    def check_for_new_active_requests(self):

        DBO = db_tools.DBObjects
        results = db_tools.execute_stored_procedure_with_params(self.cnxn, DBO.Procedures.GetActiveGeneralReq.value,
                                                                {}).fetchall()

        for result in results:
            if result not in self.current_active_requests and self.view_general_requests_dlg is None and \
                    self.live_updates:
                self.view_general_requests_clicked()

        self.current_active_requests = results

    def launch_update_tool(self):

        try:
            startfile(getcwd() + '\\' + 'UEORS_DB_GUI.exe')
            self.close()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def general_request_clicked(self):

        GeneralRequestDialog(parent=self).exec_()

    def view_general_requests_clicked(self):

        if self.view_general_requests_dlg is not None:
            return

        dlg = ViewGeneralRequestsDialog(parent=self)
        self.view_general_requests_dlg = dlg
        self.inventory_notification_timer.times_up.connect(dlg.load_requests)
        dlg.show()

    def link_login_dialog(self, dlg: db_tools.LoginDialog):

        self.login_dialog = dlg
        dlg.name_edit.setText(self.privileged_user)
        if self.privileged_user:
            dlg.pass_edit.setFocus()
        dlg.login_signal.connect(self.login)
        self.login_success.connect(dlg.close)
        self.login_failed.connect(dlg.pass_edit.clear)
        dlg.close_signal.connect(self.unlink_login_dialog)

    def unlink_login_dialog(self):

        self.login_dialog = None

    def login_default(self):

        self.login(username=self.default_user, password=self.default_password)

    def login(self, username: str, password: str):

        if self.cnxn is not None:
            self.cnxn.cursor().commit()
            self.cnxn.close()
            self.cnxn = None
            self.surf_db.cnxn = None
            self.brine_db.cnxn = None
            self.osha_db.cnxn = None
            self.polymer_db.cnxn = None

        try:
            cnxn = db_tools.connect_to_database(self.server, self.database, username, password)
            self.set_connection(cnxn)
            self.current_user = username

            if not self.current_user_is_default():
                self.privileged_user = username
                self.login_thread.start(priority=QThread.LowPriority)

            if self.current_user == username:
                self.login_success.emit()

        except db_tools.pyodbc.Error:
            QMessageBox(parent=self, text='Username or password is incorrect.').exec_()
            self.login_failed.emit()

    def run_login_with_functions(self, func, func_finally=None):

        try:

            if not self.current_user_is_default() and self.login_thread.isRunning():

                self.login_timer.re_start = True
                func()

            elif self.login_dialog is None:

                dlg = db_tools.LoginDialog(parent=self)
                self.link_login_dialog(dlg)
                # dlg.pass_edit.setText('5k1a7n806UEORS')
                dlg.exec()

                if not self.current_user_is_default():

                    func()

            if self.cnxn is not None:
                self.cnxn.cursor().commit()

        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

        finally:

            if self.cnxn is None:
                self.login_default()

            if func_finally is not None:
                func_finally()

    def current_user_is_default(self) -> bool:

        if self.current_user != self.default_user:
            return False

        return True

    def closeEvent(self, _):

        self.cnxn.cursor().commit()
        if self.view_general_requests_dlg is not None:
            self.view_general_requests_dlg.close()
        self.cnxn.close()


class GeneralRequestDialog(QDialog):

    def __init__(self, parent: UEORS_DB_GUI):
        super(GeneralRequestDialog, self).__init__(parent=parent)
        sf = parent.sf
        self.setFixedSize(int(sf * 300), int(sf * 300))
        self.setWindowTitle('General Request Form')
        lyt = QVBoxLayout()
        self.setLayout(lyt)

        request_notes_label = QLabel(parent=self, text='Request:')
        self.request_notes = QTextEdit(parent=self)
        self.request_notes.textChanged.connect(self.notes_changed)
        urgency_label = QLabel(parent=self, text='Urgency:')
        self.urgency_combo = QComboBox(parent=self)
        self.urgency_combo.addItems([' ', 'Low', 'Normal', 'ASAP'])
        self.urgency_combo.currentIndexChanged.connect(self.urgency_selected)
        urgency_widget = QWidget(parent=self)
        u_lyt = QHBoxLayout()
        urgency_widget.setLayout(u_lyt)
        u_lyt.addWidget(urgency_label)
        u_lyt.addWidget(self.urgency_combo)
        self.submit_button = QPushButton(parent=self, text='Submit')
        self.submit_button.clicked.connect(self.submit_button_clicked)
        self.submit_button.setEnabled(False)

        lyt.addWidget(request_notes_label)
        lyt.addWidget(self.request_notes)
        lyt.addWidget(urgency_widget)
        lyt.addWidget(self.submit_button)

    def submit_button_clicked(self):

        self.parent().run_login_with_functions(self.submit_text, self.close)

    def notes_changed(self):

        if not self.request_notes.toPlainText():
            self.submit_button.setEnabled(False)
            return

        self.check_submit_enable(True)

    def urgency_selected(self, i: int):

        if not i:
            self.submit_button.setEnabled(False)
            return

        self.check_submit_enable(False)

    def check_submit_enable(self, flag: bool):

        enable_submit = True

        if flag:
            i = self.urgency_combo.currentIndex()
            if not i:
                enable_submit = False
        else:
            if not self.request_notes.toPlainText():
                enable_submit = False

        self.submit_button.setEnabled(enable_submit)

    def submit_text(self):

        txt = self.request_notes.toPlainText()
        u_id = self.urgency_combo.currentIndex()
        db_tools.execute_stored_procedure_with_params(self.parent().cnxn,
                                                      db_tools.DBObjects.Procedures.SubmitGeneralRequest.value,
                                                      {db_tools.DBObjects.Params.RequestNotes.value: txt,
                                                       db_tools.DBObjects.Params.UrgencyID.value: u_id})


class ViewGeneralRequestsDialog(QDialog):

    def __init__(self, parent: UEORS_DB_GUI):
        super(ViewGeneralRequestsDialog, self).__init__(parent=parent)
        sf = parent.sf
        self.setFixedSize(int(sf * 700), int(sf * 300))
        self.setWindowTitle('General Requests')
        lyt = QGridLayout()
        self.setLayout(lyt)

        self.live_updates_checkbox = QCheckBox(parent=self)
        self.live_updates_checkbox.setText('Live Updates?')
        self.live_updates_checkbox.setChecked(parent.live_updates)
        self.live_updates_checkbox.clicked.connect(self.toggle_live_update)

        active_requests_label = QLabel(parent=self, text='Active Requests:')
        self.active_requests_list = QListWidget(parent=self)
        self.active_requests_list.itemClicked.connect(self.load_active_request_notes)
        self.active_requests_notes = QTextEdit(parent=self)
        self.active_requests_notes.setReadOnly(True)
        self.resolve_notes = QTextEdit(parent=self)
        self.resolve_button = QPushButton(parent=self, text='Resolve')
        self.resolve_button.clicked.connect(self.resolve_button_clicked)

        inactive_requests_label = QLabel(parent=self, text='Inactive Requests:')
        self.inactive_requests_list = QListWidget(parent=self)
        self.inactive_requests_list.itemClicked.connect(self.load_inactive_request_notes)
        self.inactive_requests_notes = QTextEdit(parent=self)
        self.inactive_requests_notes.setReadOnly(True)
        self.inactive_resolve_notes = QTextEdit(parent=self)
        self.inactive_resolve_notes.setReadOnly(True)

        lyt.addWidget(self.live_updates_checkbox, 0, 0, 1, 1)

        lyt.addWidget(active_requests_label, 1, 0, 1, 1)
        lyt.addWidget(self.active_requests_list, 2, 0, 1, 1)
        lyt.addWidget(self.active_requests_notes, 2, 1, 1, 1)
        lyt.addWidget(self.resolve_notes, 2, 2, 1, 1)
        lyt.addWidget(self.resolve_button, 3, 2, 1, 1)

        lyt.addWidget(inactive_requests_label, 3, 0, 1, 1)
        lyt.addWidget(self.inactive_requests_list, 4, 0, 1, 1)
        lyt.addWidget(self.inactive_requests_notes, 4, 1, 1, 1)
        lyt.addWidget(self.inactive_resolve_notes, 4, 2, 1, 1)

        self.active_requests = []
        self.inactive_requests = []

        try:
            self.load_requests()
        except Exception as e:
            QMessageBox(parent=self, text=str(e)).exec_()

    def toggle_live_update(self):

        checked = self.live_updates_checkbox.checkState()
        self.parent().live_updates = checked

    def load_requests(self, clear_resolve: bool=False):

        self.resolve_button.setEnabled(False)

        self.active_requests_list.clear()
        self.inactive_requests_list.clear()
        self.active_requests_notes.clear()
        self.inactive_requests_notes.clear()
        self.inactive_resolve_notes.clear()

        if clear_resolve:
            self.resolve_notes.clear()

        DBO = db_tools.DBObjects

        requests = db_tools.execute_stored_procedure_with_params(self.parent().cnxn,
                                                                 DBO.Procedures.GetActiveGeneralReq.value, {})
        active_requests = requests.fetchall()
        self.active_requests = active_requests

        active_requests_list = list()

        for request in active_requests:
            active_requests_list.append('{}, Urgency: {}, Requestor: {}'.format(request[1], request[6], request[2]))

        if active_requests_list:
            self.active_requests_list.addItems(active_requests_list)

        requests = db_tools.execute_stored_procedure_with_params(self.parent().cnxn,
                                                                 DBO.Procedures.GetInactiveGeneralReq.value, {})
        inactive_requests = requests.fetchall()
        self.inactive_requests = inactive_requests

        inactive_requests_list = list()

        for request in inactive_requests:
            inactive_requests_list.append('{}, Requestor: {}, Resolver: {}'.format(request[1], request[2], request[4]))

        if inactive_requests_list:
            self.inactive_requests_list.addItems(inactive_requests_list)

    def load_active_request_notes(self, _):

        i = self.active_requests_list.currentIndex().row()
        self.active_requests_notes.setText(self.active_requests[i][3])

        self.resolve_button.setEnabled(True)

    def load_inactive_request_notes(self, _):

        i = self.inactive_requests_list.currentIndex().row()
        self.inactive_requests_notes.setText(self.inactive_requests[i][3])
        self.inactive_resolve_notes.setText(self.inactive_requests[i][5])

    def resolve_button_clicked(self):

        self.parent().run_login_with_functions(self.resolve, lambda: self.load_requests(True))

    def resolve(self):

        DBO = db_tools.DBObjects
        i = self.active_requests_list.currentIndex().row()
        req_id = self.active_requests[i][0]
        resolve_notes = self.resolve_notes.toPlainText()
        db_tools.execute_stored_procedure_with_params(self.parent().cnxn, DBO.Procedures.SubmitReqResolution.value,
                                                      {DBO.Params.GenReqID.value: req_id,
                                                       DBO.Params.ResolveNotes.value: resolve_notes})

    def closeEvent(self, a0):
        try:
            self.parent().view_general_requests_dlg = None
        except Exception as e:
            print(e)
            
        super(ViewGeneralRequestsDialog, self).closeEvent(a0)


def main():

    server = 'UEORS-DB\\'
    database = 'UEORS_MAIN_DB'
    username = 'ueors_user'
    password = 'ueor101'

    app = QApplication(argv)
    app.setStyle('fusion')

    try:
        cnxn = db_tools.connect_to_database(server, database, username, password)
    except Exception as e:
        QMessageBox(text=str(e)).exec_()
        return

    gui = UEORS_DB_GUI(cnxn=cnxn)
    gui.show()
    exit(app.exec_())


if __name__ == '__main__':
    main()
