import sys
import os
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,QLineEdit, QPushButton, QLabel, QFileDialog, QListWidgetItem,QGroupBox, QTableWidget, QTableWidgetItem, QFrame, QMessageBox,QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont,QMovie
from PyQt5.QtWidgets import QHeaderView

from api_client import APIClient
from charts import MplCanvas, plot_type_distribution, plot_correlation_heatmap

BACKEND_URL = "http://127.0.0.1:8000"
POLL_INTERVAL_MS = 3000

APP_STYLE = """
QWidget { background: #f6f6f7; font-family: "Segoe UI", Arial, sans-serif; }
QLabel#title { font-size:20px; font-weight:700; color:#111; }
QGroupBox { border: 1px solid #e6e6e6; border-radius: 10px; padding: 12px; background: white; }
QPushButton.primary { background: #ffb300; color: #000; border-radius: 8px; padding: 8px 12px; font-weight:700; }
QPushButton.ghost { background: transparent; border: 2px solid #ffb300; color: #ffb300; border-radius: 18px; padding: 6px 10px; font-weight:700; }
QFrame.sidebar { background: #efefef; border-right: 1px solid #e0e0e0; }
QTableWidget { background: white; }
"""


def show_error(parent, title, msg):
    QMessageBox.critical(parent, title, str(msg))


class RegisterDialog(QWidget):
    def __init__(self, api: APIClient, on_success):
        super().__init__()
        self.api = api
        self.on_success = on_success
        self.setWindowTitle("Register")
        self.setFixedSize(520, 520)
        self.init_ui()

    def init_ui(self):
        v = QVBoxLayout()
        v.setAlignment(Qt.AlignTop)

        title = QLabel("Create an Account")
        title.setStyleSheet("font-size:22px; font-weight:700; color:#192a56;")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("Chemical Equipment Visualizer")
        subtitle.setStyleSheet("font-size:16px; font-weight:600;")
        subtitle.setAlignment(Qt.AlignCenter)

        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(20)

        
        self.user = QLineEdit(); self.user.setPlaceholderText("Username")
        self.pass1 = QLineEdit(); self.pass1.setPlaceholderText("Password"); self.pass1.setEchoMode(QLineEdit.Password)
        self.pass2 = QLineEdit(); self.pass2.setPlaceholderText("Confirm Password"); self.pass2.setEchoMode(QLineEdit.Password)

        v.addWidget(self.user)
        v.addWidget(self.pass1)
        v.addWidget(self.pass2)

        create = QPushButton("Register"); create.setProperty("class","primary")
        create.clicked.connect(self.do_register)

        back = QPushButton("Back to Login")
        back.clicked.connect(self.close)

        v.addWidget(create)
        v.addWidget(back)
        v.addStretch(1)

        self.setLayout(v)

    def do_register(self):
        u = self.user.text().strip()
        p1 = self.pass1.text().strip()
        p2 = self.pass2.text().strip()

        if p1 != p2:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        try:
            self.api.register(u, p1)
            QMessageBox.information(self, "Success", "Account created!")
            self.close()
        except Exception as e:
            show_error(self, "Register failed", e)


class LoginDialog(QWidget):
    def __init__(self, api: APIClient, on_success):
        super().__init__()
        self.api = api
        self.on_success = on_success
        self.reg_dialog = None    
        self.setWindowTitle("Login")
        self.setFixedSize(620, 520)
        self.init_ui()

    def init_ui(self):
        v = QVBoxLayout()
        v.setContentsMargins(40, 20, 40, 20)
        v.setSpacing(15)

        title1 = QLabel("FOSSEE Intern Screening")
        title1.setStyleSheet("font-size:28px; font-weight:800; color:#1a237e;")
        title1.setAlignment(Qt.AlignCenter)
        v.addWidget(title1)

        title2 = QLabel("Chemical Equipment Visualizer")
        title2.setStyleSheet("font-size:20px; font-weight:600;")
        title2.setAlignment(Qt.AlignCenter)
        v.addWidget(title2)

      
        gif_lbl = QLabel()
        movie = QMovie("assets/flask.gif")
        movie.setScaledSize(QSize(230, 230))
        gif_lbl.setMovie(movie)
        movie.start()
        v.addWidget(gif_lbl, alignment=Qt.AlignCenter)

       
        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pw = QLineEdit()
        self.pw.setPlaceholderText("Password")
        self.pw.setEchoMode(QLineEdit.Password)

        v.addWidget(self.user)
        v.addWidget(self.pw)

        # Buttons row
        btn_row = QHBoxLayout()

        login = QPushButton("Login")
        login.setProperty("class", "primary")
        login.clicked.connect(self.do_login)

        register = QPushButton("Register")
        register.clicked.connect(self.open_register)

        btn_row.addWidget(login)
        btn_row.addWidget(register)

        v.addLayout(btn_row)
        v.addStretch(1)

        self.setLayout(v)

    def open_register(self):
        

        self.reg_dialog = RegisterDialog(self.api, on_success=self.on_success)
        self.reg_dialog.setWindowModality(Qt.ApplicationModal)
        self.reg_dialog.show()

    def do_login(self):
        u = self.user.text().strip()
        p = self.pw.text().strip()

        try:
            data = self.api.login(u, p)
            if data.get("token"):
                self.api.set_token(data["token"])
                QMessageBox.information(self, "OK", "Logged in")
                self.on_success()
                self.close()
        except Exception as e:
            show_error(self, "Login failed", e)


class DashboardPane(QWidget):
    def __init__(self, api: APIClient):
        super().__init__()
        self.api = api
        self.selected_file = None
        self.init_ui()

    def init_ui(self):
        v = QVBoxLayout(); v.setContentsMargins(0,20,0,0); v.setSpacing(18)

        # Upload
        up = QGroupBox("Upload CSV"); h = QHBoxLayout()
        choose = QPushButton("⬆ CHOOSE FILE"); choose.setProperty("class","ghost"); choose.setFixedWidth(160)
        choose.clicked.connect(self.choose)
        self.file_lbl = QLabel("No file chosen"); self.file_lbl.setStyleSheet("color:#444")
        upload = QPushButton("Upload & Analyze"); upload.setProperty("class","primary"); upload.setFixedWidth(160)
        upload.clicked.connect(self.do_upload)
        h.addWidget(choose); h.addWidget(self.file_lbl,1); h.addWidget(upload)
        up.setLayout(h)
        v.addWidget(up)

        # Stats
        stats = QHBoxLayout()
        def mk(title):
            gb = QGroupBox(); inner = QVBoxLayout()
            t = QLabel(title); t.setStyleSheet("font-weight:600;")
            val = QLabel("-"); val.setStyleSheet("font-size:22px; font-weight:700;")
            inner.addWidget(t); inner.addWidget(val); inner.addStretch(1)
            gb.setLayout(inner); gb.setFixedHeight(100)
            return gb,val
        self.c_total, self.v_total = mk("Total Equipment")
        self.c_flow, self.v_flow = mk("Avg Flowrate")
        self.c_press, self.v_press = mk("Avg Pressure")
        self.c_temp, self.v_temp = mk("Avg Temperature")
        stats.addWidget(self.c_total); stats.addWidget(self.c_flow); stats.addWidget(self.c_press); stats.addWidget(self.c_temp)
        v.addLayout(stats)

        # Charts
        charts = QHBoxLayout()
        self.pie = MplCanvas(width=5,height=3)
        self.heat = MplCanvas(width=4,height=3)
        charts.addWidget(self.pie,2); charts.addWidget(self.heat,1)
        v.addLayout(charts)

        # Bottom analytics
        bottom = QHBoxLayout()
        self.grp_type = QGroupBox("Type-wise Averages"); tlay = QVBoxLayout()
        self.tbl_type = QTableWidget(0,4)
        self.tbl_type.setHorizontalHeaderLabels(["Type","Avg Flowrate","Avg Pressure","Avg Temp"])
        self.tbl_type.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tlay.addWidget(self.tbl_type); self.grp_type.setLayout(tlay)
        bottom.addWidget(self.grp_type,1)

        self.grp_out = QGroupBox("Outliers"); olay = QVBoxLayout()
        self.lbl_out = QLabel("No outliers detected.")
        self.lbl_out.setWordWrap(True)
        olay.addWidget(self.lbl_out); self.grp_out.setLayout(olay)
        bottom.addWidget(self.grp_out,1)
        v.addLayout(bottom)

        self.setLayout(v)

    def choose(self):
        p,_ = QFileDialog.getOpenFileName(self,"Select CSV","","CSV files (*.csv)")
        if p:
            self.selected_file = p
            self.file_lbl.setText(os.path.basename(p))

    def do_upload(self):
        if not self.selected_file:
            QMessageBox.warning(self,"No file","Select CSV first.")
            return
        try:
            self.api.upload_csv(self.selected_file)
            QMessageBox.information(self,"OK","Uploaded & analyzed.")
            self.refresh_all()
            self.selected_file=None; self.file_lbl.setText("No file chosen")
        except Exception as e:
            show_error(self,"Upload failed",e)

    def refresh_all(self):
        try:
            s = self.api.get_summary()
        except Exception as e:
            print("refresh_all error",e); return
        self.v_total.setText(str(s.get("total_equipment","-")))
        self.v_flow.setText(f"{s.get('avg_flowrate',0):.2f}")
        self.v_press.setText(f"{s.get('avg_pressure',0):.2f}")
        self.v_temp.setText(f"{s.get('avg_temperature',0):.2f}")

        plot_type_distribution(self.pie,s.get("type_distribution",{}))
        plot_correlation_heatmap(self.heat,s.get("correlation",{}))

        # type table
        self.tbl_type.setRowCount(0)
        tw = s.get("typewise_averages",{})
        for k,v in tw.items():
            r = self.tbl_type.rowCount(); self.tbl_type.insertRow(r)
            self.tbl_type.setItem(r,0,QTableWidgetItem(str(k)))
            self.tbl_type.setItem(r,1,QTableWidgetItem(str(v.get("Flowrate",v.get("flowrate","-")))))
            self.tbl_type.setItem(r,2,QTableWidgetItem(str(v.get("Pressure",v.get("pressure","-")))))
            self.tbl_type.setItem(r,3,QTableWidgetItem(str(v.get("Temperature",v.get("temperature","-")))))

        # outliers
        outs = s.get("outliers",[])
        if not outs:
            self.lbl_out.setText("No outliers detected.")
        else:
            t=""
            for o in outs:
                n = o.get("EquipmentName") or o.get("Name") or "Unknown"
                t += f"{n}: Flow {o.get('Flowrate')} | Pressure {o.get('Pressure')} | Temp {o.get('Temperature')}\n"
            self.lbl_out.setText(t)


class HistoryPane(QWidget):
    def __init__(self, api: APIClient):
        super().__init__()
        self.api = api
        self.init_ui()

    def init_ui(self):
        v = QVBoxLayout(); v.setContentsMargins(0,10,0,0); v.setSpacing(10)

        title = QLabel("Upload History (Last 5)")
        title.setStyleSheet("font-weight:700; font-size:16px;")
        v.addWidget(title)

        # scroll area for cards
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.card_wrap = QWidget()
        self.card_layout = QVBoxLayout(); self.card_layout.setSpacing(14)
        self.card_wrap.setLayout(self.card_layout)
        self.scroll.setWidget(self.card_wrap)
        v.addWidget(self.scroll)

        # preview
        self.preview_title = QLabel("Select an item to view details")
        self.preview_title.setStyleSheet("font-weight:600; margin-top:15px;")
        v.addWidget(self.preview_title)
         

        self.table = QTableWidget()
        table_wrap = QHBoxLayout()
        table_wrap.addStretch(1)
        table_wrap.addWidget(self.table,3)
        table_wrap.addStretch(1)
        v.addWidget(self.table)

        self.setLayout(v)
        self.refresh_list()

    # Build web-style card
    def build_card(self, item):
        box = QGroupBox(); box.setStyleSheet("""
            QGroupBox {
                background:white;
                border-radius:10px;
                border:1px solid #e6e6e6;
                padding:12px;
            }
        """)
        v = QVBoxLayout()

        # header
        fn = QLabel(item.get("filename","file")); fn.setStyleSheet("font-weight:700; font-size:14px;")
        dt = QLabel(item.get("uploaded","")); dt.setAlignment(Qt.AlignRight)
        h = QHBoxLayout()
        h.addWidget(fn); h.addWidget(dt)
        v.addLayout(h)

        # summary
        s = item.get("summary",{})
        sm = QLabel(
            f"<b>Total:</b> {s.get('total_equipment')}  |  "
            f"<b>Avg Flow:</b> {s.get('avg_flowrate'):.2f}  |  "
            f"<b>Avg Pressure:</b> {s.get('avg_pressure'):.2f}  |  "
            f"<b>Avg Temp:</b> {s.get('avg_temperature'):.2f}"
        )
        v.addWidget(sm)

        # distribution bar
        dist = s.get("type_distribution",{})
        pal = ["#26a69a","#42a5f5","#ef5350","#8e24aa","#fb8c00","#8d6e63","#5c6bc0"]
        hb = QHBoxLayout()
        for i,(k,val) in enumerate(dist.items()):
            seg = QLabel(f"  {k} — {val}  ")
            seg.setStyleSheet(f"background:{pal[i%len(pal)]}; color:white; padding:6px 10px; border-radius:6px; font-weight:600;")
            hb.addWidget(seg)
        v.addLayout(hb)

        # view button
        btn = QPushButton("View original data"); btn.setProperty("class","ghost")
        btn.clicked.connect(lambda: self.load_preview(item))
        v.addWidget(btn)

        box.setLayout(v)
        return box

    def refresh_list(self):
        while self.card_layout.count():
            c = self.card_layout.takeAt(0)
            w = c.widget()
            if w: w.deleteLater()

        try:
            arr = self.api.get_history()
        except Exception as e:
            print("history load error",e); return

        for it in arr:
            card = self.build_card(it)
            self.card_layout.addWidget(card)

    def load_preview(self, item):
        try:
            d = self.api.get_dataset_rows(item["id"])
        except Exception as e:
            show_error(self,"Load failed",e); return

        cols = d.get("columns",[]); rows = d.get("rows",[])
        self.preview_title.setText(f"Dataset Preview — {item.get('filename')}")

        self.table.setColumnCount(len(cols))
        self.table.setRowCount(len(rows))
        self.table.setHorizontalHeaderLabels(cols)
        for r,row in enumerate(rows):
            for c,col in enumerate(cols):
                self.table.setItem(r,c,QTableWidgetItem(str(row.get(col,""))))
        self.table.resizeColumnsToContents()


class MainWindow(QMainWindow):
    def __init__(self, api: APIClient):
        super().__init__()
        self.api = api
        self.setWindowTitle("Chemical Equipment Visualizer (Desktop)")
        self.resize(1200,820)
        self.init_ui()
        self.poll = QTimer(self); self.poll.setInterval(POLL_INTERVAL_MS)
        self.poll.timeout.connect(self.sync)
        self.poll.start()

    def init_ui(self):
        central = QWidget(); central.setStyleSheet(APP_STYLE)
        main = QHBoxLayout(); central.setLayout(main)

        # Sidebar
        side = QFrame(); side.setProperty("class","sidebar"); side.setFixedWidth(200)
        sb = QVBoxLayout(); sb.setContentsMargins(12,12,12,12)
        t = QLabel("Chemical Equipment\nVisualizer"); t.setWordWrap(True); t.setStyleSheet("font-weight:700;")
        sb.addWidget(t); sb.addSpacing(10)
        self.btn_dash = QPushButton("Dashboard"); self.btn_dash.clicked.connect(lambda:self.switch("dash"))
        self.btn_hist = QPushButton("History"); self.btn_hist.clicked.connect(lambda:self.switch("hist"))
        sb.addWidget(self.btn_dash); sb.addWidget(self.btn_hist); sb.addStretch(1)
        logout = QPushButton("Logout"); logout.clicked.connect(self.logout)
        sb.addWidget(logout)
        side.setLayout(sb)
        main.addWidget(side)

        # Right side
        right = QVBoxLayout()
        top = QHBoxLayout()
        ref = QPushButton("Refresh"); ref.clicked.connect(self.refresh_all); ref.setFixedWidth(90)
        top.addWidget(ref); top.addStretch(1)
        title = QLabel("Chemical Equipment Parameter Visualizer"); title.setStyleSheet("font-weight:700; font-size:16px;")
        top.addWidget(title); top.addStretch(1)
        self.btn_pdf = QPushButton("Download PDF (Latest)"); self.btn_pdf.setProperty("class","primary"); self.btn_pdf.setFixedWidth(180)
        self.btn_pdf.clicked.connect(self.download_pdf)
        top.addWidget(self.btn_pdf)
        right.addLayout(top)

        self.pane_dash = DashboardPane(self.api)
        self.pane_hist = HistoryPane(self.api)
        right.addWidget(self.pane_dash)
        right.addWidget(self.pane_hist)
        self.pane_hist.hide()

        main.addLayout(right,1)
        self.setCentralWidget(central)
        self.refresh_all()

    def switch(self,mode):
        if mode=="dash":
            self.pane_hist.hide(); self.pane_dash.show(); self.btn_pdf.show()
        else:
            self.pane_dash.hide(); self.pane_hist.show(); self.btn_pdf.hide()

    def refresh_all(self):
        try:
            self.pane_dash.refresh_all()
        except Exception as e:
            print("dash refresh",e)
        try:
            self.pane_hist.refresh_list()
        except Exception as e:
            print("hist refresh",e)

    def sync(self): self.refresh_all()

    def download_pdf(self):
        try:
            h = self.api.get_history()
            if not h:
                QMessageBox.warning(self,"No data","No dataset available."); return
            did = h[0]["id"]
            tmp = tempfile.NamedTemporaryFile(delete=False,suffix=".pdf"); tmp.close()
            self.api.download_pdf(did,tmp.name)
            QMessageBox.information(self,"Saved",f"Saved report to {tmp.name}")
        except Exception as e:
            show_error(self,"Download failed",e)

    def logout(self):
        self.api.set_token(None)
        QMessageBox.information(self,"Logged out","You have been logged out.")
        self.open_login()

    def open_login(self):
        l = LoginDialog(self.api,on_success=self.refresh_all)
        l.setWindowModality(Qt.ApplicationModal)
        l.show()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    api = APIClient(BACKEND_URL)

    main_win = MainWindow(api)
    main_win.hide() 

    def on_login_success():
        main_win.refresh_all()
        main_win.show()

        screen = app.primaryScreen().availableGeometry()
        w = main_win.frameGeometry()
        main_win.move(
            (screen.width() - w.width()) // 2,
            (screen.height() - w.height()) // 2
        )


    login = LoginDialog(api, on_success=on_login_success)
    login.setWindowModality(Qt.ApplicationModal)
    login.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
