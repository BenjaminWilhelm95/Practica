import tkinter as tk
from tkinter import ttk
import serial
from serial import SerialException

class CNCInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("PRO CNC Drive")
        self.serial_connection = None
        self.connect_serial()

        # Crear componentes de la interfaz
        self.create_widgets()

        # Actualizar valores de XYZ periódicamente
        if self.serial_connection:
            self.update_xyz()

    def connect_serial(self):
        try:
            self.serial_connection = serial.Serial('COM5', 9600, timeout=1)
        except SerialException as e:
            print(f"Error al abrir el puerto serial: {e}")

    def create_widgets(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status Label
        self.status_label = tk.Label(main_frame, text="Status: OK set", font=("Helvetica", 12))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=10)

        # XYZ Labels
        self.x_label = tk.Label(main_frame, text="X: 0.00 [mm]", font=("Helvetica", 12))
        self.x_label.grid(row=1, column=0, pady=5)
        self.y_label = tk.Label(main_frame, text="Y: 0.00 [mm]", font=("Helvetica", 12))
        self.y_label.grid(row=2, column=0, pady=5)
        self.z_label = tk.Label(main_frame, text="Z: 0.00 [mm]", font=("Helvetica", 12))
        self.z_label.grid(row=3, column=0, pady=5)

        # Manual Drive Buttons
        manual_drive_frame = tk.Frame(main_frame)
        manual_drive_frame.grid(row=4, column=0, pady=10, columnspan=3)

        tk.Button(manual_drive_frame, text="↑", command=lambda: self.move_axis('Y+', 1)).grid(row=0, column=1, padx=5)
        tk.Button(manual_drive_frame, text="↓", command=lambda: self.move_axis('Y-', 1)).grid(row=2, column=1, padx=5)
        tk.Button(manual_drive_frame, text="←", command=lambda: self.move_axis('X-', 1)).grid(row=1, column=0, padx=5)
        tk.Button(manual_drive_frame, text="→", command=lambda: self.move_axis('X+', 1)).grid(row=1, column=2, padx=5)

        # Set Origin Buttons
        set_origin_frame = tk.Frame(main_frame)
        set_origin_frame.grid(row=5, column=0, pady=10, columnspan=3)

        tk.Button(set_origin_frame, text="Set X Origin", command=lambda: self.send_command('SX')).grid(row=0, column=0, padx=5)
        tk.Button(set_origin_frame, text="Set Y Origin", command=lambda: self.send_command('SY')).grid(row=0, column=1, padx=5)
        tk.Button(set_origin_frame, text="Set Z Origin", command=lambda: self.send_command('SZ')).grid(row=0, column=2, padx=5)

        # Calibration Button
        tk.Button(main_frame, text="Calibrate", command=self.calibrate).grid(row=6, column=0, pady=10, columnspan=3)

        # Volume and Time Entry
        volume_time_frame = tk.Frame(main_frame)
        volume_time_frame.grid(row=7, column=0, pady=10, columnspan=3)

        tk.Label(volume_time_frame, text="Volume [mm³]").grid(row=0, column=0, padx=5)
        self.volume_entry = tk.Entry(volume_time_frame)
        self.volume_entry.grid(row=0, column=1, padx=5)

        tk.Label(volume_time_frame, text="Time [s]").grid(row=1, column=0, padx=5)
        self.time_entry = tk.Entry(volume_time_frame)
        self.time_entry.grid(row=1, column=1, padx=5)

    def move_axis(self, axis, step):
        if self.serial_connection:
            self.serial_connection.write(f'{axis}{step}'.encode())

    def send_command(self, command):
        if self.serial_connection:
            self.serial_connection.write(command.encode())

    def calibrate(self):
        if self.serial_connection:
            self.serial_connection.write('CALIBRATE'.encode())

    def update_xyz(self):
        if not self.serial_connection:
            return
        try:
            # Leer datos de Arduino
            self.serial_connection.write(b'G')  # Comando para obtener datos
            data = self.serial_connection.readline().decode('utf-8').strip()

            # Procesar datos y actualizar etiquetas
            if data:
                values = data.split(',')
                x_value = values[0].split(':')[1]
                y_value = values[1].split(':')[1]
                z_value = values[2].split(':')[1]

                self.x_label.config(text=f"X: {x_value} [mm]")
                self.y_label.config(text=f"Y: {y_value} [mm]")
                self.z_label.config(text=f"Z: {z_value} [mm]")

        except Exception as e:
            print(f"Error: {e}")

        # Llamar a esta función nuevamente después de 1 segundo
        self.root.after(1000, self.update_xyz)

# Crear ventana principal
root = tk.Tk()
app = CNCInterface(root)
root.mainloop()
