import tkinter as tk
from tkinter import ttk,filedialog

class CustomDialog:
    def __init__(self, parent, title, prompt,t=""):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")

        self.label = ttk.Label(self.top, text=prompt, font=('Times new roman', 9), wraplength=360)
        self.label.pack(pady=10, anchor='w', padx=20)

        self.text = tk.Text(self.top, wrap=tk.WORD, height=10, width=40,
                            font=('Times new roman', 9), bg='#f0f0f0')
        self.text.insert('1.0', t)
        self.text.pack(padx=20, fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Confirm", command=self.on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)

        self.result = None
        self.top.grab_set()

    def on_confirm(self):
        self.result = self.text.get("1.0", tk.END).strip()
        self.top.destroy()

class EnterDialog:
    def __init__(self, parent, title, prompt,t=""):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x150")

        self.label = ttk.Label(self.top, text=prompt, font=('Times new roman', 9), wraplength=360)
        self.label.pack(pady=10, anchor='w', padx=20)

        self.text = tk.Entry(self.top, width=40,
                            font=('Times new roman', 13), bg='#f0f0f0')
        self.text.insert(0, t)
        self.text.pack(padx=20, expand=True)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Confirm", command=self.on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)

        self.result = None
        self.top.grab_set()

    def on_confirm(self):
        self.result = self.text.get().strip()
        self.top.destroy()

class ChoiceDialog:
    def __init__(self, parent, title, prompt, values):
        self.result = tk.StringVar()

        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x150")

        self.label = ttk.Label(self.top, text=prompt, font=('Times new roman', 9), wraplength=360)
        self.label.pack(pady=10, anchor='w', padx=20)

        self.text = ttk.Combobox(
            master=self.top,
            width=40,
            state='readonly',
            font=('Times new roman', 13),
            textvariable=self.result,
            values=values,
            )
        self.text.pack(padx=20, expand=True)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Confirm", command=self.on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.top.destroy).pack(side=tk.LEFT)


        self.top.grab_set()

    def on_confirm(self):
        self.result = self.text.get().strip()
        self.top.destroy()

class BoolDialog:
    def __init__(self, parent, title, prompt,t=""):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x200")

        self.label = ttk.Label(self.top, text=prompt, font=('Times new roman', 12), wraplength=360)
        self.label.pack(pady=30, anchor='w', padx=20)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="True", command=self.on_confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="False", command=self.on_cancel).pack(side=tk.LEFT)

        self.result = None
        self.top.grab_set()

    def on_confirm(self):
        self.result = True
        self.top.destroy()

    def on_cancel(self):
        self.result = False
        self.top.destroy()

class MessageDialog:
    def __init__(self, parent, title, message):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.geometry("400x300")
        self.top.resizable(False, False)

        content_frame = ttk.Frame(self.top)
        content_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        msg_label = ttk.Label(
            content_frame,
            text=message,
            font=('Times new roman', 11),
            wraplength=360,
            justify=tk.LEFT
        )
        msg_label.pack(side=tk.LEFT, padx=10)

        btn_frame = ttk.Frame(self.top)
        btn_frame.pack(pady=10)
        ttk.Button(
            btn_frame,
            text="OK",
            command=self.top.destroy,
            width=10
        ).pack()

        self.top.grab_set()
        self.top.focus_force()

class Popup:
    def __init__(self):
        pass

    def textbox(self, msg, title, text, run=True):
        root = tk.Tk()
        root.withdraw()
        dialog = CustomDialog(root, title=title,prompt=msg,t=text)
        root.wait_window(dialog.top)
        root.destroy()
        if dialog.result:
            return dialog.result
        else:
            return None
    def msgbox(self,msg, title):
        root = tk.Tk()
        root.withdraw()
        dialog = MessageDialog(root, title=title, message=msg)
        root.wait_window(dialog.top)
        root.destroy()

    def filesavebox(self,default=None):
        root = tk.Tk()
        root.withdraw()
        if(default==None):
            path=filedialog.asksaveasfilename(initialfile="saved model")
        else:
            default=default.replace("\\","/")
            t=default.split("/")
            file_name=""
            if(len(t)>1):
                file_name=t[-1]
                t=t[:-1]
            t="/".join(t)

            path=filedialog.asksaveasfilename(initialdir=t,initialfile=file_name)
        root.destroy()
        if(path==""):
            return None
        else:
            return path

    def fileopenbox(self,default="./maps/*.dill",filetypes=".dill"):
        root = tk.Tk()
        root.withdraw()
        if (default == None):
            path = filedialog.asksaveasfilename(defaultextension=filetypes,filetypes=[(filetypes.replace(".","").upper(),filetypes)])
        else:
            default = default.replace("\\", "/")
            t = default.split("/")
            if (len(t) > 1):
                t = t[:-1]
            t = "/".join(t)

            path = filedialog.askopenfilename(defaultextension=filetypes, initialdir=t,filetypes=[(filetypes.replace(".","").upper(),filetypes)])
        root.destroy()
        if (path == ""):
            return None
        else:
            return path

    def enterbox(self,prompt, title, default=""):
        root = tk.Tk()
        root.withdraw()
        dialog = EnterDialog(root, title=title, prompt=prompt, t=default)
        root.wait_window(dialog.top)
        root.destroy()
        if dialog.result:
            return dialog.result
        else:
            return None

    def choicebox(self,prompt, title, choice_list):
        root = tk.Tk()
        root.withdraw()
        dialog = ChoiceDialog(root, title=title, prompt=prompt,values=choice_list)
        root.wait_window(dialog.top)
        root.destroy()
        if dialog.result:
            return dialog.result
        else:
            return None

    def boolbox(self,msg, title):
        root = tk.Tk()
        root.withdraw()
        dialog = BoolDialog(root, title=title, prompt=msg)
        root.wait_window(dialog.top)
        root.destroy()
        if dialog.result:
            return dialog.result
        else:
            return None

# p=Popup()
#
#
# msg="Enter the action you want to execute as the main control character."
# text="The actions you can choose to take include:\n"+str(["aaa"])+"\n___________\n\n"+"action: \nshort-term situational cognition: \nshort-term goal: \ninteractive object cognitive description: \nchat content (Optional, if you choose the action of chat with, it is required): "
# asw=p.choicebox(prompt=msg, title='Action', choice_list=["aaa","bbb"])
# print(asw)
# asw=p.boolbox(prompt=msg, title='Action')
# print(asw)
# asw=p.enterbox(prompt=msg, title='Action', default="50x50")
# print(asw)
# path=p.fileopenbox(default="./maps/*.dill",filetypes="*.dill")
# print(path)
# path=p.filesavebox(default="./env file/saved model")
# print(path)
# p.msgbox(msg=text, title='Action')
# asw=p.textbox(msg=msg, title='Action', text=text, run=True)
# print(asw)