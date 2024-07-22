import wx
import serial
import time
import threading

class CNCFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super(CNCFrame, self).__init__(*args, **kw)
        self.init_ui()
        self.serial_connection = None

    def init_ui(self):
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Port and Status
        port_sizer = wx.BoxSizer(wx.HORIZONTAL)
        port_label = wx.StaticText(panel, label="ComPort:")
        self.port_text = wx.TextCtrl(panel, value="COM3")
        connect_button = wx.Button(panel, label="Connect")
        connect_button.Bind(wx.EVT_BUTTON, self.on_connect)
        self.status_label = wx.StaticText(panel, label="Status: Not connected")

        port_sizer.Add(port_label, 0, wx.ALL | wx.CENTER, 5)
        port_sizer.Add(self.port_text, 1, wx.ALL | wx.CENTER, 5)
        port_sizer.Add(connect_button, 0, wx.ALL | wx.CENTER, 5)
        port_sizer.Add(self.status_label, 0, wx.ALL | wx.CENTER, 5)
        left_sizer.Add(port_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Add manual control buttons
        manual_drive_sizer = wx.GridSizer(3, 3, 5, 5)
        self.btn_up = wx.Button(panel, label="Y↑")
        self.btn_down = wx.Button(panel, label="Y↓")
        self.btn_left = wx.Button(panel, label="←X")
        self.btn_right = wx.Button(panel, label="X→")
        self.btn_z_up = wx.Button(panel, label="↑Z")
        self.btn_z_down = wx.Button(panel, label="↓Z")

        self.btn_up.Bind(wx.EVT_BUTTON, self.on_move_up)
        self.btn_down.Bind(wx.EVT_BUTTON, self.on_move_down)
        self.btn_left.Bind(wx.EVT_BUTTON, self.on_move_left)
        self.btn_right.Bind(wx.EVT_BUTTON, self.on_move_right)
        self.btn_z_up.Bind(wx.EVT_BUTTON, self.on_move_z_up)
        self.btn_z_down.Bind(wx.EVT_BUTTON, self.on_move_z_down)

        manual_drive_sizer.Add(wx.StaticText(panel), 0, wx.ALL, 5)
        manual_drive_sizer.Add(self.btn_up, 0, wx.ALL, 5)
        manual_drive_sizer.Add(wx.StaticText(panel), 0, wx.ALL, 5)
        manual_drive_sizer.Add(self.btn_left, 0, wx.ALL, 5)
        manual_drive_sizer.Add(wx.StaticText(panel, label="XYZ"), 0, wx.ALL, 5)
        manual_drive_sizer.Add(self.btn_right, 0, wx.ALL, 5)
        manual_drive_sizer.Add(wx.StaticText(panel), 0, wx.ALL, 5)
        manual_drive_sizer.Add(self.btn_down, 0, wx.ALL, 5)
        manual_drive_sizer.Add(wx.StaticText(panel), 0, wx.ALL, 5)
        right_sizer.Add(manual_drive_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Add Z control buttons
        z_control_sizer = wx.BoxSizer(wx.HORIZONTAL)
        z_control_sizer.Add(self.btn_z_up, 1, wx.EXPAND | wx.ALL, 5)
        z_control_sizer.Add(self.btn_z_down, 1, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(z_control_sizer, 0, wx.EXPAND | wx.ALL, 5)

        # Add other controls (calibration, volume, etc.)
        self.calibration_btn = wx.Button(panel, label="Calibrar")
        self.calibration_btn.Bind(wx.EVT_BUTTON, self.on_calibrate)
        right_sizer.Add(self.calibration_btn, 0, wx.EXPAND | wx.ALL, 5)

        volume_time_sizer = wx.GridSizer(2, 2, 5, 5)
        self.volume_text = wx.TextCtrl(panel)
        self.time_text = wx.TextCtrl(panel)
        self.set_params_btn = wx.Button(panel, label="Establecer Parámetros")
        self.set_params_btn.Bind(wx.EVT_BUTTON, self.on_set_params)

        volume_time_sizer.Add(wx.StaticText(panel, label="Volumen[mm]:"), 0, wx.ALL, 5)
        volume_time_sizer.Add(self.volume_text, 1, wx.EXPAND | wx.ALL, 5)
        volume_time_sizer.Add(wx.StaticText(panel, label="Tiempo[s]:"), 0, wx.ALL, 5)
        volume_time_sizer.Add(self.time_text, 1, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(volume_time_sizer, 0, wx.EXPAND | wx.ALL, 5)
        right_sizer.Add(self.set_params_btn, 0, wx.EXPAND | wx.ALL, 5)

        # Add position text controls
        self.x_text = wx.TextCtrl(panel, value="0.00", style=wx.TE_RIGHT)
        self.y_text = wx.TextCtrl(panel, value="0.00", style=wx.TE_RIGHT)
        self.z_text = wx.TextCtrl(panel, value="0.00", style=wx.TE_RIGHT)
        left_sizer.Add(wx.StaticText(panel, label="Posición X:"), 0, wx.ALL, 5)
        left_sizer.Add(self.x_text, 0, wx.ALL | wx.EXPAND, 5)
        left_sizer.Add(wx.StaticText(panel, label="Posición Y:"), 0, wx.ALL, 5)
        left_sizer.Add(self.y_text, 0, wx.ALL | wx.EXPAND, 5)
        left_sizer.Add(wx.StaticText(panel, label="Posición Z:"), 0, wx.ALL, 5)
        left_sizer.Add(self.z_text, 0, wx.ALL | wx.EXPAND, 5)

        main_sizer.Add(left_sizer, 0, wx.ALL, 5)
        main_sizer.Add(right_sizer, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(main_sizer)

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.SetTitle('CNC Control')
        self.Centre()

    def on_connect(self, event):
        port = self.port_text.GetValue()
        try:
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            self.status_label.SetLabel("Status: Connected")
            wx.MessageBox("Conexión exitosa.", "Info", wx.OK | wx.ICON_INFORMATION)
            threading.Thread(target=self.read_serial_data, daemon=True).start()
        except serial.SerialException:
            wx.MessageBox("Error de conexión.", "Error", wx.OK | wx.ICON_ERROR)
            self.status_label.SetLabel("Status: Not connected")

    def on_move_up(self, event):
        self.update_position('Y', 1)

    def on_move_down(self, event):
        self.update_position('Y', -1)

    def on_move_left(self, event):
        self.update_position('X', -1)

    def on_move_right(self, event):
        self.update_position('X', 1)

    def on_move_z_up(self, event):
        self.update_position('Z', 1)

    def on_move_z_down(self, event):
        self.update_position('Z', -1)

    def on_calibrate(self, event):
        wx.MessageBox("Calibración automática iniciada.", "Info", wx.OK | wx.ICON_INFORMATION)
        self.send_command("CALIBRAR")

    def on_set_params(self, event):
        volume = self.volume_text.GetValue()
        time = self.time_text.GetValue()
        wx.MessageBox(f"Volumen: {volume}, Tiempo: {time}", "Info", wx.OK | wx.ICON_INFORMATION)
        self.send_command(f"SET_PARAMS V{volume} T{time}")

    def send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.write((command + '\n').encode('utf-8'))
            time.sleep(0.1)

    def update_position(self, axis, delta):
        text_ctrl = self.x_text if axis == 'X' else self.y_text if axis == 'Y' else self.z_text
        try:
            value = float(text_ctrl.GetValue())
            value += delta
            text_ctrl.SetValue(f"{value:.2f}")
            self.send_command(f"{axis} {value:.2f}")
        except ValueError:
            wx.MessageBox(f"Valor no válido en el eje {axis}.", "Error", wx.OK | wx.ICON_ERROR)

    def read_serial_data(self):
        while self.serial_connection and self.serial_connection.is_open:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                if line:
                    wx.CallAfter(self.update_display, line)
            except serial.SerialException:
                break

    def update_display(self, line):
        try:
            x_value, y_value, z_value = [float(val.split(':')[1]) for val in line.split(',')]
            self.x_text.SetValue(f"{x_value:.2f}")
            self.y_text.SetValue(f"{y_value:.2f}")
            self.z_text.SetValue(f"{z_value:.2f}")
        except (IndexError, ValueError):
            pass

    def on_close(self, event):
        if self.serial_connection:
            self.serial_connection.close()
        self.Destroy()

if __name__ == '__main__':
    app = wx.App(False)
    frame = CNCFrame(None)
    frame.Show()
    app.MainLoop()
