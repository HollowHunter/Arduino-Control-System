import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QFileDialog, QSlider, QMenu, QMenuBar, QLCDNumber
from PyQt5.QtWidgets import QPushButton, QLineEdit, QCheckBox, QRadioButton, QButtonGroup, QAction
from PyQt5.QtCore import Qt
from threading import Thread
import serial
import glob

# Разработцик - HollowHunter
# https://habr.com/ru/users/HollowHunter/
def serial_ports():
    # Функция со stackoverflow, автор - Thomas
    # https://stackoverflow.com/users/300783/thomas
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class Main_window(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 150, 700, 500)
        self.setWindowTitle('Контроллер сериал порта')

        self.obg_list = []  # список со всеми нодами
        speeds = ['1200', '2400', '4800', '9600', '19200', '38400', '57600', '115200']

        self.file_name = ''
        self.now_port = ''
        self.now_speed = 9600

        menu_line = QMenuBar(self)

        file = menu_line.addMenu("Файл")
        new = QAction('Новый', self)
        file.addAction(new)
        new.triggered.connect(self.new_progect)
        open = QAction("Открыть", self)
        file.addAction(open)
        open.triggered.connect(self.open_file)
        save = QAction("Сохранить", self)
        save.setShortcut("Ctrl+S")
        file.addAction(save)
        save.triggered.connect(self.save_file)
        save_us = QAction("Сохранить как", self)
        file.addAction(save_us)
        save_us.triggered.connect(self.clear_fname)
        save_us.triggered.connect(self.save_file)
        author = file.addMenu('Автор')
        for elem in ['Habr:\tHollowHunter', 'GitHub:\tHollowHunter', 'AlexGyver Community:\tHollowHunter']:
            a = QAction(elem, self)
            author.addAction(a)

        create = menu_line.addMenu('Создать')
        btn = QAction('Кнопка', self)
        create.addAction(btn)
        sld = QAction('Слайдер', self)
        create.addAction(sld)
        edt = QAction('Поле для ввода', self)
        create.addAction(edt)
        inp = QAction('Вход данных', self)
        create.addAction(inp)
        create.triggered[QAction].connect(self.spawn_new_node)

        ard = menu_line.addMenu('Подключение ардуино')
        self.port = ard.addMenu('Порт:')
        self.port.triggered[QAction].connect(self.change_port)
        self.udate = QAction('Обновить порты', self)
        self.port.addAction(self.udate)
        self.display_port = QAction('Текущий порт: None', self)
        self.port.addAction(self.display_port)
        port_list = serial_ports()
        for i in serial_ports():
            edt = QAction(i, self)
            self.port.addAction(edt)
        if len(port_list) == 1:
            self.now_port = port_list[0]
            self.display_port.setText('Текущий порт: ' + port_list[0])
        speed = ard.addMenu('Скорость')
        self.speed_viewier = QAction('Текущая скорость: 9600', self)
        speed.addAction(self.speed_viewier)
        for elem in speeds:
            n = QAction(elem, self)
            speed.addAction(n)
        speed.triggered[QAction].connect(self.change_speed)
        self.connect_btn = QAction('Подключить', self)
        ard.addAction(self.connect_btn)
        self.connect_btn.triggered.connect(self.connect)
        dis = QAction('Отключить', self)
        ard.addAction(dis)
        dis.triggered.connect(self.disConnect)
        comand_type = ard.addMenu('Тип сигнала')
        self.type_viewier = QAction('Текущий сигнал: ${indx} {comand};')
        comand_type.addAction(self.type_viewier)

        self.read_ser = Thread(target=self.read_serial_port, daemon=True)
        self.read_ser.start()

    def read_serial_port(self):
        global ser
        while 1:
            try:
                string = ser.readline()
                if string != None:
                    for elem in self.obg_list:
                        if type(elem) == Input_serial_Node:
                            elem.displayValue(string.decode()[:-1])
            except Exception:
                pass

    def copy_node(self, parametrs):
        parametrs[3] = str(int(parametrs[3]) + 70)
        self.close()
        self.obg_list.append([Button_Node, Slider_Node, Edit_Node,
                              Input_serial_Node][int(parametrs[0])](self, parametrs))
        self.show()


    def mouseMoveEvent(self, event):
        global trigered_node
        if trigered_node != None and event.x() >= 0 and event.y() >= 0:
            trigered_node.ubdate_cord(event.x(), event.y())

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            for elem in self.obg_list:
               if elem.is_keyword():
                   elem.change_key_state(1, event.key())

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            for elem in self.obg_list:
               if elem.is_keyword():
                   elem.change_key_state(1, event.key(), True)

    def mouseReleaseEvent(self, event):
        global trigered_node
        trigered_node = None

    def open_file(self):
        print(serial_ports())
        fname = QFileDialog.getOpenFileName(self, 'Выбрать файл', '',
                                            'Arduino Node Save (*.ans);;Все файлы (*)')[0]
        print(fname)
        if fname != '':
            self.close()
            with open(fname, 'r', encoding='utf8') as f_r:
                save_file = f_r.read().split('\n')
                save_file = list(filter(lambda elem: elem != '', save_file))
                for i in range(len(self.obg_list)):
                    self.obg_list[i].del_widgets()
                self.obg_list.clear()
                for elem in save_file:
                    if elem[0] == '#':
                        continue
                    e = elem.split('$')
                    self.obg_list.append([Button_Node, Slider_Node, Edit_Node,
                                          Input_serial_Node][int(e[0])](self, e))
            self.file_name = fname
            self.show()

    def clear_fname(self):
        self.file_name = ''

    def save_file(self):
        if self.file_name == '':
            fname = QFileDialog.getSaveFileName(self, 'сохранение', '', 'Arduino Node Save (*.ans)')[0]
        else:
            fname = self.file_name
        self.obg_list = list(filter(lambda elem: elem.is_delete(), self.obg_list))
        if fname != '':
            with open(fname, 'w', encoding='utf8') as f_w:
                for elem in self.obg_list:
                    print('$'.join(elem.parametrs_return()), file=f_w)
            self.file_name = fname

    def new_progect(self):
        for i in range(len(self.obg_list)):
            self.obg_list[i].del_widgets()
        self.obg_list.clear()
        self.file_name = ''

    def spawn_new_node(self, event):
        self.close()
        if event.text() == 'Кнопка':
            self.obg_list.append(Button_Node(self))
        elif event.text() == 'Слайдер':
            self.obg_list.append(Slider_Node(self))
        elif event.text() == 'Поле для ввода':
            self.obg_list.append(Edit_Node(self))
        elif event.text() == 'Вход данных':
            self.obg_list.append(Input_serial_Node(self))
        self.show()

    def change_port(self, action):
        print('hi', action.text())
        if action.text()[:13] == 'Текущий порт:' or action.text() == 'Обновить порты':
            self.close()
            self.port.clear()
            self.udate = QAction('Обновить порты', self)
            self.port.addAction(self.udate)
            self.display_port = QAction('Текущий порт: ' + self.now_port, self)
            self.port.addAction(self.display_port)
            for i in serial_ports():
                edt = QAction(i, self)
                self.port.addAction(edt)
            self.show()
        else:
            self.display_port.setText('Текущий порт: ' + action.text())
            self.now_port = action.text()

    def change_speed(self, action):
        try:
            self.now_speed = int(action.text())
            self.speed_viewier.setText('Текущая скорость: ' + action.text())
        except ValueError:
            pass

    def connect(self):
        if self.now_port != '':
            try:
                global ser
                ser = serial.Serial(self.now_port, self.now_speed)
                self.connect_btn.setText('Подключено')
            except Exception:
                self.connect_btn.setText('Не подключено')

    def disConnect(self):
        global ser
        ser.close()
        ser = Hollow_serial()
        self.connect_btn.setText('Подключить')


class Hollow_serial:
    def write(self, data):
        pass

    def readline(self):
        return None


class Node:
    def __init__(self, main_obg, name, first_x, first_y):
        # переменные кординат левого верхнего угла нода
        self.main_window_obg = main_obg  # обьект основного окна
        self.flag = True  # флаг для стрелочки настроек
        self.x = int(first_x)
        self.y = int(first_y)
        self.delete = True

        self.left_com = '$'
        self.middle_com = ' '
        self.right_com = ';'

        self.node_name = QLabel(self.main_window_obg)
        self.node_name.setText(name)
        self.node_name.resize(self.node_name.sizeHint())
        self.name = name

        self.control_btn = QPushButton('...', self.main_window_obg)
        self.control_btn.resize(20, 20)
        self.control_btn.pressed.connect(self.press_control_btn)
        self.control_btn.clicked.connect(self.released_control_btn)

        self.delete_btn = QPushButton('✖', self.main_window_obg)
        self.delete_btn.resize(20, 20)
        self.delete_btn.clicked.connect(self.del_widgets)

        self.copy_btn = QPushButton('❐', self.main_window_obg)
        self.copy_btn.resize(20, 20)
        self.copy_btn.clicked.connect(self.copy_widget)

        self.settings_btn = QPushButton('▲', self.main_window_obg)
        self.settings_btn.resize(20, 20)
        self.settings_btn.clicked.connect(self.open_setings)

        self.text_set1 = QLabel(self.main_window_obg)
        self.text_set1.setText('Имя нода:')

        self.input_line1 = QLineEdit(name, self.main_window_obg)
        self.input_line1.textChanged.connect(self.change_name)
        self.input_line1.resize(60, 23)

        self.arr_of_elem = [(self.node_name, 42, 1), (self.control_btn, 0, 0),
                            (self.settings_btn, 21, 0), (self.text_set1, 1, 54),
                            (self.input_line1, 62, 51), (self.delete_btn, -21, 0), (self.copy_btn, 0, -21)]

        self.ubdate_cord(first_x, first_y)

    def press_control_btn(self):
        global trigered_node
        trigered_node = self

    def released_control_btn(self):
        global trigered_node
        trigered_node = None

    def ubdate_cord(self, x, y):
        for elem in self.arr_of_elem:
            elem[0].move(x + elem[1], y + elem[2])
        self.x = x
        self.y = y

    def change_name(self):
        self.node_name.setText(self.input_line1.text())
        self.node_name.resize(self.node_name.sizeHint())
        self.name = self.input_line1.text()

    def copy_widget(self):
        self.main_window_obg.copy_node(self.parametrs_return())


    def is_delete(self):
        return self.delete


class Button_Node(Node):
    def __init__(self, main_obg, parametrs=['0', 'Вкл', '50', '50', '1', '1', '0', '1',
                                            'выкл', '1', 'Кнопка', 'None', '0']):
        super().__init__(main_obg, parametrs[10], int(parametrs[2]), int(parametrs[3]))

        self.main_window_obg = main_obg

        self.index_comand = parametrs[4]
        self.first_comand = parametrs[5]  # Первая команда
        self.second_comand = parametrs[6]  # Вторая команда
        self.btn_flag = True  # Отправка первой или второй команды
        self.parametr_btn = False  # наличие второй команды
        self.btn_name = parametrs[1]
        self.two_btn_name = parametrs[8]
        self.size_big_btn = float(parametrs[7])
        self.mode = int(parametrs[9])  # тип кнопки 1 - одна команда 2 - две попеременно 3 - две "нажал отпустил"
        self.key_state = bool(int(parametrs[12]))
        self.key_btn = int(parametrs[11]) if parametrs[11] != 'None' else None
        self.key_flag = False

        # |--------------------------------------------| обьявление виджетов
        self.big_btn = QPushButton(self.btn_name, self.main_window_obg)
        self.big_btn.clicked.connect(self.enter_comand)
        self.big_btn.pressed.connect(self.enter_comand_for_3_mode)

        self.text_set2 = QLabel(self.main_window_obg)
        self.text_set2.setText('Имя кнопки 1:')
        self.input_line2 = QLineEdit(self.btn_name, self.main_window_obg)
        self.input_line2.textChanged.connect(self.change_btn_name_1)
        self.input_line2.resize(60, 23)

        self.text_set3 = QLabel(self.main_window_obg)
        self.text_set3.setText('Индекс:')
        self.input_line3 = QLineEdit(self.index_comand, self.main_window_obg)
        self.input_line3.textChanged.connect(self.change_index)
        self.input_line3.resize(60, 23)

        self.text_set4 = QLabel(self.main_window_obg)
        self.text_set4.setText('Команда 1:')
        self.input_line4 = QLineEdit(self.first_comand, self.main_window_obg)
        self.input_line4.textChanged.connect(self.change_first_parametr)
        self.input_line4.resize(60, 23)

        self.text_set5 = QLabel(self.main_window_obg)
        self.text_set5.setText('Размер:')
        self.input_line5 = QLineEdit(str(self.size_big_btn), self.main_window_obg)
        self.input_line5.editingFinished.connect(self.change_size_big_btn)
        self.input_line5.resize(60, 23)

        self.rb_group = QButtonGroup(self.main_window_obg)
        self.rb1 = QRadioButton("Один сигнал", self.main_window_obg)
        self.rb1.move(50, 50)
        if self.mode == 1:
            self.rb1.click()
        self.rb1.clicked.connect(self.update_type)
        self.rb2 = QRadioButton("Два сигнала попеременно", self.main_window_obg)
        self.rb2.move(80, 50)
        if self.mode == 2:
            self.rb2.click()
        self.rb2.clicked.connect(self.update_type)
        self.rb3 = QRadioButton('Два сигнала "нажал-отпустил"', self.main_window_obg)
        self.rb3.move(120, 50)
        if self.mode == 3:
            self.rb3.click()
        self.rb3.clicked.connect(self.update_type)
        self.rb_group.addButton(self.rb1)
        self.rb_group.addButton(self.rb2)
        self.rb_group.addButton(self.rb3)

        self.text_set7 = QLabel(self.main_window_obg)
        self.text_set7.setText('Команда 2:')
        self.input_line7 = QLineEdit(self.second_comand, self.main_window_obg)
        self.input_line7.textChanged.connect(self.change_second_parametr)
        self.input_line7.resize(60, 23)

        self.text_set8 = QLabel(self.main_window_obg)
        self.text_set8.setText('Имя кнопки 2:')
        self.input_line8 = QLineEdit(self.two_btn_name, self.main_window_obg)
        self.input_line8.textChanged.connect(self.change_btn_name_2)
        self.input_line8.resize(60, 23)

        self.key_chekBox = QCheckBox('Использовать клавиши', self.main_window_obg)
        self.key_chekBox.stateChanged.connect(self.change_key_state)
        if self.key_state:
            self.key_chekBox.click()

        self.lit = QLabel(self.main_window_obg)
        if self.key_btn != None:
            self.lit.setText(chr(self.key_btn))
        #  |--------------------------------------------|
        #  Список всех виджетов нода и их относительных координат
        self.arr_of_elem.extend([(self.big_btn, 0, 21), (self.text_set2, 0, 78),
                                 (self.input_line2, 84, 76), (self.text_set3, 0, 102),
                                 (self.input_line3, 46, 100),
                                 (self.text_set4, 0, 128), (self.input_line4, 66, 125),
                                 (self.text_set5, 0, 152), (self.input_line5, 50, 150),
                                 (self.rb1, 0, 170), (self.rb2, 0, 190), (self.rb3, 0, 210),
                                 (self.text_set7, 0, 232), (self.input_line7, 66, 230),
                                 (self.text_set8, 0, 257), (self.input_line8, 84, 255),
                                 (self.key_chekBox, 0, 280), (self.lit, 0, 50)])
        #  Список всех виджетов настроек
        self.elems_of_settings = [self.text_set1, self.input_line1, self.text_set2,
                                  self.input_line2, self.input_line3, self.text_set3,
                                  self.text_set4, self.input_line4,
                                  self.text_set5, self.input_line5, self.rb1, self.rb2,
                                  self.rb3, self.text_set7, self.input_line7, self.text_set8,
                                  self.input_line8, self.key_chekBox, self.delete_btn, self.copy_btn]
        #  Список дополнительных настроек
        self.additional_widgets = [self.text_set7, self.input_line7,
                                   self.text_set8, self.input_line8]
        for elem in self.elems_of_settings:
            elem.hide()
        self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))
        self.ubdate_cord(self.x, self.y)
        self.update_type()
        for elem in self.additional_widgets:
            elem.hide()
        self.change_key_state(None, self.key_btn)


    def del_widgets(self):
        if self.delete:
            for elem in self.arr_of_elem:
                elem[0].deleteLater()
            self.delete = False

    def parametrs_return(self):
        return ['0', self.btn_name, str(self.x), str(self.y), self.index_comand, self.first_comand,
                self.second_comand, str(self.size_big_btn), self.two_btn_name, str(self.mode), self.name,
                str(self.key_btn), str(int(self.key_state))]

    def enter_comand(self):
        global ser
        if self.mode == 2:
            comand = self.left_com + self.index_comand + \
                     self.middle_com + self.first_comand + self.right_com if self.btn_flag else \
                self.left_com + self.index_comand + \
                self.middle_com + self.second_comand + self.right_com
            print('2', comand)
            if self.btn_flag:
                ser.write(comand.encode())
                self.big_btn.setText(self.btn_name)
                self.btn_flag = False
            else:
                ser.write(comand.encode())
                self.big_btn.setText(self.two_btn_name)
                self.btn_flag = True
        elif self.mode == 1:
            comand = self.left_com + self.index_comand + \
                     self.middle_com + self.first_comand + self.right_com
            self.big_btn.setText(self.btn_name)
            ser.write(comand.encode())
            print(comand)
        elif self.mode == 3:
            comand = self.left_com + self.index_comand + \
                     self.middle_com + self.first_comand + self.right_com
            self.big_btn.setText(self.btn_name)
            ser.write(comand.encode())
            print(comand)

    def enter_comand_for_3_mode(self):
        global ser
        if self.mode == 3:
            comand = self.left_com + self.index_comand + \
                     self.middle_com + self.second_comand + self.right_com
            self.big_btn.setText(self.two_btn_name)
            ser.write(comand.encode())
            print(comand)

    def change_btn_name_1(self):
        self.big_btn.setText(self.input_line2.text())
        self.btn_name = self.input_line2.text()
        self.big_btn.resize(self.big_btn.sizeHint())

    def change_btn_name_2(self):
        self.two_btn_name = self.input_line8.text()

    def change_index(self):
        self.index_comand = self.input_line3.text()

    def change_parametr_btn(self):
        self.parametr_btn = not self.parametr_btn
        if self.parametr_btn:
            for elem in [self.text_set2]:
                elem.show()
        else:
            for elem in [self.text_set2]:
                elem.hide()

    def change_first_parametr(self):
        self.first_comand = self.input_line4.text()

    def change_second_parametr(self):
        self.second_comand = self.input_line7.text()

    def change_size_big_btn(self):
        self.size_big_btn = float(self.input_line5.text())
        self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))

    def change_key_state(self, data, key=None, released=False):
        # self.key_state = not self.key_state
        try:
            if self.key_chekBox.isChecked() and key == None:
                self.key_state = True
                self.key_flag = True
                self.key_chekBox.setText('Нажмите на клавишу')
            elif key != None and self.key_flag:
                self.key_chekBox.setText('Нажата клавиша:' + chr(key))
                self.lit.setText(chr(key))
                #self.lit.resize(self.lit.sizeHint())
                self.btn_flag = True
                self.key_btn = key
                self.key_flag = False
            elif self.key_btn == key and data != None:
                if self.mode == 3 and released:
                    self.enter_comand()
                elif self.mode == 3 and not released:
                    self.enter_comand_for_3_mode()
                elif not released:
                    self.big_btn.click()
            elif not self.key_chekBox.isChecked():
                self.key_btn = key
                self.lit.setText('')
                self.key_state = False
                self.key_chekBox.setText('Использовать клавиши')
        except Exception:
            pass

    def update_type(self):
        if self.rb1.isChecked():
            self.mode = 1
            self.big_btn.setCheckable(False)
            for elem in self.additional_widgets:
                elem.hide()
        elif self.rb2.isChecked():
            self.mode = 2
            self.big_btn.setCheckable(True)
            for elem in self.additional_widgets:
                elem.show()
        elif self.rb3.isChecked():
            self.mode = 3
            self.big_btn.setCheckable(False)
            for elem in self.additional_widgets:
                elem.show()

    def open_setings(self):
        if self.flag:
            self.settings_btn.setText('▼')
            self.flag = False
            for elem in self.elems_of_settings:
                elem.show()
            if self.mode == 1:
                for elem in self.additional_widgets:
                    elem.hide()
            self.big_btn.resize(100, 30)
            self.lit.hide()
        else:
            self.settings_btn.setText('▲')
            self.flag = True
            for elem in self.elems_of_settings:
                elem.hide()
            self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))
            self.lit.show()

    def is_keyword(self):
        return True if self.key_state else False


class Slider_Node(Node):
    def __init__(self, main_obg, parametrs=['1', 'Слайдер', '50', '50', '10', 1, 1, '', '0', '100']):
        super().__init__(main_obg, parametrs[1], int(parametrs[2]), int(parametrs[3]))

        self.index_comand = parametrs[4]
        self.size_slider = float(parametrs[5])
        self.mode = int(parametrs[6])  # тип слайдера
        self.value_sld = 0
        self.binding = int(parametrs[7]) if parametrs[7] != '' else ''
        self.min = int(parametrs[8])
        self.max = int(parametrs[9])


        # |--------------------------------------------| обьявление виджетов
        self.sld = QSlider(Qt.Horizontal, self.main_window_obg)
        self.sld.setFocusPolicy(Qt.NoFocus)
        self.sld.setGeometry(30, 40, 100, 30)
        self.sld.valueChanged[int].connect(self.changeValue)
        self.sld.sliderReleased.connect(self.enter_comand)
        self.sld.setMinimum(self.min)
        self.sld.setMaximum(self.max)
        self.sld.resize(int(100 * self.size_slider), 30)

        self.text_set2 = QLabel(self.main_window_obg)
        self.text_set2.setText('None')

        self.text_set3 = QLabel(self.main_window_obg)
        self.text_set3.setText('Индекс:')
        self.input_line3 = QLineEdit(self.index_comand, self.main_window_obg)
        self.input_line3.textChanged.connect(self.change_index)
        self.input_line3.resize(60, 23)

        self.text_set5 = QLabel(self.main_window_obg)
        self.text_set5.setText('Размер:')
        self.input_line5 = QLineEdit(str(self.size_slider), self.main_window_obg)
        self.input_line5.editingFinished.connect(self.change_size_sld)
        self.input_line5.resize(60, 23)

        self.text_set4 = QLabel(self.main_window_obg)
        self.text_set4.setText('Минимум:')
        self.input_line4 = QLineEdit(str(self.min), self.main_window_obg)
        self.input_line4.textChanged.connect(self.change_minimum)
        self.input_line4.resize(60, 23)

        self.text_set6 = QLabel(self.main_window_obg)
        self.text_set6.setText('Максимум:')
        self.input_line6 = QLineEdit(str(self.max), self.main_window_obg)
        self.input_line6.textChanged.connect(self.change_maximum)
        self.input_line6.resize(60, 23)

        self.text_set7 = QLabel(self.main_window_obg)
        self.text_set7.setText('Привязка:')
        self.input_line7 = QLineEdit(str(self.binding), self.main_window_obg)
        self.input_line7.textChanged.connect(self.change_binding)
        self.input_line7.resize(60, 23)

        self.rb_group = QButtonGroup(self.main_window_obg)
        self.rb1 = QRadioButton("Отправка при отпуске", self.main_window_obg)
        self.rb1.move(50, 50)
        if self.mode == 1:
            self.rb1.click()
        self.rb1.clicked.connect(self.update_type)
        self.rb2 = QRadioButton("Отправка при изменении", self.main_window_obg)
        self.rb2.move(80, 50)
        if self.mode == 2:
            self.rb2.click()
        self.rb2.clicked.connect(self.update_type)
        self.rb_group.addButton(self.rb1)
        self.rb_group.addButton(self.rb2)

        #  |--------------------------------------------|
        #  Список всех виджетов нода и их относительных координат
        self.arr_of_elem.extend([(self.text_set2, 0, 50), (self.sld, 0, 21),
                                 (self.text_set3, 0, 76), (self.input_line3, 46, 75),
                                 (self.text_set4, 0, 102), (self.input_line4, 63, 100),
                                 (self.text_set6, 0, 127), (self.input_line6, 63, 125),
                                 (self.text_set5, 0, 152), (self.input_line5, 50, 150),
                                 (self.text_set7, 0, 177), (self.input_line7, 63, 175),
                                 (self.rb1, 0, 195), (self.rb2, 0, 215)])
        #  Список всех виджетов настроек
        self.elems_of_settings = [self.text_set1, self.input_line1,
                                  self.input_line3, self.text_set3,
                                  self.text_set5, self.input_line5, self.rb1, self.rb2,
                                  self.text_set4, self.text_set6, self.input_line4, self.input_line6,
                                  self.text_set7, self.input_line7, self.delete_btn, self.copy_btn]
        #  Список дополнительных настроек
        for elem in self.elems_of_settings:
            elem.hide()
        # self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))
        self.ubdate_cord(self.x, self.y)

    def del_widgets(self):
        if self.delete:
            for elem in self.arr_of_elem:
                elem[0].deleteLater()
            self.delete = False

    def parametrs_return(self):
        return ['1', self.name, str(self.x), str(self.y), self.index_comand, str(self.size_slider),
                str(self.mode), str(self.binding), str(self.min), str(self.max)]

    def enter_comand(self):
        if self.mode == 1:
            global ser
            comand = self.left_com + self.index_comand + \
                     self.middle_com + str(self.value_sld) + self.right_com
            ser.write(comand.encode())
        if self.binding != '':
            try:
                self.sld.setValue(int(self.binding))
                comand = self.left_com + self.index_comand + \
                         self.middle_com + str(self.value_sld) + self.right_com
                ser.write(comand.encode())
            except ValueError:
                pass

    def change_index(self):
        self.index_comand = self.input_line3.text()

    def change_size_sld(self):
        try:
            self.size_slider = float(self.input_line5.text())
            self.sld.resize(int(100 * self.size_slider), 30)
        except ValueError:
            pass

    def change_binding(self):
        self.binding = self.input_line7.text()

    def changeValue(self, value='X_X'):
        global ser
        self.value_sld = value
        self.text_set2.setText(str(value))
        self.text_set2.resize(self.text_set2.sizeHint())
        if self.mode == 2:
            comand = self.left_com + self.index_comand + \
                     self.middle_com + str(self.value_sld) + self.right_com
            ser.write(comand.encode())

    def change_maximum(self):
        try:
            self.max = int(self.input_line6.text())
            self.sld.setMaximum(self.max)
        except ValueError:
            pass

    def change_minimum(self):
        try:
            self.min = int(self.input_line6.text())
            self.sld.setMinimum(self.min)
        except ValueError:
            pass

    def update_type(self):
        if self.rb1.isChecked():
            self.mode = 1
        elif self.rb2.isChecked():
            self.mode = 2

    def open_setings(self):
        if self.flag:
            self.settings_btn.setText('▼')
            self.flag = False
            for elem in self.elems_of_settings:
                elem.show()
            self.text_set2.hide()
        else:
            self.settings_btn.setText('▲')
            self.flag = True
            for elem in self.elems_of_settings:
                elem.hide()
            self.text_set2.show()

    def is_keyword(self):
        return False


class Edit_Node(Node):
    def __init__(self, main_obg, parametrs=['2', 'Ввод', '50', '50', '5']):
        super().__init__(main_obg, parametrs[1], int(parametrs[2]), int(parametrs[3]))

        self.index_comand = parametrs[4]

        # |--------------------------------------------| обьявление виджетов
        self.edit = QLineEdit('', self.main_window_obg)
        self.edit.editingFinished.connect(self.enter_comand)

        self.last_comand1 = QLabel(self.main_window_obg)
        self.last_comand1.setText('None')

        self.last_comand2 = QLabel(self.main_window_obg)
        self.last_comand2.setText('None')

        self.last_comand3 = QLabel(self.main_window_obg)
        self.last_comand3.setText('None')

        self.text_set3 = QLabel(self.main_window_obg)
        self.text_set3.setText('Индекс:')
        self.input_line3 = QLineEdit(self.index_comand, self.main_window_obg)
        self.input_line3.textChanged.connect(self.change_index)
        self.input_line3.resize(60, 23)

        # self.text_set4 = QLabel(self.main_window_obg)
        # self.text_set4.setText('F(x)')
        # self.input_line4 = QLineEdit('0', self.main_window_obg)
        # self.input_line4.textChanged.connect(self.change_minimum)
        # self.input_line4.resize(60, 23)
        #  |--------------------------------------------|
        #  Список всех виджетов нода и их относительных координат
        self.arr_of_elem.extend([(self.last_comand1, 0, 50), (self.last_comand2, 50, 50),
                                 (self.last_comand3, 100, 50), (self.edit, 0, 25),
                                 (self.text_set3, 0, 76), (self.input_line3, 46, 75)])
        #  Список всех виджетов настроек
        self.elems_of_settings = [self.text_set1, self.input_line1,
                                  self.input_line3, self.text_set3, self.delete_btn, self.copy_btn]
        #  Список дополнительных настроек
        for elem in self.elems_of_settings:
            elem.hide()
        # self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))
        self.ubdate_cord(self.x, self.y)

    def del_widgets(self):
        if self.delete:
            for elem in self.arr_of_elem:
                elem[0].deleteLater()
            self.delete = False


    def parametrs_return(self):
        return ['2', self.name, str(self.x), str(self.y), self.index_comand]

    def enter_comand(self):
        global ser
        if self.edit.text() != '':
            comand = self.left_com + self.index_comand + \
                     self.middle_com + self.edit.text() + self.right_com
            ser.write(comand.encode())
            self.last_comand3.setText(self.last_comand2.text())
            self.last_comand2.setText(self.last_comand1.text())
            self.last_comand1.setText(self.edit.text())

            self.last_comand1.resize(self.last_comand1.sizeHint())
            self.last_comand2.resize(self.last_comand2.sizeHint())
            self.last_comand3.resize(self.last_comand3.sizeHint())

        self.edit.setText('')

    def change_index(self):
        self.index_comand = self.input_line3.text()

    def changeValue(self, value='X_X'):
        global ser
        self.value_sld = value
        self.last_comand1.setText(str(value))
        self.last_comand1.resize(self.last_comand1.sizeHint())
        if self.mode == 2:
            comand = comand = self.left_com + self.index_comand + \
                     self.middle_com + str(self.value_sld) + self.right_com
            print('enter', comand)
            ser.write(comand.encode())

    def open_setings(self):
        if self.flag:
            self.settings_btn.setText('▼')
            self.flag = False
            for elem in self.elems_of_settings:
                elem.show()
            self.last_comand1.hide()
            self.last_comand2.hide()
            self.last_comand3.hide()
        else:
            self.settings_btn.setText('▲')
            self.flag = True
            for elem in self.elems_of_settings:
                elem.hide()
            self.last_comand1.show()
            self.last_comand2.show()
            self.last_comand3.show()

    def is_keyword(self):
        return False


class Input_serial_Node(Node):
    def __init__(self, main_obg, parametrs=['3', 'Ввод', '50', '50', '5', '1']):
        super().__init__(main_obg, parametrs[1], int(parametrs[2]), int(parametrs[3]))

        self.index_comand = parametrs[4]
        self.sizeLCD = float(parametrs[5])

        # |--------------------------------------------| обьявление виджетов

        self.numberLCD = QLCDNumber(self.main_window_obg)
        self.numberLCD.resize(int(80 * self.sizeLCD), int(27 * self.sizeLCD))

        self.text_set3 = QLabel(self.main_window_obg)
        self.text_set3.setText('Индекс:')
        self.input_line3 = QLineEdit(self.index_comand, self.main_window_obg)
        self.input_line3.textChanged.connect(self.change_index)
        self.input_line3.resize(60, 23)

        self.text_set4 = QLabel(self.main_window_obg)
        self.text_set4.setText('Размер:')
        self.input_line4 = QLineEdit(str(self.sizeLCD), self.main_window_obg)
        self.input_line4.editingFinished.connect(self.change_size_lcd)
        self.input_line4.resize(60, 23)
        #  |--------------------------------------------|
        #  Список всех виджетов нода и их относительных координат
        self.arr_of_elem.extend([(self.numberLCD, 0, 21), (self.text_set3, 0, 76), (self.input_line3, 48, 75),
                                 (self.text_set4, 0, 102), (self.input_line4, 48, 100)])
        #  Список всех виджетов настроек
        self.elems_of_settings = [self.input_line1, self.text_set1, self.input_line3,
                                  self.text_set3, self.delete_btn,
                                  self.input_line4, self.text_set4, self.copy_btn]
        #  Список дополнительных настроек
        for elem in self.elems_of_settings:
            elem.hide()
        # self.big_btn.resize(int(100 * self.size_big_btn), int(30 * self.size_big_btn))
        self.ubdate_cord(self.x, self.y)

    def del_widgets(self):
        if self.delete:
            for elem in self.arr_of_elem:
                elem[0].deleteLater()
            self.delete = False

    def change_size_lcd(self):
        try:
            self.sizeLCD = float(self.input_line4.text())
            self.numberLCD.resize(int(80 * self.sizeLCD), int(27 * self.sizeLCD))
        except ValueError:
            pass

    def parametrs_return(self):
        return ['3', self.name, str(self.x), str(self.y), self.index_comand, str(self.sizeLCD)]

    def change_index(self):
        self.index_comand = self.input_line3.text()

    def displayValue(self, value='error'):
        try:
            indx = value.split()[0]
            com = value.split()[1]
            if indx == self.index_comand:
                self.numberLCD.display(com)
        except:
            pass

    def open_setings(self):
        if self.flag:
            self.settings_btn.setText('▼')
            self.flag = False
            for elem in self.elems_of_settings:
                elem.show()
            self.numberLCD.resize(80, 27)
        else:
            self.settings_btn.setText('▲')
            self.flag = True
            for elem in self.elems_of_settings:
                elem.hide()
            self.numberLCD.resize(int(80 * self.sizeLCD), int(27 * self.sizeLCD))

    def is_keyword(self):
        return False





ser = Hollow_serial()
trigered_node = None  # глобальная переменная для перетаскивания кнопок

app = QApplication(sys.argv)
ex = Main_window()
ex.show()
sys.exit(app.exec())
