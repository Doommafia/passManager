# !TODO customtkinter
# !TODO clean up code

import csv
import tkinter as tk
import random
import string
import subprocess
from tkinter import Toplevel, filedialog
from tkinter import messagebox
from cryptography.fernet import Fernet

def copy2clip(txt):
    cmd='echo '+txt.strip()+'|clip'
    return subprocess.check_call(cmd, shell=True)

def center_window(top):
    window_width = top.winfo_screenwidth()
    window_height = top.winfo_screenheight()
    position_right = int(window_width / 2 - top.winfo_reqwidth() / 2)
    position_down = int(window_height / 2 - top.winfo_reqheight() / 2)
    top.geometry("+{}+{}".format(position_right, position_down))

class PasswordManager:
    def __init__(self):
        self.passwords = {}
        # !! This is a demo key, do not use it in production.   !!
        # !! Generate a new key with Fernet.generate_key()      !!
        # !! and store it securely, this is just a github       !!
        # !! project, so I don't care about security.           !!
        self.key = b'9QZ9-PBjPZ6yHhoH5oZGJvj1jUJkEVOp1q5TrBbszKU='
        self.cipher_suite = Fernet(self.key)
        self.chooseFile()

    def chooseFile(self):
        answer = messagebox.askquestion("Choose file", "Do you want to open an existing CSV file?")
        if answer == 'yes':
            self.filePath = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        else:
            self.filePath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if self.filePath:
            self.passLoad()

    def passEnc(self, password):
        return self.cipher_suite.encrypt(password.encode()).decode()


    def passDec(self, passHashed):
        return self.cipher_suite.decrypt(passHashed.encode()).decode()

    def passStore(self, purpose, password):
        passHashed = self.passEnc(password)
        self.passwords[purpose] = passHashed
        self.passSave()

    def passRet(self, purpose):
        passHashed = self.passwords.get(purpose)
        if passHashed:
            return self.passDec(passHashed)

    def passDel(self, purpose):
        if purpose in self.passwords:
            del self.passwords[purpose]
            self.passSave()

    def passLoad(self):
        try:
            with open(self.filePath, 'r') as file:
                reader = csv.reader(file)
                self.passwords = {rows[0]:rows[1] for rows in reader if len(rows) >= 2}
        except FileNotFoundError:
            pass

    def passSave(self):
        with open(self.filePath, 'w') as file:
            writer = csv.writer(file)
            for key, value in self.passwords.items():
                writer.writerow([key, value])

class Application(tk.Frame):
    def __init__(self, master=None, password_manager=None):
        super().__init__(master)
        self.master = master
        self.password_manager = password_manager
        self.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        window_width = self.master.winfo_screenwidth()
        window_height = self.master.winfo_screenheight()
        position_right = int(window_width / 2 - self.master.winfo_reqwidth() / 2)
        position_down = int(window_height / 2 - self.master.winfo_reqheight() / 2)
        self.master.geometry("+{}+{}".format(position_right, position_down)) 

    def create_widgets(self):
        self.master.geometry("300x200")

        self.btnStore = tk.Button(self)
        self.btnStore["text"] = "Store Password"
        self.btnStore["command"] = self.passStore
        self.btnStore["command"] = self.passStore
        self.btnStore.place(relx=0.5, rely=0.3, anchor='center')

        self.btnGet = tk.Button(self)
        self.btnGet["text"] = "Get Password"
        self.btnGet["command"] = self.passRet
        self.btnGet.place(relx=0.5, rely=0.5, anchor='center')

        self.btnDel = tk.Button(self)
        self.btnDel["text"] = "Delete Password"
        self.btnDel["command"] = self.passDel
        self.btnDel.place(relx=0.5, rely=0.7, anchor='center')
        
    def passStore(self):
        dialog = StorePasswordDialog(self, self.password_manager)
        self.wait_window(dialog.top)

    def passRet(self):
        dialog = GetPasswordDialog(self, self.password_manager)
        self.wait_window(dialog.top)

    def passDel(self):
        dialog = DeletePasswordDialog(self, self.password_manager)
        self.wait_window(dialog.top)

    

class DeletePasswordDialog:
    def __init__(self, parent, password_manager):
        top = self.top = Toplevel(parent)
        self.password_manager = password_manager

        top.geometry("300x200")
        center_window(top)

        tk.Label(top, text="Purpose").pack()
        self.purposeVar = tk.StringVar(top)
        self.purposeVar.set(list(self.password_manager.passwords.keys())[0])
        self.purposeMenu = tk.OptionMenu(top, self.purposeVar, *self.password_manager.passwords.keys())
        self.purposeMenu.pack()

        tk.Button(top, text='OK', command=self.ok).pack()

    def ok(self):
        purpose = self.purposeVar.get()
        self.password_manager.passDel(purpose)
        messagebox.showinfo("Success", f"Password for {purpose} deleted.")
        self.purposeMenu['menu'].delete(0, 'end')
        new_choices = list(self.password_manager.passwords.keys())
        for choice in new_choices:
            self.purposeMenu['menu'].add_command(label=choice, command=tk._setit(self.purposeVar, choice))
        if new_choices:
            self.purposeVar.set(new_choices[0])

class StorePasswordDialog:
    def __init__(self, parent, password_manager):
        top = self.top = Toplevel(parent)
        self.password_manager = password_manager

        top.geometry("300x200")
        center_window(top)

        tk.Label(top, text="Purpose").pack()
        self.purpose_entry = tk.Entry(top)
        self.purpose_entry.pack()

        tk.Label(top, text="Password").pack()
        self.password_entry = tk.Entry(top, show="*")
        self.password_entry.pack()

        tk.Button(top, text='Generate', command=self.passGen).pack()
        tk.Label(top, text=" ").pack()
        tk.Button(top, text='OK', command=self.ok).pack()

    def passGen(self):
        purpose = self.purpose_entry.get()
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.password_manager.passStore(purpose, password)
        messagebox.showinfo("Success", f"Password for {purpose} stored. Generated password is {password}")
        self.top.destroy()
    
    def ok(self):
        purpose = self.purpose_entry.get()
        password = self.password_entry.get()
        self.password_manager.passStore(purpose, password)
        messagebox.showinfo("Success", f"Password for {purpose} stored.")
        self.top.destroy()

class GetPasswordDialog:
    def __init__(self, parent, password_manager):
        top = self.top = Toplevel(parent)
        self.password_manager = password_manager

        top.geometry("300x200")
        center_window(top)

        tk.Label(top, text="Purpose").pack()
        self.purposeVar = tk.StringVar(top)
        self.purposeVar.set(list(self.password_manager.passwords.keys())[0])
        self.purposeMenu = tk.OptionMenu(top, self.purposeVar, *self.password_manager.passwords.keys())
        self.purposeMenu.pack()

        tk.Button(top, text='OK', command=self.ok).pack()

    def ok(self):
        purpose = self.purposeVar.get()
        password = self.password_manager.passRet(purpose)
        if password:
            messagebox.showinfo("Password!", f"Password for {purpose} is {password}. Copied to clipboard!")
            copy2clip(password)
        else:
            messagebox.showinfo("Error", f"No password stored for {purpose}")
        self.top.destroy()

root = tk.Tk()
root.geometry("500x300")
manager = PasswordManager()
app = Application(master=root, password_manager=manager)
app.mainloop()
