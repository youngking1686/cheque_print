import tkinter as tk
from tkinter import ttk, messagebox, OptionMenu
import tkinter.scrolledtext as scrolledtext
from tkinter.constants import CENTER, NORMAL
from turtle import width
from PIL import Image, ImageTk
from PIL import ImageDraw, ImageFont
import config, sqlite3, os
import babel.numbers
from dbquery import Database
from functools import partial
import tabulate
from tkcalendar import DateEntry
from num2words import num2words
import pandas as pd

db = Database('app.db')
mainfolder = config.mainfolder

root = tk.Tk() #Start Tkinter UI async 
root.minsize(1000,610)
root.title("Cheque Print")
root.resizable(width=False, height=False)
tabControl = ttk.Notebook(root)

#Define Variables
chk_to = tk.StringVar()
dept = tk.StringVar()
amount = tk.StringVar()
cheque_no = tk.StringVar()
chk_date = tk.StringVar()
remarks = tk.StringVar()
chk_to_1 = tk.StringVar()
dept_1 = tk.StringVar()
dept_b = tk.StringVar()
start_balance = tk.StringVar()
user = tk.StringVar()
password = tk.StringVar()
dept_balance = tk.StringVar()
vch_num = tk.StringVar()
particulars = tk.StringVar()

issue_lst = db.fetch_issue()
dept_lst = db.fetch_dept()

class Action:
    def add_issue_to(): #To add Party Name to the db
        global issue_lst
        db.insert_issue_to(chk_to_1.get())
        issue_lst = db.fetch_issue()
        OptionMenu(tab1, chk_to, *issue_lst ).grid(row=1,column=2, padx=5, pady=15)
        messagebox.showinfo("Added", "Party Name added")
        
    def remove_issue_to(): #To remove the party name from db
        global issue_lst
        db.remove_issue_to(chk_to_1.get())
        issue_lst = db.fetch_issue()
        OptionMenu(tab1, chk_to, *issue_lst ).grid(row=1,column=2, padx=5, pady=15)
        messagebox.showinfo("Removed", "Removed Party Name")
        
    def add_dept(): #To add the department name to db
        global dept_lst
        db.insert_dept(dept_1.get())
        dept_lst = db.fetch_dept()
        OptionMenu(tab1 , dept , *dept_lst).grid(row=2,column=2, columnspan= 4, padx=5, pady=10)
        messagebox.showinfo("Added", "Department Added")
        
    def remove_dept(): #To remove the department name from db
        global dept_lst
        db.remove_dept(dept_lst.get())     
        dept_lst = db.fetch_dept()
        OptionMenu(tab1 , dept , *dept_lst).grid(row=2,column=2, columnspan= 4, padx=5, pady=10)
        messagebox.showinfo("Removed", "Removed Department")
        
    def save_balance(): #To enter the starting balance
        db.update_balance(start_balance.get(), dept_b.get())
        messagebox.showinfo("Saved", "Start Balance Saved")
           
    def get_hist(): #To get the history of cheques generated
        ttk.Label(tab2, text = 'Issue History', font = ('calibre',10,'bold')).grid(row=2,column=1, padx=8, pady=5)
        txt2 = scrolledtext.ScrolledText(tab2, undo=True, wrap='word', height = 20, width = 150, bg="gray")
        txt2['font'] = ('consolas', '8')
        txt2.grid(row=3,column = 1, columnspan=6, padx=10, pady=8)
        logs = db.fetch_all() # from db
        try:
            df = pd.DataFrame(logs, columns =['no.', 'Voucher\nno.', 'To' , 'Particulars', 'Date', 'Department', 'Amount', 'Cheque\nNumber', 'Dept Avl\nBalance', 'remarks'])
            df['To'] = df['To'].str.wrap(15)
            df['Particulars'] = df['Particulars'].str.wrap(15)
            df['Department'] = df['Department'].str.wrap(15)
            df['remarks'] = df['remarks'].str.wrap(15)
            df['Date'] = pd.to_datetime(df.Date, format='%m/%d/%y')
            df['Date'] = df['Date'].dt.strftime('%d/%m/%y')
            sho = df.to_markdown(showindex=False)
            df.to_excel("Issued_History.xlsx", index=False)
            txt2.insert(tk.INSERT,sho)
        except TypeError:
            pass
             
    def add_text(I, img, amount, chk_date, chk_to): #Adds the overlay of text on to the Cheque template
        amount_words = num2words(int(amount), to='cardinal', lang='en_IN') + ' Rupees Only'
        if len(amount_words) > 8: #Splits the sentence to fit the amount field of the cheque
            amount_words = amount_words.split()[:8] + ['\n\n'] + amount_words.split()[8:]
            str1 = " "
            amount_words = str1.join(amount_words)
            
        prnt_ls = chk_date.split('/')
        mnt = '0  ' + prnt_ls[0] if len(prnt_ls[0]) < 2 else prnt_ls[0][0] + '  ' + prnt_ls[0][1]
        dat = '0  ' + prnt_ls[1] if len(prnt_ls[1]) < 2 else prnt_ls[1][0] + '  ' + prnt_ls[1][1]
        prnt_dt = dat + '  ' +  mnt + ' ' + ' 2  0 ' + prnt_ls[2][0] + '  ' + prnt_ls[2][0]
        
        
        font1 = ImageFont.truetype("arial.ttf", 17, encoding="unic")
        font2 = ImageFont.truetype("arial.ttf", 14, encoding="unic")
        ##TEXT Alignment on the cheque leaf
        I.text((120, 62), chk_to.upper(), fill=(0, 0, 0), font=font2) #X,Y Alignment of party name on the cheque template
        I.text((640, 22), prnt_dt, fill=(0, 0, 0), font=font1) #X,Y Alignment of Date on the cheque template
        I.text((175, 90), amount_words.upper(), fill=(0, 0, 0), font=font2) #X,Y Alignment of Amount in words on the cheque template
        I.text((645, 117), amount, fill=(0, 0, 0), font=font1) #X,Y Alignment of Amount in numbers on the cheque template
        ##CHANGE X,Y values of the above 4 lines to align with the template, can be used if anyother template is used.
        return img
                
    def save_d(preview): #Saves preview and reference of ready cheque and makes the print template to print on to the actual cheque
        if chk_to.get() == "" or dept.get()=="" or amount.get()=="" or \
            cheque_no.get()=="" or remarks.get()=="" or chk_date.get()=="":
            messagebox.showerror("Error in Input", "Required Fields cannot be empty")
            return
        else:
            img = Image.open('{}/image/Template.png'.format(mainfolder))
            I1 = ImageDraw.Draw(img)
            img = Action.add_text(I1, img, amount.get(), chk_date.get(), chk_to.get())
            # img.show()
            
            photo = ImageTk.PhotoImage(img)
            labelx = ttk.Label(tab1, image=photo)
            labelx.grid(row=3,column=1, columnspan=6, padx=20, pady=20)
            labelx.image1 = photo
            labelx.place(x=15, y=250)
            
            # Save the edited image
            if preview != 'y':
                try:
                    try:
                        spent = float(db.fetch_chk_sum(dept.get())) + float(amount.get())
                    except:
                        spent = float(amount.get())
                    start_bal = float(db.fetch_balance(dept.get()))
                    curr_bal = start_bal - spent
                    db.update_balance(curr_bal, dept.get())
                    db.insert(vch_num.get(), chk_to.get(), particulars.get(), chk_date.get(), dept.get(), amount.get(), cheque_no.get(), curr_bal, remarks.get())
                             
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Cheque number already exist")
                    return
                img2 = Image.open('{}/image/blank.png'.format(mainfolder))
                I2 = ImageDraw.Draw(img2)
                img2 = Action.add_text(I2, img2, amount.get(), chk_date.get(), chk_to.get())
                im_2 = img2.convert('RGB')
                # im_2.save('{}/print/cheque_no-{}.pdf'.format(mainfolder, cheque_no.get()))
                # os.startfile('{}/print/cheque_no-{}.pdf'.format(mainfolder, cheque_no.get()))
                im_2.save('{}/print/cheque_no-{}.png'.format(mainfolder, cheque_no.get()))
                os.startfile('{}/print/cheque_no-{}.png'.format(mainfolder, cheque_no.get()))
                messagebox.showinfo("Success", "Print ready")
    
    def get_dept_bal():
        try:
            start_balance.set(db.fetch_balance(dept_b.get()))
        except:
            pass
        
    def update_dept_balance(dept):
        try:
            dept_balance.set(db.fetch_balance(dept))
        except:
            pass
                    
    def on_closing():
        if messagebox.askyesno("Quit", "Do you want to quit?"):
            root.destroy()        
            
    def login(win):
        if user.get() == 'FADMIN' and password.get() == 'FADMIN':
            gui_contents.add_details()
            gui_contents.main_form()
            gui_contents.logs()
            win.destroy()
        else:
            messagebox.showerror("Login Error", "Wrong User or Password!")
            
class gui_contents:
             
    def tabs():
        tabControl.add(tab0, text ='Update Data')
        tabControl.add(tab1, text ='Make Cheque')
        tabControl.add(tab2, text ='Get History')
        tabControl.pack(expand = 1, fill ="both", padx = 20)
    
    def add_details():
        ttk.Label(tab0, text = '-------Add/Remove Party & Department--------', font=('calibre',10, 'bold')).grid(row=1,column=1, columnspan= 4, padx=10, pady=15)
        ttk.Label(tab0, text = 'Party Name', font=('calibre',10, 'bold')).grid(row=2,column=1, padx=10, pady=15)
        ttk.Entry(tab0, textvariable = chk_to_1, font=('calibre',10,'normal'), state='enabled').grid(row=2,column=2, padx=3, pady=15)
        ttk.Label(tab0, text = 'Department', font = ('calibre',10,'bold')).grid(row=3,column=1, padx=10, pady=10)
        ttk.Entry(tab0, textvariable = dept_1, font = ('calibre',10,'normal'), state='enabled').grid(row=3,column=2, padx=3, pady=10)
        ttk.Button(tab0, text = 'Add', command = Action.add_issue_to, width=10, state='enabled').grid(row=2,column=3, padx=40, pady=10)
        ttk.Button(tab0, text = 'Remove', command = Action.remove_issue_to, width=10, state='enabled').grid(row=2,column=4, padx=40, pady=10)
        ttk.Button(tab0, text = 'Add', command = Action.add_dept, width=10, state='enabled').grid(row=3,column=3, padx=40, pady=10)
        ttk.Button(tab0, text = 'Remove', command = Action.remove_dept, width=10, state='enabled').grid(row=3,column=4, padx=40, pady=10)
        ttk.Label(tab0, text = '--------Edit Departmental Balance---------', font = ('calibre',10,'bold')).grid(row=4,column=1, columnspan= 4, padx=5, pady=10)
        ttk.Label(tab0, text = 'Select Department', font = ('calibre',10,'bold')).grid(row=5,column=1, padx=5, pady=10)
        OptionMenu(tab0, dept_b, *dept_lst).grid(row=5,column=2, columnspan= 4, padx=5, pady=10)
        ttk.Label(tab0, text = 'Department Balance', font = ('calibre',10,'bold')).grid(row=6,column=1, padx=10, pady=10)
        ttk.Entry(tab0, textvariable = start_balance, font = ('calibre',10,'normal'), state='enabled').grid(row=6,column=2, padx=3, pady=10)
        ttk.Button(tab0, text = 'Check', command = Action.get_dept_bal, width=10, state='enabled').grid(row=7,column=1, padx=40, pady=10)
        ttk.Button(tab0, text = 'Save', command = Action.save_balance, width=10, state='enabled').grid(row=7,column=2, padx=40, pady=10)
        
    def main_form():
        ttk.Label(tab1, text = 'Party Name', font=('calibre',10, 'bold')).grid(row=1,column=1, padx=5, pady=15)
        OptionMenu(tab1, chk_to, *issue_lst ).grid(row=1,column=2,columnspan= 4, padx=10, pady=15)
        
        ttk.Label(tab1, text = 'Department', font = ('calibre',10,'bold')).grid(row=2,column=1, padx=10, pady=10)
        OptionMenu(tab1 , dept , *dept_lst, command=Action.update_dept_balance).grid(row=2,column=2, columnspan= 4, padx=10, pady=10)
        
        ttk.Label(tab1, text = 'Cheque\nNumber', font = ('calibre',10,'bold')).grid(row=1,column=5, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = cheque_no, font = ('calibre',10,'normal'), state='enabled').grid(row=1,column=6, padx=10, pady=15)
        
        ttk.Label(tab1, text= "Date", font=('calibre',10, 'bold')).grid(row=2,column=5, padx=10, pady=10)
        cal = DateEntry(tab1, textvariable = chk_date, width= 10, foreground= "white",bd=2)
        cal.grid(row=2,column=6, padx=5, pady=10)

        ttk.Label(tab1, text = 'Amount', font = ('calibre',10,'bold')).grid(row=3,column=1, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = amount, font = ('calibre',10,'normal'), state='enabled').grid(row=3,column=2, padx=10, pady=10)

        ttk.Label(tab1, text = 'Available\nDepartment Balance', font = ('calibre',10,'bold')).grid(row=3,column=3, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = dept_balance, font = ('calibre',10,'normal'), state='disabled').grid(row=3, column=4, padx=10, pady=10)
        
        ttk.Label(tab1, text = 'Voucher\nnumber', font = ('calibre',10,'bold')).grid(row=3,column=5, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = vch_num, font = ('calibre',10,'normal'), state='enabled').grid(row=3, column=6, padx=10, pady=10)
        
        ttk.Label(tab1, text = 'Particulars', font = ('calibre',10,'bold')).grid(row=4,column=1, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = particulars, font = ('calibre',10,'normal'), state='enabled', width=55).grid(row=4, column=2, columnspan=4, padx=10, pady=10)
        
        ttk.Label(tab1, text = 'Remarks', font = ('calibre',10,'bold')).grid(row=4,column=5, padx=10, pady=10)
        ttk.Entry(tab1, textvariable = remarks, font = ('calibre',10,'normal'), state='enabled').grid(row=4,column=6, padx=10, pady=10)
        
        preview_com = partial(Action.save_d, 'y')
        print_com = partial(Action.save_d, 'n')
        ttk.Button(tab1, text = 'Preview', command = preview_com, width=15, state='enabled').grid(row=5,column=4, padx=5, pady=10)
        ttk.Button(tab1, text = 'Print', command = print_com, width=15, state='enabled').grid(row=5,column=6, padx=5, pady=10)
    
        image1 = Image.open('{}/image/Template.png'.format(mainfolder))
        photo = ImageTk.PhotoImage(image1)
        labelx = ttk.Label(tab1, image=photo)
        labelx.grid(row=3,column=1, columnspan=6, padx=20, pady=20)
        labelx.image1 = photo
        labelx.place(x=15, y=250)
        
    def logs():
        ttk.Button(tab2, text = 'Get History', command = Action.get_hist, width=15, state='enabled').grid(row=1,column=1, padx=40, pady=10)
        
    def tab_contents():
        win = tk.Toplevel()
        win.attributes('-topmost', 'true')
        win.wm_title("Login")
        win.resizable(width=False, height=False)
        ttk.Label(win, text = 'User', font = ('calibre',10,'bold')).grid(row=1,column=1, padx=5, pady=10)
        ttk.Entry(win, textvariable = user, font = ('calibre',10,'normal'), state='enabled').grid(row=1,column=2, padx=5, pady=10)
        ttk.Label(win, text = 'Password', font = ('calibre',10,'bold')).grid(row=2,column=1, padx=5, pady=10)
        ttk.Entry(win, textvariable = password, font = ('calibre',10,'normal'), state='enabled').grid(row=2,column=2, padx=5, pady=10)
        login = partial(Action.login, win)
        ttk.Button(win, text = 'Login', command = login, width=15, state='enabled').grid(row=3,column=2, padx=5, pady=10)

tab0 = ttk.Frame(tabControl)
tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

gui_contents.tabs()
gui_contents.tab_contents()

if __name__=='__main__':
    root.protocol("WM_DELETE_WINDOW", Action.on_closing)
    root.mainloop()