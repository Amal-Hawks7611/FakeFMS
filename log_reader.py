import sqlite3
import tkinter as tk
from tkinter import ttk

def fetch_match_records():
    conn = sqlite3.connect('match_records.db')
    c = conn.cursor()
    c.execute("SELECT * FROM match_log ORDER BY id")
    rows = c.fetchall()
    conn.close()
    matches = []
    i = 0
    while i < len(rows):
        if i + 1 < len(rows) and rows[i][2] == "Autonomous" and rows[i+1][2] == "Teleop":
            auto = rows[i]
            tele = rows[i+1]
            match_id = len(matches) + 1
            auto_score = auto[3]
            tele_score = tele[3]
            overall = auto_score + tele_score
            auto_details = f"L1:{auto[4]}, L2:{auto[5]}, L3:{auto[6]}, L4:{auto[7]}, PROCESSOR:{auto[8]}, TAKSI:{auto[9]}"
            tele_details = f"L1:{tele[4]}, L2:{tele[5]}, L3:{tele[6]}, L4:{tele[7]}, PROCESSOR:{tele[8]}, PARK:{tele[9]}"
            matches.append((match_id, tele[1], auto_score, tele_score, overall, auto_details, tele_details))
            i += 2
        else:
            i += 1
    return matches

def main():
    root = tk.Tk()
    root.title("Maç Kayıtları")
    tree = ttk.Treeview(root)
    tree["columns"] = ("match_id", "timestamp", "autonomous", "teleop", "overall", "auto_details", "tele_details")
    tree.column("#0", width=0, stretch=tk.NO)
    tree.column("match_id", anchor=tk.CENTER, width=60)
    tree.column("timestamp", anchor=tk.CENTER, width=150)
    tree.column("autonomous", anchor=tk.CENTER, width=100)
    tree.column("teleop", anchor=tk.CENTER, width=100)
    tree.column("overall", anchor=tk.CENTER, width=100)
    tree.column("auto_details", anchor=tk.CENTER, width=300)
    tree.column("tele_details", anchor=tk.CENTER, width=300)
    
    tree.heading("match_id", text="Maç ID", anchor=tk.CENTER)
    tree.heading("timestamp", text="Zaman", anchor=tk.CENTER)
    tree.heading("autonomous", text="Otonom", anchor=tk.CENTER)
    tree.heading("teleop", text="Teleop", anchor=tk.CENTER)
    tree.heading("overall", text="Genel", anchor=tk.CENTER)
    tree.heading("auto_details", text="Otonom Detay", anchor=tk.CENTER)
    tree.heading("tele_details", text="Teleop Detay", anchor=tk.CENTER)
    
    matches = fetch_match_records()
    for match in matches:
        tree.insert("", "end", values=match)
    
    tree.pack(expand=True, fill="both")
    root.mainloop()

if __name__ == "__main__":
    main()
