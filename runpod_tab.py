import sys
import os
import json
import subprocess
import time
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QCheckBox, QLabel, QLineEdit, QVBoxLayout, QPushButton, QGridLayout, QRadioButton, QButtonGroup, QScrollArea, QHBoxLayout, QGroupBox, QInputDialog, QStyle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Add runpod-api to the path
current_path = os.path.dirname(os.path.abspath(__file__))
preset_json = os.path.join(current_path, 'runpod_presets.json')
api_dir = current_path
# sys.path.insert(0, api_dir)

from get_gpu_types import get_gpu_types
from get_templates import get_latest_tags


class CustomComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_update = 0

    def showPopup(self):
        current_time = time.time()
        if current_time - self.last_update > 60:
            self.parent().update_gpu_types()
            self.last_update = current_time
        super().showPopup()

class GPUSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.gpu_types = sorted(get_gpu_types(), key=lambda gpu: gpu['memoryInGb'])
        self.setWindowTitle("Runpod Deployment Tool")
        # self.setMinimumSize(1200, 800)
        self.initUI()

         # Check for API key
        self.api_key = os.getenv('RUNPOD_API_KEY')
        if not self.api_key:
            try:
                with open(preset_json, 'r') as f:
                    presets = json.load(f)
                    self.api_key = presets.get('api_key')
            except FileNotFoundError:
                pass

        if not self.api_key:
            self.api_key, ok = QInputDialog.getText(self, 'API Key', '请输入 API Key:')
            if ok:
                try:
                    with open(preset_json, 'r+') as f:
                        presets = json.load(f)
                        presets['api_key'] = self.api_key
                        f.seek(0)
                        json.dump(presets, f)
                        f.truncate()
                except FileNotFoundError:
                    with open(preset_json, 'w') as f:
                        json.dump({'api_key': self.api_key}, f)

    def initUI(self):
        layout = QGridLayout()

        preset_group = QGroupBox('预设:')
        preset_layout = QHBoxLayout()
        preset_group.setLayout(preset_layout)
        layout.addWidget(preset_group, 1, 2, 1, 4)

        self.preset_combo = QComboBox()
        self.preset_combo.setMaxVisibleItems(10)
        self.preset_combo.setFixedHeight(50)
        self.preset_combo.addItem("")
        self.preset_combo.currentIndexChanged.connect(self.load_preset)
        preset_layout.addWidget(self.preset_combo)

        self.preset_button = QPushButton('保存预设')
        self.preset_button.setFixedHeight(50)
        self.preset_button.clicked.connect(self.save_preset)
        preset_layout.addWidget(self.preset_button)

        self.load_presets()

        self.image_combo = QComboBox()
        self.image_combo.setMaxVisibleItems(10)
        self.image_combo.setFixedHeight(40)
        layout.addWidget(QLabel('镜像名:'), 1, 0)
        layout.addWidget(self.image_combo, 1, 1)
        repo = 'runpod/stable-diffusion'
        latest_tags = get_latest_tags(repo)
        for tag in latest_tags:
            self.image_combo.addItem(tag)

        layout.addWidget(QLabel('GPU 信息:'), 2, 0)
        self.gpu_combo = QComboBox()
        self.gpu_combo = CustomComboBox(self)
        self.gpu_combo.setMaxVisibleItems(30)
        self.gpu_combo.setFixedHeight(40)
        self.update_gpu_types()
        layout.addWidget(self.gpu_combo, 2, 1, 1, 3)

        self.cloud_type_group = QButtonGroup(self)
        self.secure_radio = QRadioButton('SECURE')
        self.community_radio = QRadioButton('COMMUNITY')
        self.all_radio = QRadioButton('ALL')
        self.all_radio.setChecked(True)
        self.cloud_type_group.addButton(self.secure_radio)
        self.cloud_type_group.addButton(self.community_radio)
        self.cloud_type_group.addButton(self.all_radio)
        cloud_type_box = QHBoxLayout()
        cloud_type_box.addWidget(self.secure_radio)
        cloud_type_box.addWidget(self.community_radio)
        cloud_type_box.addWidget(self.all_radio)
        cloud_type_groupbox = QGroupBox('服务器类型:')
        cloud_type_groupbox.setLayout(cloud_type_box)
        layout.addWidget(cloud_type_groupbox, 3, 0, 1, 2)

        self.pricing_model_group = QButtonGroup(self)
        self.on_demand_radio = QRadioButton('On Demand')
        self.on_demand_radio.setChecked(True)
        self.spot_radio = QRadioButton('Spot')
        self.pricing_model_group.addButton(self.on_demand_radio)
        self.pricing_model_group.addButton(self.spot_radio)
        pricing_model_box = QHBoxLayout()
        pricing_model_box.addWidget(self.on_demand_radio)
        pricing_model_box.addWidget(self.spot_radio)
        self.spot_radio.setChecked(True)
        pricing_model_groupbox = QGroupBox('服务器租赁模式:')
        pricing_model_groupbox.setLayout(pricing_model_box)
        layout.addWidget(pricing_model_groupbox, 3, 2, 1, 2)

        self.os_disk_size_edit = QLineEdit("20")
        layout.addWidget(QLabel('缓存盘大小 (GB):'), 4, 0)
        layout.addWidget(self.os_disk_size_edit, 4, 1)

        self.persistent_disk_size_edit = QLineEdit("50")
        layout.addWidget(QLabel('硬盘大小 (GB):'), 4, 2)
        layout.addWidget(self.persistent_disk_size_edit, 4, 3)

        self.http_port_edit = QLineEdit("8888,4444,7860")
        layout.addWidget(QLabel('HTTP 端口:'), 5, 0)
        layout.addWidget(self.http_port_edit, 5, 1)

        self.tcp_port_edit = QLineEdit("22")
        layout.addWidget(QLabel('TCP 端口:'), 5, 2)
        layout.addWidget(self.tcp_port_edit, 5, 3)

        self.env_var_edit = QLineEdit("RUNPOD_STOP_AUTO=1")
        layout.addWidget(QLabel('环境变量:'), 6, 0)
        layout.addWidget(self.env_var_edit, 6, 1, 1, 3)

        self.create_button = QPushButton('创建')
        self.create_button.setFixedHeight(80)
        self.create_button.clicked.connect(self.create_pod)
        layout.addWidget(self.create_button, 7, 0, 1, 4)

        self.pod_status_area = QScrollArea()
        # self.pod_status_area.setFixedHeight(200)
        self.pod_status_area.setWidgetResizable(True)
        scroll_content = QWidget(self.pod_status_area)
        self.pod_status_layout = QVBoxLayout(scroll_content)
        self.pod_status_layout.setAlignment(Qt.AlignTop)
        self.pod_status_area.setWidget(scroll_content)
        layout.addWidget(self.pod_status_area, 8, 0, 1, 4)
        
        self.refresh_pods()

        self.delete_all_button = QPushButton('删除所有')
        self.delete_all_button.setFixedHeight(50)
        self.delete_all_button.clicked.connect(self.delete_all_pods)
        layout.addWidget(self.delete_all_button, 9, 0, 1, 3)

        self.refresh_button = QPushButton('刷新')
        self.refresh_button.setFixedHeight(50)
        self.refresh_button.clicked.connect(self.refresh_pods)
        layout.addWidget(self.refresh_button, 9, 3, 1, 1)

        # self.api_key_edit = QLineEdit()
        # self.api_key_edit.setEchoMode(QLineEdit.Password)  # 设置输入框的回显模式为密码模式
        # self.show_api_key_button = QPushButton()
        # self.show_api_key_button.setIcon(self.style().standardIcon(QStyle.SP_DialogYesButton))  # 设置按钮的图标为眼睛图标
        # self.show_api_key_button.clicked.connect(self.toggle_api_key_visibility)  # 当点击按钮时，调用 toggle_api_key_visibility 方法

        # layout.addWidget(QLabel('API Key:'), 9, 0)
        # layout.addWidget(self.api_key_edit, 9, 1)
        # layout.addWidget(self.show_api_key_button, 9, 2)

        self.setLayout(layout)


###################################
# funnctions
###################################

    def update_gpu_types(self):
        self.gpu_combo.last_update = time.time()
        self.gpu_types = sorted(get_gpu_types(), key=lambda gpu: gpu['memoryInGb'])
        self.gpu_combo.clear()

        for gpu in self.gpu_types:
                gpu['securePrice'] = ' -' if not gpu.get('secureCloud', False) else gpu.get('securePrice', ' -')
                gpu['communityPrice'] = ' -' if not gpu.get('communityCloud', False) else gpu.get('communityPrice', ' -')
                gpu['lowestPrice']['minimumBidPrice'] = ' -' if gpu['lowestPrice']['minimumBidPrice'] is None else gpu['lowestPrice']['minimumBidPrice']
                gpu_info = (
                    f"{gpu['id']:<30}  |  {gpu['memoryInGb']:<2} GB  |  Max: {gpu['maxGpuCount']:<2}  |  "
                    f"Secure: {gpu['securePrice']:<4}  |  "
                    f"Community: {gpu['communityPrice']:<4}  |  "
                    f"bid: {gpu['lowestPrice']['minimumBidPrice']:<4}"
                )
                self.gpu_combo.addItem(gpu_info, gpu)

    def create_pod(self):
        http_ports = [port + '/http' for port in self.http_port_edit.text().split(',')]
        tcp_ports = [port + '/tcp' for port in self.tcp_port_edit.text().split(',')]
        ports = ','.join(http_ports + tcp_ports)

        command = ['python', 'create_pod.py', 
                '--name', self.gpu_combo.currentData()['id'], 
                '--image_name', self.image_combo.currentText(), 
                '--gpu_type_id', self.gpu_combo.currentData()['id'], 
                '--cloud_type', self.cloud_type_group.checkedButton().text(), 
                '--os_disk_size_gb', str(self.os_disk_size_edit.text()), 
                '--persistent_disk_size_gb', str(self.persistent_disk_size_edit.text()), 
                '--ports', ports, 
                '--user_envs', self.env_var_edit.text()
                ]

        if self.spot_radio.isChecked():
            command.append('--spot')
        try:
            result = subprocess.run(command, cwd=api_dir, capture_output=True, text=True)
        except Exception as e:
            print(f"Error running create_pod.py: {e}")

        if result.returncode == 0:
            if result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    # Extract pod_info based on the pod type
                    if 'podFindAndDeployOnDemand' in data['data']:
                        pod_info = data['data']['podFindAndDeployOnDemand']
                    elif 'podRentInterruptable' in data['data']:
                        pod_info = data['data']['podRentInterruptable']
                except json.JSONDecodeError:
                    print(f"Error parsing JSON: {result.stdout}")
            else:
                print("No output from create_pod.py")
            self.add_pod_to_status_area(pod_info)
        else:
            print(f"Error creating pod: {result.stderr}")

    def add_pod_to_status_area(self, pod_info):
        pod_group = QGroupBox()
        pod_layout = QHBoxLayout(pod_group)

        terminate_button = QPushButton('删除')
        terminate_button.setFixedWidth(80)
        terminate_button.setFixedHeight(60)
        terminate_button.clicked.connect(lambda: self.terminate_pod(pod_info['id'], pod_layout))
        pod_layout.addWidget(terminate_button)

        if pod_info['desiredStatus'] == 'RUNNING':
            stop_button = QPushButton('停止')
            stop_button.setFixedWidth(80)
            stop_button.setFixedHeight(60)
            stop_button.clicked.connect(lambda: self.stop_pod(pod_info, stop_button))
            pod_layout.addWidget(stop_button)
        elif pod_info['desiredStatus'] == 'EXITED':
            start_button = QPushButton('开始')
            start_button.setFixedWidth(80)
            start_button.setFixedHeight(60)
            start_button.clicked.connect(lambda: self.start_pod(pod_info, start_button))
            pod_layout.addWidget(start_button)

        pod_info_label = QLabel(
            f"{pod_info['name']} - {pod_info['id']}<br>"
            f"{pod_info['podType']} - {pod_info['costPerHr']}<br>"
            f"{pod_info['imageName']}"
        )
        pod_info_label.setFixedWidth(500)
        pod_layout.addWidget(pod_info_label)
        pod_layout.setAlignment(Qt.AlignLeft)
        self.update_groupbox_color(pod_group, pod_info['desiredStatus'])
        self.pod_status_layout.addWidget(pod_group)

    def get_pods(self):
        result = subprocess.run(['python', 'get_pods.py'], cwd=api_dir, capture_output=True, text=True)
        pod_info = json.loads(result.stdout) if result.stdout.strip() else []
        return pod_info

    def stop_pod(self, pod_info, stop_button):
        pod_id = pod_info['id']
        subprocess.run(['python', os.path.join(api_dir, 'stop_pod.py'), '--pod_id', str(pod_id)])
        # Update the stop button to a start button
        stop_button.setText('开始')
        stop_button.clicked.connect(lambda: self.start_pod(pod_info, stop_button))
        self.update_groupbox_color(stop_button.parent(), 'EXITED')

    def start_pod(self, pod_info, stop_button):
        pod_id = pod_info['id']
        spot = pod_info['podType'] == 'INTERRUPTABLE'
        if spot:
            bid_price = str(pod_info['costPerHr'])
            # bid_price = str(pod_info['lowestBidPriceToResume'])
            subprocess.run(['python', 'start_spot_pod.py', '--pod_id', str(pod_id), '--bid_price', bid_price], cwd=api_dir)
        else:
            subprocess.run(['python', os.path.join(api_dir, 'start_on_demand_pod.py'), '--pod_id', str(pod_id)])
        # Update the start button to a stop button
        stop_button.setText('停止')
        self.update_groupbox_color(stop_button.parent(), 'RUNNING')
        stop_button.clicked.connect(lambda: self.stop_pod(pod_info, stop_button))

    def update_groupbox_color(self, groupbox, status):
        if status == 'RUNNING':
            groupbox.setStyleSheet("QGroupBox { background-color: #8fe4bd; }")
        elif status == 'EXITED':
            groupbox.setStyleSheet("QGroupBox { background-color: #c9d0ed; }")

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clear_layout(child.layout())

    def update_pods_in_ui(self, pod_infos):
        pod_infos = sorted(pod_infos, key=lambda pod: datetime.datetime.strptime(" ".join(pod['name'].rsplit(" ", 2)[-2:]), "%Y-%m-%d %H:%M:%S"))

        self.clear_layout(self.pod_status_layout)
        for pod_info in pod_infos:
            self.add_pod_to_status_area(pod_info)

    def refresh_pods(self):
        pod_infos = self.get_pods()
        self.update_pods_in_ui(pod_infos)

    def terminate_pod(self, pod_id, pod_layout):
        subprocess.run(['python', os.path.join(api_dir, 'terminate_pod.py'), '--pod_id', str(pod_id)])
        self.refresh_pods()

    def delete_all_pods(self):
        subprocess.run(['python', os.path.join(api_dir, 'terminate_all_pods.py')])
        self.refresh_pods()

    # def toggle_api_key_visibility(self):
    #     if self.api_key_edit.echoMode() == QLineEdit.Password:
    #         self.api_key_edit.setEchoMode(QLineEdit.Normal)
    #     else:
    #         self.api_key_edit.setEchoMode(QLineEdit.Password)

    def save_preset(self):
        preset_name, ok = QInputDialog.getText(self, '预设名称', '请输入预设名称:')
        if ok:
            preset = {
                'gpu_type_id': self.gpu_combo.currentData()['id'],
                'image_name': self.image_combo.currentText(),
                'secure_radio': self.secure_radio.isChecked(),
                'community_radio': self.community_radio.isChecked(),
                'all_radio': self.all_radio.isChecked(),
                'spot': self.spot_radio.isChecked(),
                'on_demand': self.on_demand_radio.isChecked(),
                'os_disk_size_gb': str(self.os_disk_size_edit.text()),
                'persistent_disk_size_gb': str(self.persistent_disk_size_edit.text()),
                'http_ports': self.http_port_edit.text(),
                'tcp_ports': self.tcp_port_edit.text(),
                'user_envs': self.env_var_edit.text(),
            }
            try:
                with open(preset_json, 'r+') as f:
                    presets = json.load(f)
                    if preset_name != 'api_key':
                        presets[preset_name] = preset
                    f.seek(0)
                    json.dump(presets, f)
                    f.truncate()
                self.preset_combo.currentIndexChanged.disconnect()
                self.preset_combo.addItem(preset_name)
                self.preset_combo.currentIndexChanged.connect(self.load_preset)
            except FileNotFoundError:
                with open(preset_json, 'w') as f:
                    json.dump({preset_name: preset}, f)
                self.preset_combo.currentIndexChanged.disconnect()
                self.preset_combo.addItem(preset_name)
                self.preset_combo.currentIndexChanged.connect(self.load_preset)

    def load_preset(self, index):
        if not hasattr(self, 'gpu_combo'):
            return
        preset_name = self.preset_combo.itemText(index)
        if not preset_name or not os.path.exists(preset_json):
            return
        with open(preset_json, 'r') as f:
            presets = json.load(f)
            if preset_name in presets and preset_name != 'api_key':
                preset = presets[preset_name]
                for i in range(self.gpu_combo.count()):
                    if self.gpu_combo.itemData(i)['id'] == preset['gpu_type_id']:
                        self.gpu_combo.setCurrentIndex(i)
                        break
                self.image_combo.setCurrentText(preset['image_name'])
                self.secure_radio.setChecked(preset['secure_radio'])
                self.community_radio.setChecked(preset['community_radio'])
                self.all_radio.setChecked(preset['all_radio'])
                self.spot_radio.setChecked(preset['spot'])
                self.on_demand_radio.setChecked(preset['on_demand'])
                self.os_disk_size_edit.setText(preset['os_disk_size_gb'])
                self.persistent_disk_size_edit.setText(preset['persistent_disk_size_gb'])
                self.http_port_edit.setText(preset['http_ports'])
                self.tcp_port_edit.setText(preset['tcp_ports'])
                self.env_var_edit.setText(preset['user_envs'])

    def load_presets(self):
        self.preset_combo.clear()
        self.preset_combo.addItem("")
        try:
            with open(preset_json, 'r') as f:
                presets = json.load(f)
                for preset_name in presets.keys():
                    self.preset_combo.addItem(preset_name)
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = GPUSelector()
    ex.show()

    sys.exit(app.exec_())

