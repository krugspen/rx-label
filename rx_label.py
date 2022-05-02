import tkinter as tk                # python 3
from tkinter import *
from tkinter import font as tkfont  # python 3
import json
import datetime
from tkinter import ttk
import os
import csv

def loadDB(database):
    with open(database) as db :
        data = json.load(db)
    
    return data
    
    
def init():
    global rxTreeID
    global db
    db = loadDB('medications.json')
    
    if os.path.exists("prescription-csv.csv"):
        with open("prescription-csv.csv", "r") as ff, open("prescription-csv-history.csv","a") as sf:
            for line in ff:
                sf.write(line)
                
    
        ff.close()
        sf.close()
        os.remove("prescription-csv.csv")
    
class Application(tk.Frame):
    
    def __init__(self, master):
        tk.Frame.__init__(self,master)
        
        # Initialization 
        # ------------------------------------
        self.grid()
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        dateRaw = datetime.datetime.now()
        dateFormat = dateRaw.strftime("%m/%d")

        self.rxTreeID=0
        self.csvList = []
        self.saveDose=[]
        self.saveDur=[]
        
        
        # FRAME 1: Left side
        self.addInfoFrame = tk.Frame(self, padx=10, pady=10)
        
        # Name
        # ---------------------------------------
        self._name = tk.Label(self.addInfoFrame, text = "Name:")
        self._nameBox = tk.Entry(self.addInfoFrame)
        
        # Owner Last Name
        # ----------------------------------------
        self._oname = tk.Label(self.addInfoFrame, text = "Owner Last Name:")
        self._onameBox = tk.Entry(self.addInfoFrame)
        
        # A Number
        # ----------------------------------------
        self._anum = tk.Label(self.addInfoFrame, text = "Animal Number:")
        self._anumBox = tk.Entry(self.addInfoFrame)

        # Medication Drop Down
        # ----------------------------------------
        self.medLabel = tk.Label(self.addInfoFrame, text = "Medication:")
        self._medication = tk.StringVar()
        self.medication = ttk.Combobox(self.addInfoFrame, textvariable=self._medication)
        self.medication['values']=list(db.keys())
        # print(self.medication['values'])
        self.medication['state']='readonly'
        
        self.medication.current(0)
        
        self.medication.bind('<<ComboboxSelected>>', self.formChanged)
        
        self.medForm = db[self._medication.get()]["form"]
        
        # Dosage
        # ----------------------------------------
        self.doseLabel = tk.Label(self.addInfoFrame, text = "Dose:")
        self.doseBox = tk.Entry(self.addInfoFrame)
        self.doseBox.insert(0, "1")
        self.formLabel = tk.Label(self.addInfoFrame, text = self.medForm)
        
        # Duration
        # ----------------------------------------
        self.durType = IntVar()
        
        self.durationLabel = tk.Label(self.addInfoFrame, text = "Duration:")    
        self.durationBox = tk.Entry(self.addInfoFrame)
        self.durationBox.insert(0, "14")
        self.doseCheckbox = tk.Radiobutton(self.addInfoFrame, text = "doses", variable = self.durType, value=0)
        self.dayCheckbox = tk.Radiobutton(self.addInfoFrame, text = "days", variable = self.durType, value=1)
        
        # Starting Date
        # ----------------------------------------
        self.ampmType = IntVar()
        self.startingLabel = tk.Label(self.addInfoFrame, text = "Starting:")    
        self.startingBox = tk.Entry(self.addInfoFrame)
        self.startingBox.insert(0, dateFormat)
        self.amCheckbox = tk.Radiobutton(self.addInfoFrame, text = "am", variable = self.ampmType, value=0)
        self.pmCheckbox = tk.Radiobutton(self.addInfoFrame, text = "pm", variable = self.ampmType, value=1)

        # Buttons
        # ----------------------------------------
        self.addButton = tk.Button(self.addInfoFrame, text="Add", width=7, command=self.addToTree)
        self.previewButton = tk.Button(self.addInfoFrame, text="Preview", width=7,command=self.preview)
        self.updateButton=tk.Button(self.addInfoFrame, text="Update",  width=7, command=self.updateTreeItem, state=DISABLED)
        
        
        # Total Dose Label
        #--------------------------------------------
        self.calculate()
        
        self.totalDoseLabel = tk.Label(self.addInfoFrame, text = "Total Dose:")
        self.totalDoseCalc = tk.Entry(self.addInfoFrame)
        self.totalDoseCalc.insert(END, self.totalDose)
        
        # Instruction Text Box
        #--------------------------------------------
        self.instructionLabel = tk.Label(self.addInfoFrame, text="Instruction:")
        self.instructionBox = tk.Text(self.addInfoFrame, width=70, height=3, wrap=WORD)
        self.instructionBox.insert(END, self.instruction)
        
        self.blankLine = tk.Label(self.addInfoFrame, width=3, height=2)
        self.blankLine1 = tk.Label(self.addInfoFrame, width=3, height=1)
        
        
        # TreeView
        #----------------------------------------------
        self.tree_frame = Frame(self, padx=10, pady=10)
        
        self.tree_scroll = Scrollbar(self.tree_frame)
        
        
        self.rx_tree = ttk.Treeview(self.tree_frame, height = 20, yscrollcommand=self.tree_scroll.set)
        self.rx_tree['columns'] = ("Date", "Name", "Owner", "Animal Number", "Medication", "Total Dose", "Instruction")
        self.rx_tree.column("#0", width=0)
        self.rx_tree.column("Date", minwidth=40, width=60, anchor=CENTER)
        self.rx_tree.column("Name", minwidth=80, width=100, anchor=CENTER)
        self.rx_tree.column("Owner", minwidth=80, width=100, anchor=CENTER)
        self.rx_tree.column("Animal Number", minwidth=80, width=100, anchor=CENTER)
        self.rx_tree.column("Medication", minwidth=80, width=100, anchor=CENTER)
        self.rx_tree.column("Total Dose", minwidth=70, width=70, anchor=CENTER)
        self.rx_tree.column("Instruction", width=120, anchor=CENTER)
        
        self.rx_tree.heading("Date", text="Date", anchor=CENTER)
        self.rx_tree.heading("Name", text="Name", anchor=CENTER)
        self.rx_tree.heading("Owner", text="Owner", anchor=CENTER)
        self.rx_tree.heading("Animal Number", text="Animal Number", anchor=CENTER)
        self.rx_tree.heading("Medication", text="Medication", anchor=CENTER)
        self.rx_tree.heading("Total Dose", text="Total Dose", anchor=CENTER)
        self.rx_tree.heading("Instruction", text="Instruction", anchor=CENTER)
        
        self.tree_scroll.config(command=self.rx_tree.yview)
        
        self.rx_tree.bind("<<TreeviewSelect>>", self.toggleButton)
        
        # Edit/Save Button
        #-----------------------------
        self.deleteButton = tk.Button(self, text="Delete", command=self.deleteTreeItem, width=5, state=DISABLED)
        self.editButton = tk.Button(self, text="Edit", command=self.editTreeItem, width=5, state=DISABLED)
        self.saveButton = tk.Button(self, text="Save", command=self.addToCSV, width=5, state=DISABLED)
        
        
        
        self.blankRow1 = tk.Label(self, width=4, height=1)
        self.blankColumn = tk.Label(self, width=4, text = " ")
        
        
        
        
        # ----------------------------------------
        # Grid Design
        # ----------------------------------------
        rownum = 0
        
        self.addInfoFrame.grid(row=0, column=0)
        
        
                
        self._name.grid(row = rownum, column = 0, sticky=W)
        self._nameBox.grid(row = rownum, column = 1, sticky=W)
        rownum+=1
        
        self._oname.grid(row = rownum, column = 0, sticky=W)
        self._onameBox.grid(row = rownum, column = 1, sticky=W)
        rownum+=1
        
        
        self._anum.grid(row = rownum, column = 0, sticky=W)
        self._anumBox.grid(row = rownum, column = 1, sticky=W)
        rownum+=1
       
        self.blankLine.grid(row=rownum,column=0)
        rownum+=1
       
        self.medLabel.grid(row = rownum, column = 0, sticky=W)
        self.medication.grid(row = rownum, column = 1, columnspan = 1, sticky = W)
        
        
        self.blankColumn.grid(row=0, column=4, rowspan=20)
        
        self.previewButton.grid(row=rownum, column = 5, sticky=E)
        self.addButton.grid(row=rownum+1, column = 5, sticky=E)
        self.updateButton.grid(row=rownum+2, column = 5, sticky=E)
        rownum+=1
        
        
        
        self.doseLabel.grid(row=rownum, column = 0, sticky=W)
        self.doseBox.grid(row=rownum, column = 1, sticky=W)
        self.formLabel.grid(row = rownum, column = 2, sticky=W)
        rownum+=1
        
        self.durationLabel.grid(row=rownum,column=0, sticky=W)
        self.durationBox.grid(row=rownum,column=1, sticky=W)
        self.doseCheckbox.grid(row=rownum, column = 2, sticky=W)
        self.dayCheckbox.grid(row=rownum, column = 3, sticky=W)
        rownum+=1
       
       
    

        self.startingLabel.grid(row=rownum, column=0, sticky=W)
        self.startingBox.grid(row=rownum, column=1, sticky=W)
        self.amCheckbox.grid(row=rownum, column=2, sticky=W)
        self.pmCheckbox.grid(row=rownum, column=3, sticky=W)
        rownum+=1

        self.blankRow1.grid(row=rownum,column=0)
        rownum+=1
        

        
        self.blankLine1.grid(row=rownum, column=0)
        rownum+=1
        
        self.totalDoseLabel.grid(row=rownum, column=0, sticky=W)
        self.totalDoseCalc.grid(row=rownum, column=1, sticky=W)
        rownum+=1

        self.instructionLabel.grid(row=rownum, column=0, sticky=W, pady=5)
        rownum+=1
        
        self.instructionBox.grid(row=rownum, column=0, padx=20, columnspan=4)


        self.tree_frame.grid(row = 0, column = 1, rowspan=20)
        # self.tree_scroll.grid(row=0, column=1, rowspan=20)
        self.rx_tree.grid(row=0,column=1, rowspan=20)
        self.deleteButton.grid(row=1,column=2, sticky=W)
        self.editButton.grid(row=2,column=2, sticky=W)
        self.saveButton.grid(row=3,column=2, sticky=W)


    def toggleButton(self, event):
        self.deleteButton['state']=NORMAL
        self.editButton['state']=NORMAL
    
    # ==================================================== #
    # Function:                                            #
    # Description:                                         #
    #                                                      #
    # ==================================================== #
    def preview(self):
        self.calculate()
                
        # self.loadToScreen()
        # Insert basic text instructions to text box
        self.instructionBox.delete('1.0', END)
        self.instructionBox.insert(END, self.instruction)
        
        self.totalDoseCalc.delete(0, END)
        self.totalDoseCalc.insert(END, self.totalDose)
    
    
    def addToTree(self):
        self.calculate()
               
        # Get modified instruction if exists
        self.instrMod = self.instructionBox.get(1.0, "end-1c")
        
        # Get modified total soe
        self.totalDoseMod = self.totalDoseCalc.get()
        
        # Display information in Tree
        self.rx_tree.insert(parent='', index='end', iid=self.rxTreeID, text="Parent", values=(
            self.startingBox.get(),
            self._nameBox.get(), 
            self._onameBox.get(), 
            self._anumBox.get(),
            self._medication.get(),
            self.totalDoseMod,
            self.instrMod))        
        self.rxTreeID+=1
        
        
        # Save dose and duration to edit
        self.saveDose.append(self.doseBox.get())
        self.saveDur.append(self.durationBox.get())
        
        self.saveButton['state']=NORMAL
    
    
    def addToCSV(self):
        #self.calculate()
        
        file = open("prescription-csv.csv", "w", newline='', encoding='utf-8')
        
        
        for child in self.rx_tree.get_children():
            print(self.rx_tree.item(child)["values"])
            instr = self.rx_tree.item(child)["values"][6]
            write = csv.writer(file, delimiter=',')
            write.writerow(self.rx_tree.item(child)["values"])

        file.close()
        
        self.saveButton['state']=DISABLED
        
    
    def deleteTreeItem(self):
        curItems=self.rx_tree.selection()
        for item in curItems:
            self.rx_tree.delete(item)
            
        self.saveButton['state']=NORMAL
        self.editButton['state']=DISABLED
        self.deleteButton['state']=DISABLED

    def editTreeItem(self):
        self.addButton['state']=DISABLED
        self.updateButton['state']=NORMAL
        
        self.curItem=self.rx_tree.focus()
        
        # self.editButton['state']=NORMAL
        
        values=self.rx_tree.item(self.curItem)['values']

        self._nameBox.delete(0, END)
        self._onameBox.delete(0, END)
        self._anumBox.delete(0, END)
        self.doseBox.delete(0,END)
        self.durationBox.delete(0, END)
        self.startingBox.delete(0, END)
        self.instructionBox.delete('1.0', END)
        
        self._nameBox.insert(END,values[1])
        self._onameBox.insert(END,values[2])
        self._anumBox.insert(END, values[3])
        self.medication.set(values[4])
        self.doseBox.insert(END,self.saveDose[int(self.curItem)])
        self.durationBox.insert(END,self.saveDur[int(self.curItem)])
        self.startingBox.insert(END,values[0])
        self.instructionBox.insert(END, values[6])
        
        
    
    def updateTreeItem(self):
        self.calculate()
        self.rx_tree.item(self.curItem, values =(
            self.startingBox.get(),
            self._nameBox.get(), 
            self._onameBox.get(), 
            self._anumBox.get(),
            self._medication.get(),
            self.totalDose,
            self.instructionBox.get(1.0, "end-1c")))  
                    
        self.updateButton['state']=DISABLED
        self.addButton['state']=NORMAL
        self.saveButton['state']=NORMAL
        self.editButton['state']=DISABLED
        self.deleteButton['state']=DISABLED
    
    
    # ==================================================== #
    # Function:                                            #
    # Description:                                         #
    #                                                      #
    # ==================================================== #    
    def calculate(self):
        
        # Get current date for entry
        dateRaw = datetime.datetime.now()
        self.dateFormat = dateRaw.strftime("%m/%d/%Y")
        
        
        # Calculate Dose
        frequency = db[self._medication.get()]["frequency"]
        
        if self.durType.get() == 0: #dose 
            self.totalDose = float(self.doseBox.get()) * int(self.durationBox.get())
        elif self.durType.get() == 1: #days
            self.totalDose = float(self.doseBox.get()) * int(frequency) * int(self.durationBox.get())
        
        
        # Calculate how often to administer
        if frequency == 1:
            everyHours = 24
        elif frequency == 2:
            everyHours = 12
        
        
        
        
        # Format Instruction String (create CSV)
        #--------------------------------
        instructionRaw = db[self._medication.get()]["instruction"]
        
        self.instruction = instructionRaw.replace("DOSE", self.doseBox.get() + " " + self.medForm)
        self.instruction = self.instruction.replace("SID/BID", str(everyHours))
        self.instruction = self.instruction.replace("DATE", self.startingBox.get())
        if self.ampmType.get() == 0: #AM
            self.instruction = self.instruction.replace("AMPM", "AM")
        elif self.ampmType.get() == 1: #PM
            self.instruction = self.instruction.replace("AMPM", "PM")
        
        
        ##########################################################
        # TEST
        # Concatenate Preview Text




    # ==================================================== #
    # Function:                                            #
    # Description:                                         #
    #                                                      #
    # ==================================================== #
    
    def formChanged(self, *args):
        self.medForm = db[self._medication.get()]["form"]
        self.formLabel['text'] = self.medForm
        
        self.calculate()
        self.instructionBox.delete('1.0', END)
        self.instructionBox.insert(END, self.instruction)
        
        
        
if __name__ == "__main__":
    init()
    window = tk.Tk()
    window.title("Prescription Label Maker")
    window.geometry("1600x600")
    app = Application(window)
    window.mainloop()
