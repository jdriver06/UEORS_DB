
from sys import argv, exit
from PyQt5.Qt import QApplication, QIcon, QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QTextEdit
from os.path import isdir, isfile
from os import listdir, getcwd, startfile, remove
import shutil
from time import sleep
import db_tools

__version__ = '1.1.0'


class UpdateWorker(QObject):

    started = pyqtSignal()
    finished = pyqtSignal()
    progress = pyqtSignal(int, float)

    def __init__(self, u_or_q: str, upgrade_path: list):
        super(UpdateWorker, self).__init__()
        self.upgrade_path = upgrade_path
        self.u_or_q = u_or_q

    def update_to_current(self):

        sleep(0.1)
        self.started.emit()

        path = self.u_or_q + ':\\UEORLAB1\\Python Files\\UEORS_DB_GUI\\'
        full_upgrade_path = [path + 'UEORS_DB_GUI_v' + up.replace('.', '-') for up in self.upgrade_path]
        cwd = getcwd()
        current_files_and_directories = listdir(cwd)

        for i, fup in enumerate(full_upgrade_path):
            all_files_and_directories = listdir(fup)
            l = len(all_files_and_directories)
            for j, f_or_d in enumerate(all_files_and_directories):
                self.progress.emit(i + 1, j / l)
                if f_or_d not in current_files_and_directories:
                    sleep(0.01)
                    if isfile(fup + '\\' + f_or_d) and not isfile(cwd + '\\' + f_or_d):
                        shutil.copy2(fup + '\\' + f_or_d, cwd)
                    elif isdir(fup + '\\' + f_or_d) and not isdir(cwd + '\\' + f_or_d):
                        shutil.copytree(fup + '\\' + f_or_d, cwd + '\\' + f_or_d)

        sleep(0.1)
        self.finished.emit()


class UEORS_DB_GUI_Launcher(QMainWindow):

    def __init__(self, cnxn: db_tools.pyodbc.Connection):
        super(UEORS_DB_GUI_Launcher, self).__init__()
        self.cnxn = cnxn
        self.setFixedSize(550, 150)
        self.setWindowTitle('UEORS_DB_GUI Launcher')
        self.setWindowIcon(QIcon('UEORS_logo_DB.jpg'))

        self.upgrade_widget = QWidget()
        lyt = QGridLayout()
        self.upgrade_widget.setLayout(lyt)
        self.upgrade_label = QLabel(parent=self.upgrade_widget, text='Software up-to-date.')
        font = self.upgrade_label.font()
        font.setPointSize(11)
        self.upgrade_label.setFont(font)
        self.upgrade_button = QPushButton(parent=self.upgrade_widget, text='Update')
        self.upgrade_button.setFont(font)
        self.upgrade_button.clicked.connect(self.update_clicked)
        self.upgrade_button.setEnabled(False)
        self.upgrade_button.setFixedWidth(100)
        self.launch_button = QPushButton(parent=self.upgrade_widget, text='Launch')
        self.launch_button.setFont(font)
        self.launch_button.clicked.connect(self.launch)
        self.launch_button.setEnabled(False)
        self.launch_button.setFixedWidth(100)

        self.upgrade_text = QTextEdit(parent=self)
        self.upgrade_text.setEnabled(False)

        self.upgrade_widget.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self.upgrade_label, 0, 0, 1, 1)
        lyt.addWidget(self.upgrade_button, 0, 1, 1, 1)
        lyt.addWidget(self.launch_button, 0, 2, 1, 1)
        lyt.addWidget(self.upgrade_text, 1, 0, 1, 3)

        self.setCentralWidget(self.upgrade_widget)

        self.u_or_q = 'U'
        if not isdir('U:\\'):
            self.u_or_q = 'Q'

        self.upgrade_path = []
        self.file = ''
        self.worker = None
        self.t = None

    def check_most_recent_exe(self) -> tuple:

        if not self.file:
            return ()

        ver = self.file.split('v')[-1].split('.exe')[0].split('-')

        DBO = db_tools.DBObjects
        result = db_tools.execute_stored_procedure_with_params(self.cnxn, DBO.Procedures.CheckUpdateAvailable.value,
                                                               {DBO.Params.v1.value: ver[0],
                                                                DBO.Params.v2.value: ver[1],
                                                                DBO.Params.v3.value: ver[2]}).fetchall()[0]

        return result

    def find_most_recent_exe(self):

        my_dir = getcwd()
        results = listdir(my_dir)
        exe = ''

        for result in results:

            if result.find('UEORS_DB_GUI_v') == -1 or result.find('.manifest') != -1:
                continue

            if isfile(my_dir + '\\' + result) and result > exe:
                exe = result

        self.file = my_dir + '\\' + exe

        new_exe = self.check_most_recent_exe()

        if new_exe[0] is not None:
            upgrade_path = self.check_for_update(exe)
            self.upgrade_path = upgrade_path
            # last_version = upgrade_path[-1].split('v')[-1]
            self.upgrade_label.setText('Software needs updating to version {}.{}.{}.'.format(*new_exe))
            self.upgrade_label.setStyleSheet('QLabel {color: red};')
            self.upgrade_button.setEnabled(True)
            DBO = db_tools.DBObjects
            info = db_tools.execute_stored_procedure_with_params(self.cnxn, DBO.Procedures.GetVerNotes.value,
                                                                 {DBO.Params.v1.value: new_exe[0],
                                                                  DBO.Params.v2.value: new_exe[1],
                                                                  DBO.Params.v3.value: new_exe[2]}).fetchall()[0]
            # print(new_exe, info)

            required = 'Yes'
            if not info[1]:
                required = 'No'
                self.launch_button.setEnabled(True)

            self.upgrade_text.setText('Required? {}.\n\nVersion notes: {}'.format(required, info[0]))

        else:
            self.launch_button.setEnabled(True)

    def remove_previous_exes(self):

        my_dir = getcwd()
        results = listdir(my_dir)
        exe = self.file.split('\\')[-1].split('.')[0]
        print(exe)

        for result in results:

            if result.find('UEORS_DB_GUI_v') > -1 and result.find(exe) == -1:
                print('Need to delete {}.'.format(result))
                remove(my_dir + '\\' + result)

    def check_for_update(self, exe) -> list:

        v = exe.split('v')[-1]
        v = v.split('.')[0]
        v = v.replace('-', '.')

        path = self.u_or_q + ':\\UEORLAB1\\Python Files\\UEORS_DB_GUI\\'
        directories = [f for f in listdir(path) if not isfile(path + f)]

        latest_version = ''
        upgrade_path = []

        for d in directories:
            version = d.split('v')[-1]
            version = version.replace('-', '.')

            if version > latest_version and d.find('UEORS_DB_GUI_v') != -1:
                latest_version = version
                if version > v:
                    upgrade_path.append(version)

        return upgrade_path

    def update_clicked(self):

        self.worker = UpdateWorker(self.u_or_q, self.upgrade_path)
        self.t = QThread()
        self.worker.moveToThread(self.t)
        self.t.started.connect(self.worker.update_to_current)
        self.worker.finished.connect(self.t.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.update_done)
        self.worker.progress.connect(self.update_progress)
        self.worker.started.connect(self.update_started)
        self.t.finished.connect(self.t.deleteLater)
        self.t.start(priority=QThread.LowPriority)

    def update_started(self):

        self.upgrade_button.setEnabled(False)
        self.upgrade_label.setText('Software updating. Do not close.')

    def update_progress(self, i: int, p: float):

        self.upgrade_label.setText('Update progress: {} of {}, {:.1f}%'.format(i, len(self.upgrade_path), 100. * p))

    def update_done(self):

        self.find_most_recent_exe()
        self.upgrade_label.setText('Removing previous exe files.')
        self.remove_previous_exes()
        self.upgrade_label.setText('Software ready to launch.')
        self.upgrade_label.setStyleSheet('QLabel {color: black};')
        self.launch_button.setEnabled(True)
        self.upgrade_button.setEnabled(False)

    def launch(self):

        self.find_most_recent_exe()
        startfile(self.file)
        self.close()

    def close(self):
        self.cnxn.close()
        super(UEORS_DB_GUI_Launcher, self).close()


def main():

    server = 'UEORS-DB\\'
    database = 'UEORS_MAIN_DB'
    username = 'ueors_user'
    password = 'ueor101'

    try:
        cnxn = db_tools.connect_to_database(server, database, username, password)
    except Exception as e:
        print('error with cnxn.')
        print(e)
        return

    try:
        app = QApplication(argv)
        app.setStyle('fusion')
        launcher = UEORS_DB_GUI_Launcher(cnxn=cnxn)
        launcher.show()
        launcher.find_most_recent_exe()
        exit(app.exec_())
    except Exception as e:
        print('error with launcher init.')
        print(e)
        return


if __name__ == '__main__':
    main()
