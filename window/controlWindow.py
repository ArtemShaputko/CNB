from tkinter import *
from tkinter import ttk, messagebox

import serial.tools.list_ports


def get_serial_ports():
    ports = [port.device for port in serial.tools.list_ports.comports(include_links=True)]
    return ports if ports else ["No ports available "]

def port_available(port_name: str) -> bool:
    try:
        # Проверка, доступен ли порт
        with serial.Serial(port_name) as ser:
            print(f"Порт {port_name} доступен.")
            return True
    except (serial.SerialException, OSError):
        print(f"Порт {port_name} недоступен.")
        return False


def show_message(title,message):
    root = Tk()
    root.withdraw()
    messagebox.showerror(title, message)
    root.destroy()

class ControlWindow:
    def __init__(self, context, ser1, ser2):
        self.ser1 = ser1
        self.ser2 = ser2

        self.ports = get_serial_ports()

        controlFrame = ttk.Frame(context.root, borderwidth=1, relief=SOLID, padding=[10, 10])
        controlFrame.grid(row=1, column=1, sticky="nsew")
        control_name = ttk.Label(controlFrame, text="Control")
        control_name.place(relx=0.5, anchor=CENTER)

        self.port_label = Label(controlFrame, text="Choose COM-port:")
        self.port_label.place(relx=0.5, rely= 0.1, anchor=N)

        self.port_var = StringVar(value=self.ports[0] if self.ports else "No ports available")
        self.port_combo = ttk.Combobox(controlFrame, textvariable=self.port_var, values=self.ports)
        self.port_combo.place(relx=0.5, rely= 0.25, anchor=N)

        self.parity_label = ttk.Label(controlFrame, text="Choose parity:")
        self.parity_label.place(relx=0.5, rely= 0.45, anchor=N)

        self.parity_var = StringVar(value='None')
        self.parity_combo = ttk.Combobox(controlFrame, textvariable=self.parity_var, values=['None',
                                                                                            'Mark',
                                                                                            'Space',
                                                                                            'Even',
                                                                                            'Odd'])
        self.parity_combo.place(relx=0.5, rely= 0.6, anchor=N)

        self.submit_button = Button(controlFrame, text="Accept", command=self.set_parity)
        self.submit_button.place(relx=0.5, rely= 1, anchor=S)

    def set_parity(self):
        selected_parity = None
        parity_var_string = self.parity_var.get()
        if parity_var_string == "Odd":
            selected_parity = serial.PARITY_ODD
        elif parity_var_string == "Even":
            selected_parity = serial.PARITY_EVEN
        elif parity_var_string == "Mark":
            selected_parity = serial.PARITY_MARK
        elif parity_var_string == "None":
            selected_parity = serial.PARITY_NONE
        elif parity_var_string == "Space":
            selected_parity = serial.PARITY_SPACE

        selected_port = self.port_var.get()

        try:
            if selected_port == self.ser1.name:
                self.ser1.parity = selected_parity
            elif selected_port == self.ser2.name:
                self.ser2.parity = selected_parity
            else:
                serial.Serial(selected_port, parity=selected_parity).close()

        except (serial.SerialException, ValueError) as e:
            show_message("Error", f"Error setting parity for {selected_port}")
