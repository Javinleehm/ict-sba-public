import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pandas as pd
import os
import uuid
import shutil
import re
import TKinterModernThemes as TKMT
from utils import *
import sqlite3
import csv
import datetime

# Global variable that stores name of current workspace for convenience
current_workspace = ""
data_mode = "set"

# Sets executable directory as relative path directory
set_current_directory_to_executable()

# App object
class MCMASApp:
    # Init object
    def __init__(self, root):
        self.root = root
        self.root.geometry("1920x1080")
        self.root.title("Multiple Choice Marking and Analysing System (MCMAS)")
        
        self.left_panel = AppMainLayout.LeftPanel(root)
        self.right_panel = AppMainLayout.RightPanel(root)
        
        self.left_panel.grid(row=0, column=0, sticky="news")
        self.right_panel.grid(row=0, column=1, sticky="news")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=5)
    
    # Function for updating panels of app
    def update_frame(self, upper_panel, lower_panel):
        upper_panel_content = None
        lower_panel_content = None
        if upper_panel is not None:
            upper_panel_content = upper_panel(self.right_panel)
            self.right_panel.update_upper_panel(upper_panel_content)
        if lower_panel is not None:
            lower_panel_content = lower_panel(self.right_panel)
            self.right_panel.update_lower_panel(lower_panel_content)
        return upper_panel_content,lower_panel_content
    
    # Function for updating sidebar buttons
    def update_sidebar(self):
        self.left_panel.update_workspaces(list_workspaces())
    
    # Function for lighting up sidebar
    def highlight_sidebar_button(self,workspace_name):
        self.left_panel.press_button_with_text(workspace_name)
        
# Define app layout
class AppMainLayout:
    # Right panel object
    class RightPanel(tk.Frame):
        # Init right panel
        def __init__(self, parent):
            super().__init__(parent)
            self.upper_panel = tk.Frame(self)
            self.lower_panel = tk.Frame(self, bg="#DDDDDD", height=360)
            self.lower_panel.pack(side="bottom", fill="x")
            self.upper_panel.pack(side="top", fill="both")

        # Function for changing content of right upper panel
        def update_upper_panel(self, new_content):
            self.upper_panel.pack_forget()
            self.upper_panel = new_content
            self.upper_panel.pack(side="top", fill="both")
        
        # Function for changing content of right lower panel
        def update_lower_panel(self, new_content):
            self.lower_panel.pack_forget()
            self.lower_panel = new_content
            self.lower_panel.pack(side="top", fill="both",expand="True")

    # Left panel object
    class LeftPanel(tk.Frame):
        # Init object
        def __init__(self, parent):
            super().__init__(parent, bg="#AAAAAA")
            tk.Label(self, text="Papers", fg="black", bg="#AAAAAA", font=("Helvetica", 15, "bold")).pack()
            self.workspaces = list_workspaces()
            self.buttons = []
            self.selected_button = None
            self.create_buttons()
            self.manage_workspace_button = tk.Button(self, text="Home", font=("Helvetica", 13), bg="#AAAAAA", command=init_home_page)
            self.manage_workspace_button.pack(side="top", fill="x")
        
        # Function for creating new buttons on sidebar
        def create_buttons(self):
            for workspace in self.workspaces:
                button = tk.Button(self, text=workspace, command=lambda w=workspace: self.on_workspace_click(w), font=("Helvetica", 15), height=2, justify="left", bg="#AAAAAA")
                button.pack(side="top", fill="x", anchor="w")
                button.bind("<ButtonPress>", lambda event, b=button: self.on_button_press(b))
                self.buttons.append(button)

        # Function for updating entire sidebar according to list of button text
        def update_workspaces(self, new_workspaces):
            self.manage_workspace_button.pack_forget()
            for button in self.buttons:
                button.pack_forget()
            self.workspaces = new_workspaces
            self.create_buttons()
            self.manage_workspace_button = tk.Button(self, text="Home", font=("Helvetica", 13), command=init_home_page, bg="#AAAAAA")
            self.manage_workspace_button.pack(side="top", fill="x")
            # print("Buttons updated")

        # Executed when a sidebar button is clicked
        def on_workspace_click(self, workspace):
            # print(f"Switching to workspace: {workspace}")
            init_workspace(workspace)
            
        # Lights up sidebar button
        def on_button_press(self, button):
            # print(button)
            if self.selected_button:
                self.selected_button.config(bg="#AAAAAA")
            self.selected_button = button
            self.selected_button.config(bg="#FFFFFF")
            # print("On button press")
        def press_button_with_text(self, button_text):
            for button in self.buttons:
                if button.cget("text") == button_text:
                    button.config(bg="#FFFFFF")
                    
# Welcome screen class
class Welcome:
    # Welcome screen upper right panel object
    class WelcomeWorkspace(tk.Frame):
        # Init
        def __init__(self, parent):
            super().__init__(parent, borderwidth=50)
            self.setup_layout()
        
        # Creates elements shown on welcome screen
        def setup_layout(self):
            for i in range(2):
                self.columnconfigure(i, weight=1)
                self.rowconfigure(i, weight=1)

            StartTitle = self.create_frame_with_title("Welcome to GUI MCMAS", "MC marking made easy", "Get started with one of the buttons below or work on an existing paper from the left panel.")
            AuthorInfo = tk.Frame(self)
            Quickstart = self.create_quickstart_frame()
            Walkthrough = self.create_walkthrough_frame()

            StartTitle.grid(column=0, row=0, sticky="news")
            AuthorInfo.grid(column=1, row=0, sticky="news")
            Quickstart.grid(column=0, row=1, sticky="news")
            Walkthrough.grid(column=1, row=1, sticky="news")
        
        # Creates the welcome text
        def create_frame_with_title(self, main_text, sub_text, description):
            frame = tk.Frame(self)
            tk.Label(frame, text=main_text, font=("Helvetica", 30, "bold"), anchor="w", borderwidth=15).pack(anchor="w")
            tk.Label(frame, text=sub_text, font=("Helvetica", 15), anchor="w", borderwidth=15, fg="#444444").pack(anchor="w")
            tk.Label(frame, text=description, font=("Helvetica", 10), anchor="w", borderwidth=15).pack(anchor="w")
            return frame
        
        # Create the quick start buttons
        def create_quickstart_frame(self):
            frame = tk.Frame(self)
            tk.Label(frame, text="Start", font=("Helvetica", 13, "bold"), anchor="w", borderwidth=15).pack(anchor="w")
            global root
            buttons = [
                ("Create a new paper...", NewPaperPopup),
                ("Import a new paper...", ImportPaper.popup),
                ("Open database manager...", lambda:SQLDatabaseEditor(root.root)),
                ("About this app",lambda: AboutPopup(root.root))
            ]
            for text, command in buttons:
                Welcome.WelcomeButton(frame, text, command).pack(anchor="w")
            return frame

        # Create the walkthrough buttons
        def create_walkthrough_frame(self):
            frame = tk.Frame(self)
            tk.Label(frame, text="Walkthrough", font=("Helvetica", 13, "bold"), anchor="w", borderwidth=15).pack(anchor="w")
            global root
            buttons = [
                ("Get started with the MCMAS GUI workspace", lambda:PlaceHolderPopup(root.root)),
                ("Get started with the database manager", lambda:PlaceHolderPopup(root.root))
            ]
            for text, command in buttons:
                Welcome.WelcomeButton(frame, text, command).pack(anchor="w")
            return frame

    # Create each blue buttons
    class WelcomeButton(tk.Frame):
        def __init__(self, parent, buttontext, command):
            super().__init__(parent)
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=2)
            self.rowconfigure(0, weight=1)
            self.button_label = tk.Label(self, text=buttontext, font=("Helvetica", 13), fg="#4554FF", borderwidth=15)
            self.button_label.grid(column=1, row=0)
            self.button_label.bind("<Button-1>", lambda e: command())

# Workspace class
class Marker:
    # Place holder init function
    def __init__(self):
        pass
    
    # Upper panel content object
    class Workspace(tk.Frame):
        # Init
        def __init__(self,parent):
            super().__init__(parent,bg="black")
            
            self.div = tk.Frame(self)
            self.div.pack(anchor="ne",fill="both",side="right")
            
            self.actions_panel =Marker.ActionsPanel(self.div)
            self.actions_panel.pack(side="top",fill="x")
            
            
            self.answers_frame = Marker.AnswersTable(self.div)
            self.answers_frame.pack(fill="both",expand=True)
            
            self.data_selection_panel = Marker.DataSelectionPanel(self)
            self.data_selection_panel.pack(anchor="nw",fill="both")
        # Deprecated
        def get_data_mode(self):
            return self.data_selection_panel.get_data_mode()

        # Function for updating content of answer table
        def update_answer_table(self,content):
            self.answers_frame.update_table(content)
    
    # Answer table object
    class AnswersTable(tk.Frame):
        # Init
        def __init__(self, master, max_rows=65536, values=[]):
            super().__init__(master)
            
            self.master = master
            self.max_rows = max_rows
            self.values = values
            self.title = tk.Label(self,text="Model answers",font=("Helvetica", 12, "normal"))
            self.title.pack(side="top",fill="x")
            self.create_widgets()
        
        # Function that creates the elements shown
        def create_widgets(self):
            self.change_answers_button = ttk.Button(self,text="Edit answers",command=self.launch_edit_ans_win)
            self.change_answers_button.pack(side="bottom")
            self.table = ttk.Treeview(self, columns=("Index", "Value"), show="headings")
            self.table.heading("Index", text="Index")
            self.table.heading("Value", text="Value")
            
            # Creates vertical scrollbar
            vsb = ttk.Scrollbar(self, orient="vertical", command=self.table.yview)
            vsb.pack(side='right', fill='y')
            self.table.configure(yscrollcommand=vsb.set)
            
            self.table.pack(fill='both',expand=True)

        # Launches answer editing popup
        def launch_edit_ans_win(self):
            global current_workspace
            self.edit_ans_win = Marker.EditAnsPopup(current_workspace)
        
        # Function for updating content of table
        def update_table(self, answers):
            # Clear existing items in the table
            for item in self.table.get_children():
                self.table.delete(item)

            # Update the table with the answers provided
            for i, answer in enumerate(answers, start=1):
                self.table.insert('', 'end', values=(str(i), answer))
            
    # Object that defines the left section of the upper right panel
    class DataSelectionPanel(tk.Frame):
        # Init function
        def __init__(self,parent):
            global gSetName, gEntryName
            super().__init__(parent)
            # self.rowconfigure(0,weight=1)
            # self.rowconfigure(1,weight=1)
            # self.columnconfigure(0,weight=1)
            self.upper_panel = tk.Frame(self)
            self.lower_panel = tk.Frame(self)
            
            
            self.data_mode = tk.StringVar()
            self.data_mode = "set"
            
            self.select_dataset_button = tk.Radiobutton(self.upper_panel, text="Use dataset (Multiple records)", variable=self.data_mode, value="set", command=lambda:self.set_data_mode("set"),anchor="w")
            self.select_dataset_button.pack(fill="x",side="top")
            
            # Construct a list with name of each dataset and the number of candidates store in the list
            set_list = list_can_ans_set(current_workspace)
            dataset_list_content = []
            for item in set_list:
                dataset_list_content.append((item,len(prev_workspace_can_ans_set(current_workspace,item)[0])))

            self.dataset_list = self.ScrollableRadioTreeView(self.upper_panel,["Set name", "Number of Candidates"],gSetName,data=dataset_list_content)
            
            self.dataset_list.pack(fill="x",side="top")
            
            self.manage_dataset_buttons_frame = tk.Frame(self.upper_panel)

            self.add_dataset_button = ttk.Button(self.manage_dataset_buttons_frame,text="Add dataset",command=self.add_set_button_function)
            self.add_dataset_button.grid(column=0,row=0)    
            
            self.del_dataset_button = ttk.Button(self.manage_dataset_buttons_frame,text="Delete dataset", command=self.del_set_button_function)
            self.del_dataset_button.grid(column=1,row=0)

            self.manage_dataset_buttons_frame.pack(side="top")

            self.select_data_entry_button = tk.Radiobutton(self.lower_panel, text="Use data entry (Single entry)", variable=self.data_mode, value="entry", command=lambda:self.set_data_mode("entry"),anchor="w")
            self.select_data_entry_button.pack(fill="x",side="top")
            
            # Simulate a press on select dataset button so it will not show both radio buttons are pressed when first initialized
            self.select_dataset_button.invoke()
            
            # Construct a list of each data entry's name
            ans_list = list_can_ans(current_workspace)
            data_list_content = []
            for item in ans_list:
                data_list_content.append((item))

            self.data_entry_list = self.ScrollableRadioTreeView(self.lower_panel,["Entry name"],gEntryName,data=data_list_content)
            self.data_entry_list.pack(fill="x",side="top")
            
            self.manage_ans_button = tk.Frame(self.lower_panel)
            self.add_data_entry_button = ttk.Button(self.manage_ans_button, text="Add data entry",command=self.add_ans_button_function)
            self.add_data_entry_button.grid(column=0,row=0)
            self.del_data_entry_button = ttk.Button(self.manage_ans_button, text="Delete data entry",command=self.del_ans_button_function)
            self.del_data_entry_button.grid(column=1,row=0)
            self.manage_ans_button.pack(side="bottom")
            self.upper_panel.pack(fill="x",side="top")
            self.lower_panel.pack(fill="x",side="bottom")
        
        # A method to set data_mode global variable
        def set_data_mode(self,mode):
            global data_mode
            # print(mode)
            data_mode = mode

        # Function of add dataset button
        def add_set_button_function(self):
            # Open the asks for file path window
            add_set_path = askopenfilename(filetypes=[("CSV Files", "*.csv")])
            # Make a the directory for storing datasets if it is not already created
            os.makedirs(f"data/{current_workspace}/can_ans_set",exist_ok=True)
            # Validates if there exists a dataset with the same name
            if not os.path.exists(f"data/{current_workspace}/can_ans_set/{os.path.basename(add_set_path)}"):
                if validate_set_file(current_workspace,add_set_path):
                    # Copy the targeted file to the dataset storing directory
                    shutil.copy(add_set_path, f"data/{current_workspace}/can_ans_set/{os.path.basename(add_set_path)}")
                    # Initialize the workspace again to update contents of element
                    init_workspace(current_workspace)
                else:
                    messagebox.showwarning("Error","Invalid format of dataset.")
            else:
                # Shows an error message box if dataset with same name exists
                messagebox.showwarning("Error","Dataset with same name exists.")
        
        # Function of delete dataset button
        def del_set_button_function(self):
            # Get the table object to perform more actions
            table = self.dataset_list.getTableObj()
            # Try to get the file of specified dataset and delete it, then re-init the workspace
            try:
                del_name = table.item(table.selection()[0])["values"][0]
                os.remove(f"data/{current_workspace}/can_ans_set/{del_name}.csv")
                init_workspace(current_workspace)
                
            except IndexError:
                # If user tries to click this button without selecting a dataset, this error message pops up
                messagebox.showwarning("Error","Can't delete. \nNo dataset selected.")
        
        # similar function to add_set_button_function()
        def add_ans_button_function(self):
            add_ans_path = askopenfilename(filetypes=[("Data Entry Files", "*.txt")])
            # print(add_ans_path)
            os.makedirs(f"data/{current_workspace}/can_ans",exist_ok=True)
            if not os.path.exists(f"data/{current_workspace}/can_ans/{os.path.basename(add_ans_path)}"):
                shutil.copy(add_ans_path, f"data/{current_workspace}/can_ans/{os.path.basename(add_ans_path)}")
                init_workspace(current_workspace)
            else:
                messagebox.showwarning("Error","Data entry with same name exists.")

        # similar function to del_set_button_function
        def del_ans_button_function(self):
            table = self.data_entry_list.getTableObj()
            try:
                del_name = table.item(table.selection()[0])["values"][0]
                os.remove(f"data/{current_workspace}/can_ans/{del_name}.txt")
                init_workspace(current_workspace)
            except IndexError:
                messagebox.showwarning("Error","Can't delete. \nNo data selected.")

        # Deprecated
        def get_data_mode(self):
            return self.data_mode
        
        # Defines a scrollable table with radio buttons on each option
        class ScrollableRadioTreeView(tk.Frame):
            # Init the object
            def __init__(self, master, headers, var, data):
                super().__init__(master)
                self.tree_frame = tk.Frame(self)
                self.tree_frame.pack(side='right', fill='both', expand=True)
                
                self.radio_frame = tk.Frame(self)
                self.radio_frame.pack(side='left', fill='y')

                self.tree = ttk.Treeview(self.tree_frame, columns=headers, show='headings',height=10)
                
                self.tree.pack(side='left', fill='both', expand=True)

                self.scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
                self.tree.configure(yscrollcommand=self.scrollbar.set)
                self.scrollbar.pack(side='right', fill='y')

                # Create specified headers and rows
                for header in headers:
                    self.tree.heading(header, text=header.title())
                    self.tree.column(header, width=100, anchor='center')

                item_names = []
                
                # For each row, insert the items
                for item in data:
                    self.tree.insert('', 'end', values=item)
                    if type(item) == tuple:
                        item_names.append(item[0])
                    else:
                        item_names.append(item)

                # A tk variable that stores the value of radio buttons
                self.radio_var = tk.StringVar()
                self.radio_buttons = []
                self.div = tk.Frame(self.radio_frame,height=22,width=25)
                self.div.pack(anchor='w')

                # Create the radio buttons
                for i in range(len(data)):
                    radio_button = tk.Radiobutton(self.radio_frame, variable=var, value=item_names[i])
                    self.radio_buttons.append(radio_button)
                    radio_button.pack(anchor='w')
                # Simulate a click on the first button of the list if there are any buttons on the list so it won't appear as all radio buttons pressed
                if len(self.radio_buttons) > 0:
                    self.radio_buttons[0].invoke()
            
            # Get this table object
            def getTableObj(self):
                return self.tree

            # Get the selected item inside a table
            def getSelected(self):
                return self.tree.selection()
        
    # Defines the panel with several action buttons on the upper right corner
    class ActionsPanel(tk.Frame):
        def __init__(self, parent):
            super().__init__(parent)
            
            self.evaluate_button = ttk.Button(self, text="Evaluate", width=30, style="Large.TButton",command=master_evaluate)
            self.evaluate_button.pack(side="top",expand=True)
            
            self.button_div = tk.Frame(self)
            self.button_div.pack(side="top", fill="x")
            self.button_div.columnconfigure(0, weight=1)
            self.button_div.columnconfigure(1, weight=1)
                
    # Defines the frame on the lower
    class Settings(tk.Frame):
        def __init__(self,parent):
            super().__init__(parent,bg="#DDDDDD")
            self.analysis_setting_panel = Marker.AnalysisSettingsPanel(self)
            self.analysis_setting_panel.pack(side="top",fill="both")
        
        # A method that returns all setting objects
        def getObj(self):
            return self.analysis_setting_panel.getSettingsObjects()
    
    # Creates the options for settings
    class AnalysisSettingsPanel(tk.Frame):
        def __init__(self,parent):
            super().__init__(parent,bg="#DDDDDD")
            self.rowconfigure(0,weight=1)
            self.title = tk.Label(self,text="Analysis settings",  anchor="w",bg="#DDDDDD")
            self.title.grid(column=0,row=0,sticky="nw")

            self.fixed_pass = self.SettingItem(self,"Fixed pass score","fixed_pass")
            self.fixed_pass.grid(column=0,row=1,sticky="new")
            
            self.dynamic_pass = self.SettingItem(self,"Dynamic pass score (Standard score)","dynamic_pass")
            self.dynamic_pass.grid(column=0,row=2,sticky="new")
            
            self.base_score = self.SettingItem(self,"Base score (Amount, default = 0)","base_score")
            self.base_score.grid(column=0,row=3,sticky="news")
            
            self.correct_ans_score = self.SettingItem(self, "Mark addition on correct answers (Amount, default = 1)","correct_ans_score")
            self.correct_ans_score.grid(column=0,row=4,sticky="news")
            
            self.wrong_ans_deduction = self.SettingItem(self,"Mark deduction on wrong answers (Amount, default = 0)","wrong_ans_deduction")
            self.wrong_ans_deduction.grid(column=0,row=5,sticky="new")
            
            self.blank_ans_deduction = self.SettingItem(self,"Mark deduction on blanked answers (Amount, default = 0)","blank_ans_deduction")
            self.blank_ans_deduction.grid(column=0,row=6,sticky="new")
        
        # A method that returns all settings objects created in here
        def getSettingsObjects(self):
            return self.fixed_pass.getObj(),self.dynamic_pass.getObj(),self.base_score.getObj(),self.correct_ans_score.getObj(),self.wrong_ans_deduction.getObj(),self.blank_ans_deduction.getObj()
        
        # Defines the object of each setting option
        class SettingItem(tk.Frame):
            def __init__(self,parent,text,item_name):
                super().__init__(parent,bg="#DDDDDD")
                global gSettings
                self.setting_var = tk.StringVar()
                self.enabled = tk.BooleanVar()
                self.enabled_button = tk.Checkbutton(self,variable=gSettings[item_name]["Enabled"],bg="#DDDDDD",text=text)
                self.enabled_button.pack(side="left")
                self.setting = tk.Entry(self,textvariable=gSettings[item_name]["Value"])
                self.setting.pack(side="right",fill="x")
            
            # Get the setting object
            def getObj(self):
                return self.enabled_button, self.setting

    # Defines the answer editing pop up window, similar to "NewPaperPopup"
    class EditAnsPopup:
        def __init__(self,workspace_name):
            self.workspace_name = workspace_name
            self.popup = tk.Toplevel()
            self.popup.geometry("1280x720")
            self.popup.title("Edit Answers")
            self.popup.grab_set()
            self.popup.focus_force()

            self.answers = []
            self.answer_name = tk.StringVar()

            self.setup_ui()
            self.popup.bind("<Escape>", lambda event: self.popup.destroy())
            self.popup.bind("<Control-n>", lambda event: self.add_answer())
            self.popup.bind("<Control-e>", lambda event: self.edit_answer())
            self.popup.bind("<Delete>", lambda event: self.delete_answer())

            (answers,remark) = read_workspace_ans(workspace_name)
            for i in range(len(answers)):
                self.submit_answer(answers[i],remark[i],None)

        def setup_ui(self):
            frame = tk.Frame(self.popup)
            frame.pack(fill="both", expand=True, padx=20, pady=20)

            ttk.Label(frame, text="Model Answers", font=("Helvetica", 20)).pack(anchor="w")
            ttk.Label(frame, text="Add, edit, or delete model answers. Use the buttons below to manage your answers.", anchor="w").pack(anchor="w")

            self.answer_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=15)
            self.answer_listbox.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.answer_listbox.yview)
            self.answer_listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

            button_frame = tk.Frame(frame)
            button_frame.pack(side="bottom", fill="x")

            button_options = {'width': 15}
            ttk.Button(button_frame, text="Add Answer", command=self.add_answer, **button_options).pack(side="left", padx=5, pady=5)
            ttk.Button(button_frame, text="Edit Answer", command=self.edit_answer, **button_options).pack(side="left", padx=5, pady=5)
            ttk.Button(button_frame, text="Delete Answer", command=self.delete_answer, **button_options).pack(side="left", padx=5, pady=5)
            ttk.Button(button_frame, text="Done", command=self.save_answers, **button_options).pack(side="right", padx=5, pady=5)

            instructions = ttk.Label(frame, text="Shortcuts: Ctrl+N (Add), Ctrl+E (Edit), Del (Delete), Enter (Submit)", anchor="w")
            instructions.pack(side="bottom", fill="x", padx=10, pady=10)

        def add_answer(self):
            new_window = tk.Toplevel(self.popup)
            new_window.title("Add Answer")
            new_window.geometry("400x200")
            new_window.grab_set()
            new_window.focus_force()

            new_window.bind("<Escape>", lambda event: new_window.destroy())

            tk.Label(new_window, text="Answer:").pack()
            answer_entry = tk.Entry(new_window, width=30)
            answer_entry.pack(pady=10)
            answer_entry.focus_set()

            tk.Label(new_window, text="Remarks:").pack()
            remark_entry = tk.Entry(new_window, width=30)
            remark_entry.pack(pady=10)

            # Bind Enter key to add the answer
            answer_entry.bind("<Return>", lambda event: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window))
            remark_entry.bind("<Return>", lambda event: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window))
            ttk.Button(new_window, text="Add", command=lambda: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window)).pack(pady=10)

        def submit_answer(self, answer, remark, window):
            if answer.strip():
                self.answers.append((answer, remark))
                self.answer_listbox.insert(tk.END, f"{answer} - {remark}")
                if window is not None:
                    window.destroy()
            else:
                messagebox.showwarning("Input Error", "Answer cannot be empty.")

        def edit_answer(self):
            selected = self.answer_listbox.curselection()
            if selected:
                index = selected[0]
                answer, remark = self.answers[index]

                edit_window = tk.Toplevel(self.popup)
                edit_window.title("Edit Answer")
                edit_window.geometry("400x200")
                edit_window.grab_set()
                edit_window.focus_force()

                edit_window.bind("<Escape>", lambda event: edit_window.destroy())

                tk.Label(edit_window, text="Answer:").pack()
                answer_entry = tk.Entry(edit_window, width=30)
                answer_entry.pack(pady=10)
                answer_entry.insert(0, answer)
                answer_entry.focus_set()

                tk.Label(edit_window, text="Remarks:").pack()
                remark_entry = tk.Entry(edit_window, width=30)
                remark_entry.pack(pady=10)
                remark_entry.insert(0, remark)

                answer_entry.bind("<Return>", lambda event: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window))
                remark_entry.bind("<Return>", lambda event: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window))
                ttk.Button(edit_window, text="Save", command=lambda: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window)).pack(pady=10)

        def update_answer(self, index, answer, remark, window):
            if answer.strip():
                self.answers[index] = (answer, remark)
                self.answer_listbox.delete(index)
                self.answer_listbox.insert(index, f"{answer} - {remark}")
                window.destroy()
            else:
                messagebox.showwarning("Input Error", "Answer cannot be empty.")

        def delete_answer(self):
            selected = self.answer_listbox.curselection()
            if selected:
                index = selected[0]
                del self.answers[index]
                self.answer_listbox.delete(index)

        def save_answers(self):
            if not self.answers:
                tk.messagebox.showwarning("Save Error", "Cannot save an empty file. Please add answers first.")
                return

            paper_name = self.workspace_name
            if not paper_name:
                tk.messagebox.showwarning("Input Error", "Paper name cannot be empty.")
                return
            
            new_folder_path = f"data/{paper_name}/ans.csv"

            df = pd.DataFrame(self.answers, columns=["ans", "remarks"])
            df.to_csv(new_folder_path, index=False)

            # print(f"Renamed folder to {new_folder_path}")
            init_workspace(paper_name)
            self.popup.destroy()

# Object that creates the Import Paper Popup
class ImportPaper:
    uid = ""

    def __init__(self):
        pass

    # Creates popup
    @staticmethod
    def popup():
        import_paper_win = tk.Toplevel()
        import_paper_win.geometry("1280x720")
        import_paper_win.grab_set()
        import_paper_win.wm_title("Import a new paper...")

        import_paper_win.focus_force()  # Ensure the popup is focused
        import_paper_win.bind("<Escape>", lambda event: import_paper_win.destroy())

        wrapper = tk.Frame(import_paper_win)
        wrapper.pack(fill="both", expand=True)

        content = tk.Frame(wrapper)
        preview_block = ImportPaper.create_preview_block(content)
        paper_name_entry = ImportPaper.create_settings_block(content, preview_block)
        
        ImportPaper.create_end_buttons(wrapper, paper_name_entry)
        content.pack(side="top", fill="both", anchor="w")
        
    # Creates the preview table
    @staticmethod
    def create_preview_block(content):
        preview_block = tk.Frame(content, border=50)
        tk.Label(preview_block, text="Preview:", font=("Helvetica", 12)).pack(side="top")
        prev_window = ScrollableTable(preview_block, ("Question No.", "Answer"), [], 25, 200)
        prev_window.pack(side="top", expand=True)
        preview_block.pack(side="left", anchor="nw", expand=False)
        return prev_window

    # Creates the settings panel
    @staticmethod
    def create_settings_block(content, preview_block):
        settings_block = tk.Frame(content, border=50)
        tk.Label(settings_block, text="Import a New Paper...", font=("Helvetica", 20, "bold"), anchor="w").pack(side="top", anchor="nw")
        tk.Label(settings_block, text="Please select a CSV file to import your paper answers. The data will be previewed below.", font=("Helvetica", 12), anchor="w").pack(side="top", anchor="nw")
        tk.Label(settings_block, text="Paper Name:").pack(side="top", anchor="nw")
        paper_name_entry = ttk.Entry(settings_block, width=70)
        paper_name_entry.pack(side="top", anchor="nw")
        
        ImportPaper.create_file_selection_block(settings_block, preview_block)
        settings_block.pack(side="left", anchor="nw", expand=False)
        
        return paper_name_entry

    # Creates the file selection input block
    @staticmethod
    def create_file_selection_block(settings_block, preview_block):
        tk.Label(settings_block, text="Select file:").pack(side="top", anchor="nw")
        paper_path_selection = tk.Frame(settings_block)
        paper_path_entry = ttk.Entry(paper_path_selection, width=60)
        paper_path_entry.pack(side="left")
        browse_button = ttk.Button(paper_path_selection, text="Browse...", command=lambda: ImportPaper.browse_button_func(paper_path_entry, preview_block))
        browse_button.pack(side="right")
        paper_path_selection.pack(side="top", anchor="nw")

    # Launches the find file window
    @staticmethod
    def browse_button_func(paper_path_entry, preview_block):
        file_path = askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            # Keep the original path in the entry
            paper_path_entry.delete(0, tk.END)
            paper_path_entry.insert(0, file_path)

            # Generate a unique directory and file path
            ImportPaper.uid = str(uuid.uuid4())
            dir_path = f"data/temp-{ImportPaper.uid}"
            os.makedirs(dir_path, exist_ok=True)  # Create the directory if it doesn't exist
            new_file_path = os.path.join(dir_path, "ans.csv")

            # Copy the selected file to the new location
            shutil.copy(file_path, new_file_path)

            # Read answers from the new file path
            answers = prev_read_ans(new_file_path)
            ImportPaper.populate_preview(preview_block, answers)

    @staticmethod
    def create_end_buttons(wrapper, paper_name_entry):
        end_buttons = tk.Frame(wrapper, border=20)
        end_buttons.columnconfigure(0, weight=1)
        end_buttons.columnconfigure(1, weight=1)
        ttk.Button(end_buttons, text="Close", command=wrapper.master.destroy).grid(column=0, row=0)
        
        # Pass paper_name_entry value & popup window to confirm_function
        ttk.Button(end_buttons, text="Confirm", command=lambda: ImportPaper.confirm_function(paper_name_entry.get(), wrapper.master)).grid(column=1, row=0)
        end_buttons.pack(side="bottom")

    @staticmethod
    def populate_preview(preview_block, answers):
        if isinstance(preview_block, ScrollableTable):
            preview_block.update_data(list(zip(range(1, len(answers[0]) + 1), answers[0])))
            
    @staticmethod
    def confirm_function(paper_name, popup_window):
        # Validate paper name
        if not paper_name.strip():
            messagebox.showerror("Error", "Paper name cannot be empty.")
            return

        # Check for invalid characters so no error
        if not re.match("^[a-zA-Z0-9_ ]+$", paper_name):
            messagebox.showerror("Error", "Paper name contains invalid characters.")
            return
        
        # Check if the directory already exists
        target_path = f"data/{paper_name}"
        if os.path.exists(target_path):
            messagebox.showerror("Error", "A paper with this name already exists. Please choose a different name.")
            return
        try:
            # Rename the temporary directory to the new paper name
            os.rename(f"data/temp-{ImportPaper.uid}", target_path)
            
            init_workspace(paper_name)
            popup_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"""An error occurred
    {e}""")
        
        
        
        
# Create new paper popup
class NewPaperPopup:
    # Init
    def __init__(self):
        self.popup = tk.Toplevel()
        self.popup.geometry("1280x720")
        self.popup.title("Create a New Paper")
        self.popup.grab_set()
        self.popup.focus_force()

        self.answers = []
        self.paper_name = tk.StringVar()

        self.setup_ui()
        self.popup.bind("<Escape>", lambda event: self.popup.destroy())
        self.popup.bind("<Control-n>", lambda event: self.add_answer())
        self.popup.bind("<Control-e>", lambda event: self.edit_answer())
        self.popup.bind("<Delete>", lambda event: self.delete_answer())

    # Creates element in the popup
    def setup_ui(self):
        frame = tk.Frame(self.popup)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Model Answers", font=("Helvetica", 20)).pack(anchor="w")
        ttk.Label(frame, text="Add, edit, or delete model answers for your paper. Use the buttons below to manage your answers.", anchor="w").pack(anchor="w")

        ttk.Label(frame, text="\nPaper Name:").pack(anchor="w")
        paper_name_entry = ttk.Entry(frame, textvariable=self.paper_name, width=50)
        paper_name_entry.pack(anchor="w", pady=10)

        self.answer_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=15)
        self.answer_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.answer_listbox.yview)
        self.answer_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        button_frame = tk.Frame(frame)
        button_frame.pack(side="bottom", fill="x")

        button_options = {'width': 15}
        ttk.Button(button_frame, text="Add Answer", command=self.add_answer, **button_options).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Edit Answer", command=self.edit_answer, **button_options).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Delete Answer", command=self.delete_answer, **button_options).pack(side="left", padx=5, pady=5)
        ttk.Button(button_frame, text="Done", command=self.save_answers, **button_options).pack(side="right", padx=5, pady=5)

        instructions = ttk.Label(frame, text="Shortcuts: Ctrl+N (Add), Ctrl+E (Edit), Del (Delete), Enter (Submit)", anchor="w")
        instructions.pack(side="bottom", fill="x", padx=10, pady=10)
        
    # Launches another window that asks user to fill in new ans
    def add_answer(self):
        new_window = tk.Toplevel(self.popup)
        new_window.title("Add Answer")
        new_window.geometry("400x200")
        new_window.grab_set()
        new_window.focus_force()

        new_window.bind("<Escape>", lambda event: new_window.destroy())

        tk.Label(new_window, text="Answer:").pack()
        answer_entry = tk.Entry(new_window, width=30)
        answer_entry.pack(pady=10)
        answer_entry.focus_set()

        tk.Label(new_window, text="Remarks:").pack()
        remark_entry = tk.Entry(new_window, width=30)
        remark_entry.pack(pady=10)

        # Bind Enter key to add the answer
        answer_entry.bind("<Return>", lambda event: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window))
        remark_entry.bind("<Return>", lambda event: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window))
        ttk.Button(new_window, text="Add", command=lambda: self.submit_answer(answer_entry.get(), remark_entry.get(), new_window)).pack(pady=10)

    # Function of confirm add button
    def submit_answer(self, answer, remark, window):
        if answer.strip():
            self.answers.append((answer,remark))
            self.answer_listbox.insert(tk.END, f"{answer} - {remark}")
            window.destroy()
        else:
            tk.messagebox.showwarning("Input Error", "Answer cannot be empty.")

    # Popup that edits the selected answer
    def edit_answer(self):
        selected = self.answer_listbox.curselection()
        if selected:
            index = selected[0]
            answer, remark = self.answers[index]

            edit_window = tk.Toplevel(self.popup)
            edit_window.title("Edit Answer")
            edit_window.geometry("400x200")
            edit_window.grab_set()
            edit_window.focus_force()

            edit_window.bind("<Escape>", lambda event: edit_window.destroy())

            tk.Label(edit_window, text="Answer:").pack()
            answer_entry = tk.Entry(edit_window, width=30)
            answer_entry.pack(pady=10)
            answer_entry.insert(0, answer)
            answer_entry.focus_set()

            tk.Label(edit_window, text="Remarks:").pack()
            remark_entry = tk.Entry(edit_window, width=30)
            remark_entry.pack(pady=10)
            remark_entry.insert(0, remark)

            # Bind Enter key to save edited answer
            answer_entry.bind("<Return>", lambda event: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window))
            remark_entry.bind("<Return>", lambda event: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window))
            ttk.Button(edit_window, text="Save", command=lambda: self.update_answer(index, answer_entry.get(), remark_entry.get(), edit_window)).pack(pady=10)

    # Function that actually edits the answer
    def update_answer(self, index, answer, remark, window):
        if answer.strip():
            self.answers[index] = (answer, remark)
            self.answer_listbox.delete(index)
            self.answer_listbox.insert(index, f"{answer} - {remark}")
            window.destroy()
        else:
            tk.messagebox.showwarning("Input Error", "Answer cannot be empty.")

    # Function that deletes selected answer
    def delete_answer(self):
        selected = self.answer_listbox.curselection()
        if selected:
            index = selected[0]
            del self.answers[index]
            self.answer_listbox.delete(index)

    # Function that checks if paper can actually be created without causing errors
    def validate_paper_name(self, paper_name):
        # Check for invalid characters in the paper name
        if not re.match("^[a-zA-Z0-9_ ]+$", paper_name):
            tk.messagebox.showerror("Error", "Paper name contains invalid characters. Only letters, numbers, underscores, and spaces are allowed.")
            return False

        # Check if the directory already exists
        target_path = f"data/{paper_name}"
        if os.path.exists(target_path):
            messagebox.showerror("Error", "A paper with this name already exists. Please choose a different name.")
            return
        
        return True

    # Function that actually save the answers
    def save_answers(self):
        if not self.answers:
            tk.messagebox.showwarning("Save Error", "Cannot save an empty file. Please add answers first.")
            return

        paper_name = self.paper_name.get().strip()
        if not paper_name:
            tk.messagebox.showwarning("Input Error", "Paper name cannot be empty.")
            return

        if not self.validate_paper_name(paper_name):
            return

        uid = str(uuid.uuid4())
        dir_path = f"data/temp-{uid}"
        os.makedirs(dir_path, exist_ok=True)
        
        file_path = os.path.join(dir_path, "ans.csv")

        df = pd.DataFrame(self.answers, columns=["ans", "remarks"])
        df.to_csv(file_path, index=False)
        # print(f"Saved answers to {file_path}")

        # Rename the folder
        new_folder_path = os.path.join(os.path.dirname(dir_path), paper_name)
        os.rename(dir_path, new_folder_path)

        # print(f"Renamed folder to {new_folder_path}")
        init_workspace(paper_name)
        self.popup.destroy()

# Table with scrollbar object
class ScrollableTable(tk.Frame):
    # Init
    def __init__(self, master, headers, data, height, width):
        super().__init__(master)
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(side='right', fill='both', expand=True)
        self.setup_treeview(headers, data, height, width)

    # Sets up the table itself
    def setup_treeview(self, headers, data, height, width):
        font_size = 12 
        self.tree = ttk.Treeview(self.tree_frame, height=height, columns=headers, show='headings')
        self.tree.pack(side='left', fill='both', expand=True)
        
        self.tree.tag_configure('big_font', font=('Helvetica', font_size))

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='left', fill='y')

        for header in headers:
            self.tree.heading(header, text=header.title(), anchor='center')
            self.tree.column(header, width=width, anchor='center')

        for item in data:
            self.tree.insert('', 'end', values=item, tags=('big_font',))

    # Function that updates all elements inside
    def update_data(self, data):
        self.tree.delete(*self.tree.get_children())
        for item in data:
            self.tree.insert("", "end", values=item, tags=('big_font',))

# Popup that shows the evaluated performance of a dataset
class DatasetPerformancePopup:
    # Initialize the window and create all elements in the popup
    def __init__(self, master, data):
        self.top = tk.Toplevel(master)
        self.top.geometry("1860x920")
        self.top.title("Candidates' Performance")

        frame = ttk.Frame(self.top)
        frame.pack(fill="both", expand=True, padx=20,pady=20)
        
        self.title = ttk.Label(frame,text="Candidates' Performance",font=("Helvetica", 20, "bold"))
        self.title.pack(anchor="w")
        
        self.desc = ttk.Label(frame,text="Below is the candidates' performance based on the answer key. Click on the headings of the categories to sort the table accordingly and scroll for more data.",font=("Helvetica",12,"normal"))
        self.desc.pack(anchor="w")

        self.group_performance_tree = ttk.Treeview(frame,columns=("Mean Score","Highest Score","Best Performing Candidate","Lowest Score","Worst Performing Candidate","Number of Pass","Passing Rate","Number of Candidates"),show="headings",height=1)
        self.group_performance_tree.heading("Mean Score", text="Mean Score")
        self.group_performance_tree.heading("Highest Score", text="Highest Score")
        self.group_performance_tree.heading("Best Performing Candidate", text="Best Performing Candidate")
        self.group_performance_tree.heading("Lowest Score", text="Lowest Score")
        self.group_performance_tree.heading("Worst Performing Candidate", text="Worst Performing Candidate")
        self.group_performance_tree.heading("Number of Candidates", text="Number of Candidates")
        self.group_performance_tree.heading("Number of Pass", text="Number of Pass")
        self.group_performance_tree.heading("Passing Rate", text="Passing Rate")
        self.group_performance_tree.pack(side="bottom",fill="both")

        self.treeframe = tk.Frame(frame)
        self.treeframe.pack(side="top",fill="both",expand=True)

        self.tree = ttk.Treeview(self.treeframe, columns=("ID", "Name", "Correct", "Wrong", "Blanked", "Score", "Max. Attainable Score","Standard Score", "Passed"), show='headings', height=10)
        
        self.tree.heading("ID", text="Candidate ID", command=lambda: self.sort_column("ID", False))
        self.tree.heading("Name", text="Name")
        self.tree.heading("Correct", text="Correct", command=lambda: self.sort_column("Correct", False))
        self.tree.heading("Wrong", text="Wrong")
        self.tree.heading("Blanked", text="Blanked")
        self.tree.heading("Score", text="Score", command=lambda: self.sort_column("Score", False))
        self.tree.heading("Max. Attainable Score", text="Max. Attainable Score")
        self.tree.heading("Standard Score", text="Standard Score", command=lambda: self.sort_column("Standard Score", False))
        self.tree.heading("Passed", text="Passed")

        self.tree.tag_configure('big_font', font=('Arial', 12))
        self.tree.bind("<Configure>", lambda e: self.adjust_font())

        scrollbar = ttk.Scrollbar(self.treeframe, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill=tk.Y)

        self.tree.pack(side="left", fill="both", expand=True)

        # Fills the tables with content
        self.populate_table(data)

        button_frame = ttk.Frame(self.top)
        button_frame.pack(pady=10)

        self.open_graph_button = ttk.Button(button_frame, text="Show Performance of Each Question", command=lambda data=data:get_correct_percentage_graph(data).show())
        self.open_graph_button.grid(row=0, column=0, padx=5)

        self.send_data_button = ttk.Button(button_frame, text="Send Data to Database", command=self.send_to_db)
        self.send_data_button.grid(row=0, column=1, padx=5)

        self.close_button = ttk.Button(self.top, text="Close", command=self.top.destroy)
        self.close_button.pack(pady=10)

        self.data = data
        self.sort_order = {  
            "ID": False,
            "Score": False,
            "Standard Score": False,
            "Correct": False
        }

    # Function that gets the data and fill them accordingly in the tables
    def populate_table(self, data):
        best_candidate = data[0][0]
        highest_score = data[0][3]
        worst_candidate = data[0][0]
        lowest_score = data[0][3]

        self.id_list = []
        self.name_list = []
        self.correct_list = []
        self.wrong_list = []
        self.blanked_list = []
        self.score_list = []
        self.max_a_score_list = []
        self.standard_score_list = []
        self.passed_list = []
        self.ans_list = []
        
        for entry in data:
            candidate_id = entry[0]
            name = entry[1]
            performance = entry[2]

            correct = performance.count(True)
            wrong = performance.count(False)
            blanked = performance.count(' ')

            score = entry[3]
            
            if score > highest_score:
                highest_score = score
                best_candidate = candidate_id
            if score < lowest_score:
                lowest_score = score
                worst_candidate = candidate_id

            standard_score = entry[5]
            
            base_score = 0
            blank_ans_deduction = 0
            correct_ans_score = 1
            wrong_ans_deduction = 0
            if gSettings["base_score"]["Enabled"].get():
                base_score = float(gSettings["base_score"]["Value"].get())
            if gSettings["blank_ans_deduction"]["Enabled"].get():
                blank_ans_deduction = float(gSettings["blank_ans_deduction"]["Value"].get())
            if gSettings["correct_ans_score"]["Enabled"].get():
                correct_ans_score = float(gSettings["correct_ans_score"]["Value"].get())
            if gSettings["wrong_ans_deduction"]["Enabled"].get():
                wrong_ans_deduction = float(gSettings["wrong_ans_deduction"]["Enabled"].get())
            
            max_a_score = get_max_attainable_score(current_workspace,base_score,correct_ans_score,blank_ans_deduction,wrong_ans_deduction)
            
            if gSettings["dynamic_pass"]["Enabled"].get():
                passed = standard_score >= float(gSettings["dynamic_pass"]["Value"].get())
            elif gSettings["fixed_pass"]["Enabled"].get():
                passed = score >= float(gSettings["fixed_pass"]["Value"].get())
            else:
                passed = score >= (get_max_attainable_score(current_workspace,base_score,correct_ans_score,blank_ans_deduction,wrong_ans_deduction)/2)

            self.id_list.append(candidate_id)
            self.name_list.append(name)
            self.correct_list.append(correct)
            self.wrong_list.append(wrong)
            self.blanked_list.append(blanked)
            self.score_list.append(score)
            self.max_a_score_list.append(max_a_score)
            self.standard_score_list.append(standard_score)
            self.passed_list.append(passed)
            # print(f"data 4: {entry[4]}")
            self.ans_list.append(entry[4])
            
            
            
            self.tree.insert("", "end", values=(candidate_id, name, correct, wrong, blanked, score, max_a_score, standard_score, passed), tags=('big_font',))

        for item in self.group_performance_tree.get_children():
            self.group_performance_tree.delete(item)
        
        self.q_num = len(data)
        pass_count = self.passed_list.count(True)
        # print(self.passed_list)
        
        self.group_performance_tree.insert("","end",values=(get_mean_score(data),highest_score,best_candidate,lowest_score,worst_candidate,pass_count,f"{pass_count/len(data)*100}%",len(data)))
        

    # Function that re-sort the table when the category names are pressed
    def sort_column(self, col, reverse):
        self.sort_order[col] = not self.sort_order[col]
        reverse = self.sort_order[col]

        sorted_data = sorted(self.data, key=lambda x: self.get_sort_key(x, col), reverse=reverse)

        for item in self.tree.get_children():
            self.tree.delete(item)
        self.populate_table(sorted_data)
    
    # Identify which key should be used to sort
    def get_sort_key(self, entry, col):
        if col == "ID":
            return entry[0]
        elif col == "Score":
            return entry[3]
        elif col == "Standard Score":
            return entry[4]
        elif col == "Correct":
            performance = entry[2]
            return performance.count(True)
        return entry

    # Apply font (not using Helvetica here because Helvetica is only used for instructions and descriptions, not data)
    def adjust_font(self):
        self.tree.tag_configure('big_font', font=('Arial', 12))

    # Deprecated test function
    def open_graph(self):
        print("Open Graph clicked")

    # Deprecated test function
    def send_data(self):
        print("Send Data to Database clicked")
    
    # Function that sends all data on the table and every candidate's answer to SQL editor. Creates a database if there isn't one, and create a new table. Then put all data inside
    def send_to_db(self):
        while True:
            try:
                db = sqlite3.connect(f"data_db/{current_workspace}.db")
                break
            except sqlite3.OperationalError:
                os.mkdir("data_db")
        cursor = db.cursor()
        table_name = f"_{gSetName.get().replace(" ","_")}_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"
        query = f"CREATE TABLE {table_name} (CAN_ID varchar(10) PRIMARY KEY, CAN_NAME varchar(50), ANS varchar({self.q_num}), CORRECT INTEGER, WRONG INTEGER, BLANKED INTEGER, SCORE FLOAT, MAX_A_SCORE FLOAT, STD_SCORE FLOAT, PASSED BOOLEAN)"
        # print(query)
        cursor.execute(query)
        for i,id in enumerate(self.id_list):
            query = f"INSERT INTO {table_name} VALUES ('{id}','{self.name_list[i]}','{self.ans_list[i]}',{self.correct_list[i]},{self.wrong_list[i]},{self.blanked_list[i]},{self.score_list[i]},{self.max_a_score_list[i]},{self.standard_score_list[i]},{self.passed_list[i]})"
            # print(query)
            cursor.execute(query)
        db.commit()
        global root
        SQLDatabaseEditor(root.root,default_query=f"SELECT * FROM {table_name}",default_db=current_workspace)
    
# Popup that shows the evaluated performance of a data entry
class DataEntryPerformancePopup:
    # Initalize the popup and create all elements
    def __init__(self,master,data):
        self.top = tk.Toplevel(master)
        self.top.geometry("1270x600")
        self.top.title("Candidate's Performance")
        frame = tk.Frame(self.top)
        frame.pack(expand=True,padx=20,pady=20,fill="both")
        self.title = ttk.Label(frame,text="Candidate's Performance",font=("Helvetica",20,"bold"))
        self.title.pack(side="top",anchor="w")
        
        self.desc = ttk.Label(frame,text="Below is the candidate's performance.",font=("Helvetica",12,"normal"))
        self.desc.pack(side="top",anchor="w")

        self.ans_tree_frame = tk.Frame(frame)
        self.ans_tree_frame.pack(side="top",fill="x")
        self.ans_tree = ttk.Treeview(self.ans_tree_frame,columns=("Question No.","Candidates' Answer","Model Answer"),show="headings",height=10)
        self.ans_tree.heading("Question No.", text="Question No.")
        self.ans_tree.heading("Candidates' Answer", text="Candidates' Answer")
        self.ans_tree.heading("Model Answer",text="Model Answer")
        
        self.ans_tree_scrollbar = ttk.Scrollbar(self.ans_tree_frame,orient="vertical",command=self.ans_tree.yview)
        self.ans_tree_scrollbar.pack(side="right",fill="y")

        self.performance_tree_frame = tk.Frame(frame)
        self.performance_tree_frame.pack(side="top",fill="x")

        self.performance_tree = ttk.Treeview(self.performance_tree_frame,columns=("No. of Questions","Correct Answers","Wrong Answers","Blanked Answers","Pass"),show="headings",height=1)
        self.performance_tree.heading("No. of Questions", text="No. of Questions")
        self.performance_tree.heading("Correct Answers", text="Correct Answers")
        self.performance_tree.heading("Wrong Answers", text="Wrong Answers")
        self.performance_tree.heading("Blanked Answers", text="Blanked Answers")
        self.performance_tree.heading("Pass", text="Pass")
        self.performance_tree.pack(side="top",fill="x")

        self.close_button = ttk.Button(frame,text="Close",command=self.top.destroy)
        self.close_button.pack(side="bottom")

        self.ans_tree.pack(side="left",fill="y",expand=True)

        # Fill the table after it is created and packed
        self.populate_table(data)

    # Function that fills the data into the table
    def populate_table(self,data):
        model_ans = prev_read_ans(f"data/{current_workspace}/ans.csv")
        can_ans = prev_workspace_can_ans_entry(current_workspace,gEntryName.get())

        for i,ans in enumerate(can_ans):
            self.ans_tree.insert("","end",values=(i+1,ans,model_ans[0][i]))

        if gSettings["fixed_pass"]["Enabled"].get():
            passing_score = gSettings["fixed_pass"]["Value"].get()
        else:
            passing_score = (i+1)/2

        self.performance_tree.insert("","end",values=(i+1,data.count(True),data.count(False),data.count(" "),data.count(True)>=passing_score))

# SQL Editor popup object
class SQLDatabaseEditor(tk.Toplevel):
    def __init__(self, master=None, default_query="", default_db=""):
        super().__init__(master)
        self.grab_set()
        self.focus_force()
        self.title("SQL Database Editor")
        self.geometry("1920x1080")

        frame = ttk.Frame(self, padding=(20, 20))
        frame.pack(fill="both", expand=True)

        title_label = ttk.Label(frame, text="SQL Database Editor", font=("Helvetica", 20, "bold"))
        title_label.pack(anchor="w")

        description_label = ttk.Label(frame, text="Choose a database and execute SQL queries.", font=("Helvetica", 12))
        description_label.pack(pady=(5, 20), anchor="w")

        self.db_combobox = ttk.Combobox(frame, values=self.fetch_databases(), state='readonly')
        self.db_combobox.pack(pady=(0, 20), anchor="w")

        if default_db:
            self.db_combobox.set(f"{default_db}.db")

        ttk.Label(frame,text="Enter your SQL Query here:", font=("Helvetica",12,"normal")).pack(anchor="w")

        self.query_text = tk.Text(frame, height=5, width=50, font=("Helvetica", 14))
        self.query_text.pack(pady=(0, 5), fill="x", expand=True)

        self.query_text.bind('<Shift-Return>', lambda event: self.execute_query())

        execute_button = ttk.Button(frame, text="Execute Query", command=self.execute_query)
        execute_button.pack(pady=(0, 2))

        ttk.Label(frame,text="SQL result:", font=("Helvetica",12,"normal")).pack(anchor="w")

        results_text_frame = tk.Frame(frame)
        results_text_frame.pack(fill="x", expand=True)

        self.results_text = tk.Text(results_text_frame, height=20, width=50, font=("Helvetica", 14))
        results_text_scrollbar = ttk.Scrollbar(results_text_frame, orient="vertical", command=self.results_text.yview)
        results_text_scrollbar.pack(side="right", fill="y")
        self.results_text.pack(side="left", pady=5, padx=5, fill="both", expand=True)
        self.results_text.config(yscrollcommand=results_text_scrollbar.set)

        export_button = ttk.Button(frame, text="Export to CSV", command=self.export_to_csv)
        export_button.pack(pady=(10, 2))

        close_button = ttk.Button(frame, text="Close", command=self.destroy)
        close_button.pack(pady=(0, 10))

        if default_query:
            self.query_text.insert(tk.END, default_query)
            execute_button.invoke()

    # List all database created
    def fetch_databases(self):
        db_directory = 'data_db'
        return [f for f in os.listdir(db_directory) if f.endswith('.db')]

    # Sends query in entry box to the SQL database
    def execute_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        selected_db = self.db_combobox.get()
        if not selected_db:
            messagebox.showerror("Error", "Please select a database.")
            return
        
        db_path = os.path.join('data_db', selected_db)
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            conn.commit()
            conn.close()
            
            self.results_text.delete("1.0", tk.END)
            for row in results:
                self.results_text.insert(tk.END, f"{row}\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Exported the SQL result as CSV to selected location
    def export_to_csv(self):
        selected_db = self.db_combobox.get()
        if not selected_db:
            messagebox.showerror("Error", "Please select a database.")
            return
        
        db_path = os.path.join('data_db', selected_db)
        
        query = self.query_text.get("1.0", tk.END).strip()
        
        file_path = asksaveasfilename(defaultextension=".csv", 
                                                   filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file_path:
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]
            
            with open(file_path, mode='w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(column_names)
                writer.writerows(results)
            conn.close()
            
            messagebox.showinfo("Success", "Data exported successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

marker_workspace_obj = None

# Brings app back to home page
def init_home_page():
    global root,app,current_workspace,data_mode,marker_workspace_obj
    current_workspace = ""
    
    app.update_frame(Welcome.WelcomeWorkspace,PlaceHolderLowerRightPanel)
    app.update_sidebar()

# Open any paper
def init_workspace(workspace_name):
    global root,app,current_workspace,data_mode,marker_workspace_obj
    current_workspace = workspace_name

    (ans,remarks) = read_workspace_ans(workspace_name)
    (marker_workspace,marker_settings)=app.update_frame(Marker.Workspace,Marker.Settings)

    marker_workspace_obj=marker_workspace
    marker_workspace.update_answer_table(ans)

    app.update_sidebar()
    app.highlight_sidebar_button(workspace_name)

# Evaluates the selected paper from the selected workspace
def master_evaluate():
    global data_mode
    base_score = 0
    blank_ans_deduction = 0
    correct_ans_score = 1
    dynamic_pass = 0
    fixed_pass = -1
    wrong_ans_deduction = 0
    if data_mode == "set":
        # print(data_mode)
        # print(marker_workspace_obj.get_data_mode())
        # print(gSettings)
        try:
            if gSettings["base_score"]["Enabled"].get():
                base_score = float(gSettings["base_score"]["Value"].get())
            if gSettings["blank_ans_deduction"]["Enabled"].get():
                blank_ans_deduction = float(gSettings["blank_ans_deduction"]["Value"].get())
            if gSettings["correct_ans_score"]["Enabled"].get():
                correct_ans_score = float(gSettings["correct_ans_score"]["Value"].get())
            if gSettings["dynamic_pass"]["Enabled"].get():
                dynamic_pass = float(gSettings["dynamic_pass"]["Value"].get())
            if gSettings["fixed_pass"]["Enabled"].get():
                fixed_pass = float(gSettings["fixed_pass"]["Value"].get())
            if gSettings["wrong_ans_deduction"]["Enabled"].get():
                wrong_ans_deduction = float(gSettings["wrong_ans_deduction"]["Enabled"].get())
            
            if gSettings["fixed_pass"]["Enabled"].get() and gSettings["dynamic_pass"]["Enabled"].get():
                messagebox.showerror("Error","Custom fixed score pass and custom dynamic score pass cannot be both enabled at the same time.")
                return
        except ValueError:
            messagebox.showerror("Error","Invalid settings value")
            return
        result = evaluate_dataset_answers(current_workspace,gSetName.get(),base_score,correct_ans_score,blank_ans_deduction,wrong_ans_deduction)
        
        DatasetPerformancePopup(root.root,result)
    elif data_mode == "entry":
        if gSettings["dynamic_pass"]["Enabled"].get():
            messagebox.showerror("Error","Single data entry does not support dynamic pass function.")
            return
        try:
            if gSettings["base_score"]["Enabled"].get():
                base_score = float(gSettings["base_score"]["Value"].get())
            if gSettings["blank_ans_deduction"]["Enabled"].get():
                blank_ans_deduction = float(gSettings["blank_ans_deduction"]["Value"].get())
            if gSettings["correct_ans_score"]["Enabled"].get():
                correct_ans_score = float(gSettings["correct_ans_score"]["Value"].get())
            if gSettings["fixed_pass"]["Enabled"].get():
                fixed_pass = float(gSettings["fixed_pass"]["Value"].get())
            if gSettings["wrong_ans_deduction"]["Enabled"].get():
                wrong_ans_deduction = float(gSettings["wrong_ans_deduction"]["Enabled"].get())
            
            result = evaluate_entry_answers(current_workspace,gEntryName.get(),base_score,correct_ans_score,blank_ans_deduction,wrong_ans_deduction)
            DataEntryPerformancePopup(root.root,result)
            # print(result)

        except ValueError:
            messagebox.showerror("Error","Invalid settings value")
            return

# Creates grey object at the lower left corner of the home page
class PlaceHolderLowerRightPanel(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent,height=300,bg="#DDDDDD")
        
# Object that creates the About This App popup
class AboutPopup:
    def __init__(self, master):
        self.master = master
        self.popup = tk.Toplevel(master)
        self.popup.title("About This App")
        
        self.popup.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        license_text = (
            "MIT License\n\n"
            "Copyright (c) 2024 Javinleehm\n\n"
            "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
            "of this software and associated documentation files (the \"Software\"), to deal\n"
            "in the Software without restriction, including without limitation the rights\n"
            "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
            "copies of the Software, and to permit persons to whom the Software is\n"
            "furnished to do so, subject to the following conditions:\n\n"
            "The above copyright notice and this permission notice shall be included in all\n"
            "copies or substantial portions of the Software.\n\n"
            "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
            "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
            "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
            "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
            "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
            "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n"
            "SOFTWARE.\n\n"
            "This software is experimental and still in development.\n"
            "Version: 0.1.8"
        )
        # MIT Liscense from GitHub
        
        frame = ttk.Frame(self.popup, padding=(10, 10, 10, 10))
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text=license_text, justify=tk.LEFT)
        label.pack(expand=True)

        close_button = ttk.Button(frame, text="Close", command=self.popup.destroy)
        close_button.pack(pady=(10, 0))

# Placeholder popup for coming soon functions
class PlaceHolderPopup:
    def __init__(self,master):
        self.master = master
        self.popup = tk.Toplevel(master)
        self.popup.title("Coming soon")
        frame = tk.Frame(self.popup)
        frame.pack(padx=10,pady=10)
        self.title = ttk.Label(frame,text="Coming Soon!",font=("Helvetica",20,"normal"))
        self.title.pack(anchor="w")
        self.desc = ttk.Label(frame,text="This feature is currently still under development. A proper release version will be available once all functionalities are ready.",font=("Helvetica",10,"normal"))
        self.desc.pack(anchor="w")

# Debug button function
def button_test(text):
    print(f"Button {text} pressed!")

# Deprecated way of launching the app from another python file
def master_launch():
    root.mainloop()

# Define the tk root as a custom themed TKinter app and set the app to maximized fullscreen
root = TKMT.ThemedTKinterFrame("MCMAS","sun-valley","light")
root.root.state("zoomed")

# Apply the MCMAS app to the root and update the app rendering
app = MCMASApp(root.root)
app.update_frame(Welcome.WelcomeWorkspace,PlaceHolderLowerRightPanel)

# Global variable for storing which dataset or entry is selected
gSetName = tk.StringVar()
gEntryName = tk.StringVar()

# Global variable for storing evaluation settings
gSettings = {
    "fixed_pass":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    },
    "dynamic_pass":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    },
    "base_score":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    },
    "correct_ans_score":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    },
    "wrong_ans_deduction":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    },
    "blank_ans_deduction":{
        "Enabled" : tk.BooleanVar(),
        "Value" : tk.StringVar()
    }
}

# Custom function that handles tkinter errors so it can be caught easily
class TkExceptionHandler:
    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        if self.subst:
            args = self.subst(*args)
        return self.func(*args)

tk.CallWrapper = TkExceptionHandler

# Keeps the app running
if __name__ == "__main__":
    root.root.mainloop()