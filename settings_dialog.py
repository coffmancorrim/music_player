from PySide6.QtWidgets import QCheckBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QLineEdit, QPushButton

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.music_dir_line_edit = QLineEdit(self)
        self.chooseDirButton = QPushButton("Choose...", self)
        self.chooseDirButton.clicked.connect(self.chooseMusicDir)

        self.auto_refresh_check_box = QCheckBox("Auto Refresh Directory", self)

        layout = QFormLayout()
        layout.addRow("Music Directory:", self.music_dir_line_edit)
        layout.addWidget(self.chooseDirButton)
        layout.addWidget(self.auto_refresh_check_box)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        self.setWindowTitle("Settings")

    def chooseMusicDir(self):
        dir = QFileDialog.getExistingDirectory(self, "Select Music Directory")
        if dir:
            self.music_dir_line_edit.setText(dir)