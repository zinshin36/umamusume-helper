# check_env.py
import PySimpleGUI as sg

try:
    print("Button:", sg.Button)
    print("Text:", sg.Text)
    print("Listbox:", sg.Listbox)
    print("Combo:", sg.Combo)
    print("PySimpleGUI environment is OK ✅")
except AttributeError as e:
    print("PySimpleGUI environment is broken ❌")
    print(e)
