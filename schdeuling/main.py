"""
main.py — Scheduling Demo UI  (PyQt5 / PySide6 compatible)

Install:
    pip install PyQt5
  or
    pip install PySide6

Run:
    python main.py
"""

import sys

# ── Qt compatibility shim (works with PyQt5 or PySide6) ────────────────────
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget,
        QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
        QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
        QTableWidget, QTableWidgetItem, QHeaderView,
        QMessageBox, QGroupBox, QFrame, QSizePolicy, QScrollArea,
        QListWidget, QStackedWidget
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont, QColor, QPalette
except ImportError:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QTabWidget,
        QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
        QLabel, QPushButton, QLineEdit, QComboBox, QCheckBox,
        QTableWidget, QTableWidgetItem, QHeaderView,
        QMessageBox, QGroupBox, QFrame, QSizePolicy, QScrollArea,
        QListWidget, QStackedWidget
    )
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QColor, QPalette

from models import Store, ACCOUNT_TYPES, DAYS

# ── Global store (shared across all tabs) ──────────────────────────────────
store = Store()


# ── Palette / Style ────────────────────────────────────────────────────────
STYLE = """
QMainWindow, QWidget {
    background-color: #0f111a;
    color: #f1f5f9;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    font-size: 15px;
}

/* Sidebar Styling */
QListWidget#Sidebar {
    background-color: #161925;
    border: none;
    border-right: 1px solid #22263d;
    padding: 15px 10px;
}
QListWidget#Sidebar::item {
    padding: 14px 18px;
    margin-bottom: 8px;
    border-radius: 8px;
    color: #94a3b8;
    font-weight: 600;
}
QListWidget#Sidebar::item:hover {
    background-color: #1e2238;
    color: #cbd5e1;
}
QListWidget#Sidebar::item:selected {
    background-color: #3b5bdb;
    color: #ffffff;
}

/* Content Container */
QStackedWidget#MainContent {
    background-color: #121420;
    padding: 10px;
}

/* Form Container Sections */
QGroupBox {
    border: 1px solid #22263d;
    border-radius: 12px;
    margin-top: 20px;
    padding: 24px;
    font-weight: 700;
    font-size: 16px;
    color: #8f9df7;
    background-color: #161925;
}
QGroupBox::title {
    subcontext-origin: margin;
    left: 16px;
    padding: 0 8px;
}

/* Controls */
QLineEdit, QComboBox {
    background: #1e2238;
    border: 1px solid #2e3456;
    border-radius: 8px;
    padding: 10px 14px;
    color: #f1f5f9;
    min-height: 40px;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus {
    border: 2px solid #3b5bdb;
    background: #232742;
}
QComboBox::drop-down {
    border: none;
    padding-right: 12px;
}
QComboBox QAbstractItemView {
    background: #161925;
    border: 1px solid #2e3456;
    selection-background-color: #3b5bdb;
    color: #f1f5f9;
    padding: 8px;
}

/* Buttons */
QPushButton {
    background: #3b5bdb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 700;
    font-size: 14px;
    min-height: 42px;
}
QPushButton:hover { background: #4c6ef5; }
QPushButton:pressed { background: #2f4fc4; }

QPushButton.danger {
    background: #e11d48;
}
QPushButton.danger:hover { background: #f43f5e; }
QPushButton.danger:pressed { background: #be123c; }

QPushButton.secondary {
    background: #22263d;
    color: #94a3b8;
    border: 1px solid #2e3456;
}
QPushButton.secondary:hover { background: #2b304c; color: #f1f5f9; }

/* Data Tables */
QTableWidget {
    background: #161925;
    border: 1px solid #22263d;
    border-radius: 10px;
    gridline-color: #1e2238;
    color: #e2e8f0;
    padding: 5px;
    outline: none;
}
QTableWidget::item {
    padding: 12px;
}
/* Fixed Selection: Keeps dark background, forces crisp text, adds an outline border */
QTableWidget::item:selected {
    background-color: #161925; 
    color: #ffffff;
    border: 1px solid #3b5bdb;
}
QHeaderView::section {
    background: #1e2238;
    color: #8f9df7;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #22263d;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.03em;
}

/* Typography elements */
QLabel.hint {
    color: #64748b;
    font-size: 13px;
    font-style: italic;
    margin-top: 4px;
}
QLabel.title {
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
}
QLabel.subtitle {
    font-size: 14px;
    color: #94a3b8;
}
QFrame.divider {
    background: #22263d;
    max-height: 1px;
    min-height: 1px;
    margin: 8px 0;
}
"""


# ── Helpers ────────────────────────────────────────────────────────────────

def make_label(text, cls=None):
    lbl = QLabel(text)
    if cls:
        lbl.setProperty("class", cls)
    return lbl


def alert(parent, title, msg, kind="info"):
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(msg)
    box.setStyleSheet("color: #e2e8f0; font-size: 14px;")
    if kind == "error":
        box.setIcon(QMessageBox.Critical)
    elif kind == "warn":
        box.setIcon(QMessageBox.Warning)
    else:
        box.setIcon(QMessageBox.Information)
    box.exec_()


def combo(options, placeholder="Select…"):
    c = QComboBox()
    c.addItem(placeholder)
    c.addItems(options)
    return c


# ── Tab 1: Manage Teachers ──────────────────────────────────────────────────

class TeacherTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(20)

        # Header
        layout.addWidget(make_label("👩‍🏫  Teacher Management", "title"))
        layout.addWidget(make_label("Add teachers who will be part of the schedule.", "subtitle"))

        divider = QFrame()
        divider.setProperty("class", "divider")
        layout.addWidget(divider)

        # Add teacher form
        grp = QGroupBox("Add New Teacher")
        form = QFormLayout(grp)
        form.setVerticalSpacing(14)
        form.setHorizontalSpacing(20)
        
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. jason")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Jason Cruz")
        form.addRow("Teacher ID:", self.id_input)
        form.addRow("Full Name:", self.name_input)

        btn = QPushButton("➕  Add Teacher")
        btn.clicked.connect(self.add_teacher)
        form.addRow("", btn)
        layout.addWidget(grp)

        # Teacher list
        grp2 = QGroupBox("Registered Teachers")
        v = QVBoxLayout(grp2)
        v.setContentsMargins(16, 20, 16, 16)
        
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Teacher ID", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        v.addWidget(self.table)
        layout.addWidget(grp2)

        layout.addStretch()
        self.refresh_table()

    def add_teacher(self):
        tid = self.id_input.text().strip()
        name = self.name_input.text().strip()
        if not tid or not name:
            alert(self, "Missing Info", "Please fill in both Teacher ID and Name.", "warn")
            return
        store.add_teacher(tid, name)
        self.id_input.clear()
        self.name_input.clear()
        self.refresh_table()
        alert(self, "Done", f"Teacher '{name}' added.")

    def refresh_table(self):
        teachers = store.get_teachers()
        self.table.setRowCount(len(teachers))
        for i, t in enumerate(teachers):
            self.table.setItem(i, 0, QTableWidgetItem(t.teacher_id))
            self.table.setItem(i, 1, QTableWidgetItem(t.name))


# ── Tab 2: Teacher Availability ─────────────────────────────────────────────

class AvailabilityTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(20)

        layout.addWidget(make_label("📅  Teacher Availability", "title"))
        layout.addWidget(make_label(
            "Teachers mark their free time slots for the next 3 days.",
            "subtitle"))

        divider = QFrame()
        divider.setProperty("class", "divider")
        layout.addWidget(divider)

        grp = QGroupBox("Mark Availability")
        form = QFormLayout(grp)
        form.setVerticalSpacing(14)
        form.setHorizontalSpacing(20)

        self.teacher_cb = QComboBox()
        self.day_cb = combo(DAYS)
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g. 9-12  or  10-11")
        hint = make_label("Ranges like '9-12' auto-expand to 9-10, 10-11, 11-12 slots.", "hint")

        form.addRow("Teacher:", self.teacher_cb)
        form.addRow("Day:", self.day_cb)
        form.addRow("Time Range:", self.time_input)
        form.addRow("", hint)

        btn = QPushButton("✅  Save Availability")
        btn.clicked.connect(self.save)
        form.addRow("", btn)
        layout.addWidget(grp)

        grp2 = QGroupBox("Current Availability Slots")
        v = QVBoxLayout(grp2)
        v.setContentsMargins(16, 20, 16, 16)
        
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Teacher", "Day", "Time", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        v.addWidget(self.table)
        layout.addWidget(grp2)

        self.refresh()

    def showEvent(self, e):
        super().showEvent(e)
        self.refresh_teachers()

    def refresh_teachers(self):
        current = self.teacher_cb.currentText()
        self.teacher_cb.clear()
        for t in store.get_teachers():
            self.teacher_cb.addItem(t.name, t.teacher_id)
        # restore selection
        idx = self.teacher_cb.findText(current)
        if idx >= 0:
            self.teacher_cb.setCurrentIndex(idx)

    def save(self):
        idx = self.teacher_cb.currentIndex()
        if idx < 0:
            alert(self, "Error", "No teacher selected.", "warn")
            return
        tid = self.teacher_cb.itemData(idx)
        day = self.day_cb.currentText()
        if day not in DAYS:
            alert(self, "Error", "Please select a valid day.", "warn")
            return
        time_str = self.time_input.text().strip()
        try:
            created = store.add_availability(tid, day, time_str)
            self.time_input.clear()
            self.refresh()
            alert(self, "Saved", f"{len(created)} slot(s) added for {day}.")
        except ValueError as e:
            alert(self, "Error", str(e), "error")

    def refresh(self):
        slots = [s for s in store.get_schedule() if s.account_type is None or True]
        all_slots = store.get_schedule()
        self.table.setRowCount(len(all_slots))
        for i, s in enumerate(all_slots):
            self.table.setItem(i, 0, QTableWidgetItem(s.teacher_id))
            self.table.setItem(i, 1, QTableWidgetItem(s.day))
            self.table.setItem(i, 2, QTableWidgetItem(s.time))

            status = "Free" if s.account_type is None else f"Assigned ({s.account_type})"
            status_item = QTableWidgetItem(status)
            if s.account_type is None:
                status_item.setForeground(QColor("#10b981"))
            else:
                status_item.setForeground(QColor("#f59e0b"))
            self.table.setItem(i, 3, status_item)

            if s.account_type is None:
                del_btn = QPushButton("Remove")
                del_btn.setProperty("class", "danger")
                del_btn.setMinimumHeight(30)
                del_btn.clicked.connect(lambda checked, slot=s: self.remove_slot(slot))
                self.table.setCellWidget(i, 4, del_btn)
            else:
                self.table.setCellWidget(i, 4, None)

    def remove_slot(self, slot):
        try:
            store.remove_availability(slot.teacher_id, slot.day, slot.time)
            self.refresh()
        except ValueError as e:
            alert(self, "Error", str(e), "error")


# ── Tab 3: Admin — Assign Classes ───────────────────────────────────────────

class AdminTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(20)

        layout.addWidget(make_label("🛠  Admin — Assign Classes", "title"))
        layout.addWidget(make_label(
            "Assign class types to available teachers. Only available teachers appear.",
            "subtitle"))

        divider = QFrame()
        divider.setProperty("class", "divider")
        layout.addWidget(divider)

        # Filter row
        grp_filter = QGroupBox("Find Available Teachers")
        hform = QFormLayout(grp_filter)
        hform.setVerticalSpacing(14)
        hform.setHorizontalSpacing(20)
        
        self.day_cb = combo(DAYS)
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("e.g. 10-11")
        search_btn = QPushButton("🔍  Search")
        search_btn.clicked.connect(self.search)

        hbox = QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addWidget(self.time_input)
        hbox.addWidget(search_btn)
        hform.addRow("Day:", self.day_cb)
        hform.addRow("Time Slot:", hbox)
        layout.addWidget(grp_filter)

        # Results + assign
        grp_result = QGroupBox("Available Teachers")
        vr = QVBoxLayout(grp_result)
        vr.setContentsMargins(16, 20, 16, 16)
        
        self.avail_table = QTableWidget(0, 2)
        self.avail_table.setHorizontalHeaderLabels(["Teacher ID", "Name"])
        self.avail_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.avail_table.verticalHeader().setDefaultSectionSize(44)
        self.avail_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.avail_table.setSelectionBehavior(QTableWidget.SelectRows)
        vr.addWidget(self.avail_table)
        layout.addWidget(grp_result)

        grp_assign = QGroupBox("Assign Class")
        aform = QFormLayout(grp_assign)
        aform.setVerticalSpacing(14)
        aform.setHorizontalSpacing(20)
        
        self.acct_cb = combo(ACCOUNT_TYPES, "Select class type…")
        assign_btn = QPushButton("📌  Assign Class to Selected Teacher")
        assign_btn.clicked.connect(self.assign)

        aform.addRow("Class Type:", self.acct_cb)
        aform.addRow("", assign_btn)
        layout.addWidget(grp_assign)

        layout.addStretch()

    def search(self):
        day = self.day_cb.currentText()
        if day not in DAYS:
            alert(self, "Error", "Select a valid day.", "warn")
            return
        time_str = self.time_input.text().strip()
        try:
            teachers = store.get_available_teachers(day, time_str)
        except ValueError as e:
            alert(self, "Error", str(e), "error")
            return
        self.avail_table.setRowCount(len(teachers))
        for i, t in enumerate(teachers):
            self.avail_table.setItem(i, 0, QTableWidgetItem(t.teacher_id))
            self.avail_table.setItem(i, 1, QTableWidgetItem(t.name))

        if not teachers:
            alert(self, "No Results", f"No teachers available on {day} at {time_str}.", "warn")

    def assign(self):
        row = self.avail_table.currentRow()
        if row < 0:
            alert(self, "Select Teacher", "Click a teacher in the results table first.", "warn")
            return
        teacher_id = self.avail_table.item(row, 0).text()
        day = self.day_cb.currentText()
        time_str = self.time_input.text().strip()
        acct_idx = self.acct_cb.currentIndex()
        if acct_idx == 0:
            alert(self, "Select Type", "Please select a class type.", "warn")
            return
        account_type = self.acct_cb.currentText()
        try:
            slot = store.assign_class(teacher_id, day, time_str, account_type)
            alert(self, "Assigned", f"✅ {teacher_id} assigned to {account_type} on {day} {slot.time}.")
            self.search()
        except ValueError as e:
            alert(self, "Error", str(e), "error")


# ── Tab 4: Schedule View ────────────────────────────────────────────────────

class ScheduleViewTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 24, 30, 24)
        layout.setSpacing(20)

        layout.addWidget(make_label("📋  Full Schedule", "title"))
        layout.addWidget(make_label("Filter by day or teacher, or view everything.", "subtitle"))

        divider = QFrame()
        divider.setProperty("class", "divider")
        layout.addWidget(divider)

        # Filter bar
        fbar = QHBoxLayout()
        fbar.setSpacing(12)
        self.day_cb = combo(["all"] + DAYS, "Filter by day…")
        self.teacher_cb = QComboBox()
        refresh_btn = QPushButton("🔄  Refresh")
        refresh_btn.setProperty("class", "secondary")
        refresh_btn.clicked.connect(self.refresh)
        
        fbar.addWidget(QLabel("Day:"))
        fbar.addWidget(self.day_cb)
        fbar.addSpacing(10)
        fbar.addWidget(QLabel("Teacher:"))
        fbar.addWidget(self.teacher_cb)
        fbar.addSpacing(10)
        fbar.addWidget(refresh_btn)
        fbar.addStretch()
        layout.addLayout(fbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Teacher", "Day", "Time", "Class Type", "Status", "Rest?"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(44)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.refresh()

    def showEvent(self, e):
        super().showEvent(e)
        self.refresh_teacher_filter()

    def refresh_teacher_filter(self):
        current = self.teacher_cb.currentText()
        self.teacher_cb.clear()
        self.sidebar_all_item = "All"
        self.teacher_cb.addItem(self.sidebar_all_item)
        for t in store.get_teachers():
            self.teacher_cb.addItem(t.teacher_id)
        idx = self.teacher_cb.findText(current)
        if idx >= 0:
            self.teacher_cb.setCurrentIndex(idx)

    def refresh(self):
        self.refresh_teacher_filter()
        day_text = self.day_cb.currentText()
        day = None if day_text in ("Filter by day…", "all") else day_text
        teacher_text = self.teacher_cb.currentText()
        teacher = None if teacher_text == "All" else teacher_text

        slots = store.get_schedule(day=day, teacher_id=teacher)
        self.table.setRowCount(len(slots))
        for i, s in enumerate(slots):
            self.table.setItem(i, 0, QTableWidgetItem(s.teacher_id))
            self.table.setItem(i, 1, QTableWidgetItem(s.day))
            self.table.setItem(i, 2, QTableWidgetItem(s.time))

            acct = s.account_type or "—"
            self.table.setItem(i, 3, QTableWidgetItem(acct))

            if s.account_type is None:
                status_item = QTableWidgetItem("Free")
                status_item.setForeground(QColor("#10b981"))
            else:
                status_item = QTableWidgetItem("Assigned")
                status_item.setForeground(QColor("#f59e0b"))
            self.table.setItem(i, 4, status_item)

            rest_item = QTableWidgetItem("✓" if s.is_rest else "")
            rest_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, rest_item)


# ── Main Window ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📆 Class Scheduling Management")
        self.setMinimumSize(1150, 750)

        central = QWidget()
        self.setCentralWidget(central)
        
        master_layout = QHBoxLayout(central)
        master_layout.setContentsMargins(0, 0, 0, 0)
        master_layout.setSpacing(0)

        # Navigation Sidebar UI
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        
        self.sidebar.addItems([
            "👩‍🏫  Teachers",
            "📅  Availability",
            "🛠  Admin Assign",
            "📋  Schedule View"
        ])
        
        self.container = QStackedWidget()
        self.container.setObjectName("MainContent")

        self.teacher_tab = TeacherTab()
        self.avail_tab = AvailabilityTab()
        self.admin_tab = AdminTab()
        self.view_tab = ScheduleViewTab()

        self.container.addWidget(self.teacher_tab)
        self.container.addWidget(self.avail_tab)
        self.container.addWidget(self.admin_tab)
        self.container.addWidget(self.view_tab)

        master_layout.addWidget(self.sidebar)
        master_layout.addWidget(self.container)

        self.sidebar.currentRowChanged.connect(self.on_nav_change)
        self.sidebar.setCurrentRow(0)

    def on_nav_change(self, idx):
        self.container.setCurrentIndex(idx)
        tab = self.container.widget(idx)
        if hasattr(tab, "refresh_teachers"):
            tab.refresh_teachers()
        if hasattr(tab, "refresh"):
            tab.refresh()


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec() if hasattr(app, "exec") else app.exec_())