import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QCheckBox, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QRadioButton, QButtonGroup, QScrollArea, QHBoxLayout, QGroupBox

class GPUSelector(QWidget):
    def __init__(self, gpu_types):
        super().__init__()
        self.gpu_types = gpu_types
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        self.name_edit = QLineEdit()
        layout.addWidget(QLabel('名字:'), 0, 0)
        layout.addWidget(self.name_edit, 0, 1, 1, 3)

        self.gpu_combo = QComboBox()
        for gpu in self.gpu_types:
            self.gpu_combo.addItem(f"{gpu['displayName']} - {gpu['memoryInGb']} GB - Max GPU: {gpu['maxGpuCount']}", gpu)
        layout.addWidget(QLabel('GPU 型号:'), 1, 0)
        layout.addWidget(self.gpu_combo, 1, 1)

        self.image_name_edit = QLineEdit()
        layout.addWidget(QLabel('镜像名:'), 1, 2)
        layout.addWidget(self.image_name_edit, 1, 3)

        self.cloud_type_group = QButtonGroup(self)
        self.secure_radio = QRadioButton('Secure')
        self.community_radio = QRadioButton('Community')
        self.all_radio = QRadioButton('All')
        self.cloud_type_group.addButton(self.secure_radio)
        self.cloud_type_group.addButton(self.community_radio)
        self.cloud_type_group.addButton(self.all_radio)
        cloud_type_box = QVBoxLayout()
        cloud_type_box.addWidget(self.secure_radio)
        cloud_type_box.addWidget(self.community_radio)
        cloud_type_box.addWidget(self.all_radio)
        cloud_type_groupbox = QGroupBox('服务器类型:')
        cloud_type_groupbox.setLayout(cloud_type_box)
        layout.addWidget(cloud_type_groupbox, 2, 0, 1, 2)

        self.pricing_model_group = QButtonGroup(self)
        self.on_demand_radio = QRadioButton('On Demand')
        self.spot_radio = QRadioButton('Spot')
        self.pricing_model_group.addButton(self.on_demand_radio)
        self.pricing_model_group.addButton(self.spot_radio)
        pricing_model_box = QVBoxLayout()
        pricing_model_box.addWidget(self.on_demand_radio)
        pricing_model_box.addWidget(self.spot_radio)
        pricing_model_groupbox = QGroupBox('服务器租赁模式:')
        pricing_model_groupbox.setLayout(pricing_model_box)
        layout.addWidget(pricing_model_groupbox, 2, 2, 1, 2)

        self.os_disk_size_edit = QLineEdit()
        layout.addWidget(QLabel('缓存盘大小 (GB):'), 3, 0)
        layout.addWidget(self.os_disk_size_edit, 3, 1)

        self.persistent_disk_size_edit = QLineEdit()
        layout.addWidget(QLabel('硬盘大小 (GB):'), 3, 2)
        layout.addWidget(self.persistent_disk_size_edit, 3, 3)

        self.http_port_edit = QLineEdit()
        layout.addWidget(QLabel('HTTP 端口:'), 4, 0)
        layout.addWidget(self.http_port_edit, 4, 1)

        self.tcp_port_edit = QLineEdit()
        layout.addWidget(QLabel('TCP 端口:'), 4, 2)
        layout.addWidget(self.tcp_port_edit, 4, 3)

        self.env_var_edit = QLineEdit()
        layout.addWidget(QLabel('环境变量:'), 5, 0)
        layout.addWidget(self.env_var_edit, 5, 1, 1, 3)

        self.create_button = QPushButton('创建')
        self.create_button.clicked.connect(self.create_pod)
        layout.addWidget(self.create_button, 6, 0, 1, 2)

        self.delete_all_button = QPushButton('删除所有')
        self.delete_all_button.clicked.connect(self.delete_all_pods)
        layout.addWidget(self.delete_all_button, 6, 2, 1, 2)

        self.pod_status_area = QScrollArea()
        self.pod_status_area.setWidgetResizable(True)

        scroll_content = QWidget(self.pod_status_area)  # 创建一个主控件
        self.pod_status_layout = QVBoxLayout(scroll_content)  # 将布局添加到主控件中

        # 添加一些按钮到滚动区域
        for i in range(10):  # 假设有10个pod
            pod_layout = QHBoxLayout()

            close_button = QPushButton('关闭')
            close_button.setFixedWidth(int(self.pod_status_area.width() * 0.1))
            close_button.setFixedHeight(40)  # 设置按钮高度
            pod_layout.addWidget(close_button)

            stop_button = QPushButton('停止')
            stop_button.setFixedWidth(int(self.pod_status_area.width() * 0.1))
            stop_button.setFixedHeight(40)  # 设置按钮高度
            pod_layout.addWidget(stop_button)

            pod_info_label = QLabel(f'Pod {i} 信息')
            pod_info_label.setFixedWidth(int(self.pod_status_area.width() * 0.8))
            pod_info_label.setFixedHeight(40)  # 设置标签高度
            pod_layout.addWidget(pod_info_label)

            self.pod_status_layout.addLayout(pod_layout)

        self.pod_status_area.setWidget(scroll_content)


        layout.addWidget(self.pod_status_area, 7, 0, 1, 4)

        self.setLayout(layout)

    def create_pod(self):
        selected_gpu = self.gpu_combo.currentData()
        cloud_type = 'ALL'
        if self.secure_radio.isChecked():
            cloud_type = 'SECURE'
        elif self.community_radio.isChecked():
            cloud_type = 'COMMUNITY'

        pricing_model = 'ON_DEMAND'
        if self.spot_radio.isChecked():
            pricing_model = 'SPOT'

        # TODO: Add code to create pod using the selected options and the input from the text fields

    def delete_all_pods(self):
        pass
        # TODO: Add code to delete all pods

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # TODO: Replace with actual GPU types data
    gpu_types = []

    ex = GPUSelector(gpu_types)
    ex.show()

    sys.exit(app.exec_())
