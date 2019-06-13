from os import listdir, path
import sys
import PIL.Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog


class PThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str)
    num_trigger = QtCore.pyqtSignal(int)

    def __init__(self, info=None):
        super().__init__()
        self.info = info

    def run(self):
        # photo = QtGui.QPixmap(path.join(self.info.folder, self.info.list[0]))
        # self.info.photo_label.setPixmap(photo)
        imgDoc = canvas.Canvas(path.join(self.info.folder, self.info.outer))
        imgDoc.setPageSize(self.info.size)
        i = 0
        for image in self.info.list:
            if self.info.pause_slot == False:
                try:
                    image_file = PIL.Image.open(path.join(self.info.folder, image))
                    if image_file.size[0] > self.info.size[0] and image_file.size[1] > self.info.size[1]:
                        image_file.thumbnail(self.info.size, PIL.Image.ANTIALIAS)
                    image_width, image_height = image_file.size
                    if not (image_width > 0 and image_height > 0):
                        raise Exception

                    imgDoc.drawImage(ImageReader(image_file), 0,
                                     0, width=self.info.size[0],
                                     height=self.info.size[1], preserveAspectRatio=True)

                    imgDoc.showPage()
                    i = i + 1
                    self.num_trigger.emit(i)
                except Exception as e:
                    print('error:', e, image)
                    self.trigger.emit('error:' + e)
            else:
                self.info.pause_slot = False
                break
        imgDoc.save()
        self.trigger.emit('成功')

class Info():
    pass


class Ui_widget(object):
    def __init__(self, widget):
        widget = widget
        self.setupUi()
        self.trigger()
    # pyinstaller -Fw F:\python-venv\python\good\pdf_gui.py
    # F:\python-venv\pdf_gui.spec
    def init_data(self):
        try:
            global info
            info = Info()
            info.pause_slot = False
            info.folder = self.lineEdit.text()
            info.outer = self.lineEdit_2.text()

            if self.order1.isChecked():
                info.order = 1
            elif self.order2.isChecked():
                info.order = 2
            else:
                info.order = 3

            self.type = []
            if self.checkBox.isChecked():
                self.type.append('.png')
            if self.checkBox.isChecked():
                self.type.append('.jpg')

            flist = listdir(info.folder)
            info.list = []
            for name in flist:
                fname, ext = name.split('.')
                if (self.type[0] == '.'+ext) or (self.type[-1] == '.'+ext):
                    info.list.append(name)
                else:
                    pass
            if info.order == 2:
                info.list = sorted(info.list, key=lambda x: path.getmtime(path.join(info.folder, x)))
            if info.order == 3:
                info.list = sorted(info.list)
            info.nums = len(info.list)
            self.nums = info.nums
            info.size = [int(self.width_size.value()), int(self.height_size.value())]
        except:pass

    def trigger(self):
        self.fileButton.clicked.connect(self.get_dir)
        self.start_button.clicked.connect(self.start)
        self.pause_button.clicked.connect(self.pause)

    def get_dir(self):
        folder = QFileDialog.getExistingDirectory(widget)
        self.lineEdit.setText(folder)

    def start(self):
        self.init_data()
        self.new_thread = PThread(info=info)
        self.new_thread.trigger.connect(self.show_message)
        self.new_thread.num_trigger.connect(self.show_progressbar)
        self.new_thread.start()

    def show_message(self, msg):
        self.message_lable.setText(msg)

    def show_progressbar(self, dat):
        self.progressBar.setValue(int(dat / self.nums) * 100)

    def pause(self):
        self.pause_slot = True

    def setupUi(self):
        widget.setObjectName("widget")
        widget.setEnabled(True)
        widget.setFixedSize(800, 800)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
        widget.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        widget.setFont(font)
        self.formLayoutWidget = QtWidgets.QWidget(widget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(20, 20, 441, 521))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.name_label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.name_label.setFont(font)
        self.name_label.setObjectName("name_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.name_label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(1, QtWidgets.QFormLayout.LabelRole, spacerItem)
        self.label1 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label1.setObjectName("label1")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label1)
        self.lineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label2 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label2.setObjectName("label2")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.label2)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_2.setText('out.pdf')
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        spacerItem1 = QtWidgets.QSpacerItem(20, 80, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(5, QtWidgets.QFormLayout.LabelRole, spacerItem1)
        self.label3 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label3.setObjectName("label3")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.label3)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.checkBox = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBox.setIconSize(QtCore.QSize(30, 30))
        self.checkBox.setAutoRepeatDelay(300)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_3.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.formLayoutWidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_2.setChecked(True)
        self.verticalLayout_3.addWidget(self.checkBox_2)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole, self.verticalLayout_3)
        self.label4 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label4.setObjectName("label4")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.label4)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.order1 = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.order1.setObjectName("order1")
        self.verticalLayout.addWidget(self.order1)
        self.order2 = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.order2.setChecked(True)
        self.order2.setObjectName("order2")
        self.verticalLayout.addWidget(self.order2)
        self.order3 = QtWidgets.QRadioButton(self.formLayoutWidget)
        self.order3.setObjectName("order3")
        self.verticalLayout.addWidget(self.order3)
        self.formLayout.setLayout(8, QtWidgets.QFormLayout.FieldRole, self.verticalLayout)
        self.label5 = QtWidgets.QLabel(self.formLayoutWidget)
        self.label5.setObjectName("label5")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.label5)
        self.size_form = QtWidgets.QFormLayout()
        self.size_form.setObjectName("size_form")
        self.height = QtWidgets.QLabel(self.formLayoutWidget)
        self.height.setObjectName("height")
        self.size_form.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.height)
        self.width = QtWidgets.QLabel(self.formLayoutWidget)
        self.width.setObjectName("width")
        self.size_form.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.width)
        self.height_size = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.height_size.setMaximum(5000)
        self.height_size.setValue(500)
        self.height_size.setObjectName("height_size")
        self.size_form.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.height_size)
        self.width_size = QtWidgets.QSpinBox(self.formLayoutWidget)
        self.width_size.setMaximum(5000)
        self.width_size.setValue(500)
        self.width_size.setObjectName("width_size")
        self.size_form.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.width_size)
        self.formLayout.setLayout(10, QtWidgets.QFormLayout.FieldRole, self.size_form)
        self.fileButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.fileButton.setObjectName("fileButton")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.fileButton)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(widget)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(470, 20, 291, 731))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.start_button = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.start_button.sizePolicy().hasHeightForWidth())
        self.start_button.setSizePolicy(sizePolicy)
        self.start_button.setMinimumSize(QtCore.QSize(0, 28))
        self.start_button.setObjectName("start_button")
        self.verticalLayout_2.addWidget(self.start_button)
        self.pause_button = QtWidgets.QPushButton(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pause_button.sizePolicy().hasHeightForWidth())
        self.pause_button.setSizePolicy(sizePolicy)
        self.pause_button.setObjectName("pause_button")
        self.verticalLayout_2.addWidget(self.pause_button)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem2)
        self.progress_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress_label.sizePolicy().hasHeightForWidth())
        self.progress_label.setSizePolicy(sizePolicy)
        self.progress_label.setObjectName("progress_label")
        self.verticalLayout_2.addWidget(self.progress_label)
        self.progressBar = QtWidgets.QProgressBar(self.verticalLayoutWidget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBar.sizePolicy().hasHeightForWidth())
        self.progressBar.setSizePolicy(sizePolicy)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setObjectName("progressBar")
        self.message_lable = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.verticalLayout_2.addWidget(self.progressBar)
        self.verticalLayout_2.addWidget(self.message_lable)
        self.photo_label = QtWidgets.QLabel(widget)
        self.photo_label.setGeometry(QtCore.QRect(20, 560, 441, 181))
        self.photo_label.setObjectName("photo_label")

        self.retranslateUi(widget)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "Form"))
        self.name_label.setText(_translate("widget", "批量图片转换pdf工具"))
        self.label1.setText(_translate("widget", "选择文件夹"))
        self.label2.setText(_translate("widget", "输出名称"))
        self.label3.setText(_translate("widget", "图片类型"))
        self.checkBox.setText(_translate("widget", "png"))
        self.checkBox_2.setText(_translate("widget", "jpg"))
        self.label4.setText(_translate("widget", "图片转换顺序 "))
        self.order1.setText(_translate("widget", "默认顺序"))
        self.order2.setText(_translate("widget", "文件修改顺序"))
        self.order3.setText(_translate("widget", "文件名称顺序"))
        self.label5.setText(_translate("widget", "图片大小"))
        self.height.setText(_translate("widget", "height"))
        self.width.setText(_translate("widget", "width"))
        self.fileButton.setText(_translate("widget", "打开文件夹"))
        self.start_button.setText(_translate("widget", "开始转换 "))
        self.pause_button.setText(_translate("widget", "停止"))
        self.progress_label.setText(_translate("widget", "转换进度"))


if __name__ == '__main__':
    app = QApplication([])
    widget = QWidget()
    ui = Ui_widget(widget)
    widget.show()
    sys.exit(app.exec_())
