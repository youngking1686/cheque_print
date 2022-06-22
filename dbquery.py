import sqlite3
import os, config


mainfolder = config.mainfolder

if not os.path.isfile('app.db'):
    conn = sqlite3.connect('app.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS issue_to (
            id INTEGER PRIMARY KEY, 
            chk_to NOT NULL UNIQUE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dept (
            id INTEGER PRIMARY KEY, 
            dept NOT NULL UNIQUE,
            balance NOT NULL
        )
    """)
    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS account_balance (
    #         id INTEGER PRIMARY KEY, 
    #         balance NOT NULL UNIQUE
    #     )
    # """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            vch_num,
            chk_to NOT NULL, 
            particulars,
            chk_date NOT NULL,
            dept NOT NULL,
            amount NOT NULL,
            cheque_no NOT NULL UNIQUE,
            dept_avl_bal,
            remarks
        )
    """)
    with open('{}/temp/PARTY_NAME.csv'.format(mainfolder), 'r') as f:
        Party_name = [line.strip() for line in f]
    for value in Party_name:
        cur.execute("""INSERT INTO issue_to (chk_to) VALUES (?)""", (value,))
    
    with open('{}/temp/DEPARTMENT.csv'.format(mainfolder), 'r') as f:
        dept_name = [line.strip() for line in f]
    for value in dept_name:
        value = value.split(',')
        cur.execute("""INSERT INTO dept (dept, balance) VALUES (?, ?)""", (value[0],value[1], ))
    # cur.execute("""INSERT INTO account_balance (balance) VALUES (?)""", ('0',))
    conn.commit()


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.conn.commit()

    def fetch_all(self):
        self.cur.execute("""SELECT * FROM history""")
        rows = self.cur.fetchall()
        return rows

    def insert(self, vch_num, chk_to, particulars, chk_date, dept, amount, cheque_no, dept_avl_bal, remarks):
        self.cur.execute("""INSERT INTO history (vch_num, chk_to, particulars, chk_date, dept, amount, cheque_no, dept_avl_bal, remarks)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", (vch_num, chk_to, particulars, chk_date, dept, amount, cheque_no, dept_avl_bal, remarks,))
        self.conn.commit()

    def insert_issue_to(self, chk_to):
        self.cur.execute("""INSERT INTO issue_to (chk_to) VALUES (?)""", (chk_to,))
        self.conn.commit()
    
    def insert_dept(self, dept):
        self.cur.execute("""INSERT INTO dept (dept, balance) VALUES (?, ?)""", (dept, '0'))
        self.conn.commit()
        
    def remove_issue_to(self, chk_to):
        self.cur.execute("DELETE FROM issue_to WHERE chk_to=?", (chk_to,))
        self.conn.commit()

    def remove_dept(self, dept):
        self.cur.execute("DELETE FROM dept WHERE dept=?", (dept,))
        self.conn.commit()
        
    def fetch_issue(self):
        self.cur.execute("SELECT * FROM issue_to")
        rows = self.cur.fetchall()
        rows = list(zip(*rows))[1]
        return rows
    
    def fetch_dept(self):
        self.cur.execute("SELECT * FROM dept")
        rows = self.cur.fetchall()
        rows = list(zip(*rows))[1]
        return rows
    
    def fetch_balance(self, dept):
        self.cur.execute("SELECT * FROM dept WHERE dept = ? ",(dept,))
        rows = self.cur.fetchall()[0][2]
        return rows
    
    def update_balance(self, balance,dept):
        self.cur.execute("UPDATE dept SET balance = ? WHERE dept = ?", (balance,dept, ))
        self.conn.commit()
        
    def fetch_chk_sum(self, dept):
        self.cur.execute("SELECT SUM(amount) FROM history WHERE dept = ?", (dept, ))
        return float(self.cur.fetchall()[0][0])

    def __del__(self):
        self.conn.close()