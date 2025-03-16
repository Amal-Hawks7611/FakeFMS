import sqlite3
import pyautogui
import time
import pygame
import datetime
import threading
import tkinter as tk

def init_db():
    conn = sqlite3.connect('match_records.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS match_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mode TEXT,
            total_score INTEGER,
            L1 INTEGER,
            L2 INTEGER,
            L3 INTEGER,
            L4 INTEGER,
            PROCESSOR INTEGER,
            PARK INTEGER,
            TAKSI INTEGER
        )
    ''')
    conn.commit()
    return conn

def log_phase_result(conn, mode, total, scores):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c = conn.cursor()
    c.execute("""
        INSERT INTO match_log (timestamp, mode, total_score, L1, L2, L3, L4, PROCESSOR, PARK, TAKSI)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (timestamp, mode, total, 
          scores.get("L1", 0),
          scores.get("L2", 0),
          scores.get("L3", 0),
          scores.get("L4", 0),
          scores.get("PROCESSOR", 0),
          scores.get("PARK", 0),
          scores.get("TAKSI", 0)))
    conn.commit()
    print(f"Logged {mode} result at {timestamp}: Total={total}, Scores={scores}")

def play_sound(sound_file):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("Ses çalma hatası:", e)

AUTO_MODE_POS = (100, 930)
TELEOP_MODE_POS = (200, 900)

def select_autonomous_mode(conn):
    pyautogui.click(AUTO_MODE_POS[0], AUTO_MODE_POS[1])
    print("Otonom mod seçildi.")

def select_teleoperated_mode(conn):
    pyautogui.click(TELEOP_MODE_POS[0], TELEOP_MODE_POS[1])
    print("Teleop mod seçildi.")

def enable_robot(conn, current_mode):
    pyautogui.press(']')
    pyautogui.press('\\')
    print("Robot Enabled")
    
def disable_robot(conn, current_mode):
    pyautogui.press('enter')
    print("Robot Disabled")

def emergency_stop(conn, current_mode):
    pyautogui.press('space')
    print("Emergency Stop Activated")
    play_sound("sounds/ENDMATCH.mp3")

def run_phase(conn, mode, duration, multipliers, last30_sound=False):
    root = tk.Tk()
    root.title(f"{mode} Süre ve Skor")
    timer_label = tk.Label(root, text="", font=("Helvetica", 48))
    timer_label.grid(row=0, column=0, columnspan=4, pady=10)
    scores = {slot: 0 for slot in multipliers.keys()}
    slot_labels = {}
    row_index = 1
    for slot in multipliers.keys():
        tk.Label(root, text=slot, font=("Helvetica", 14)).grid(row=row_index, column=0, padx=5, pady=5)
        count_label = tk.Label(root, text="0", font=("Helvetica", 14))
        count_label.grid(row=row_index, column=1, padx=5, pady=5)
        slot_labels[slot] = count_label
        tk.Button(root, text="+", font=("Helvetica", 14),
                  command=lambda s=slot: update_score(s, 1)).grid(row=row_index, column=2, padx=5, pady=5)
        tk.Button(root, text="-", font=("Helvetica", 14),
                  command=lambda s=slot: update_score(s, -1)).grid(row=row_index, column=3, padx=5, pady=5)
        row_index += 1
    total_label = tk.Label(root, text="Toplam Skor: 0", font=("Helvetica", 16))
    total_label.grid(row=row_index, column=0, columnspan=4, pady=10)
    
    def update_score(slot, delta):
        scores[slot] += delta
        if scores[slot] < 0:
            scores[slot] = 0
        slot_labels[slot].config(text=str(scores[slot]))
        update_total_score()
    
    def update_total_score():
        total = sum(scores[slot] * multipliers[slot] for slot in scores)
        total_label.config(text=f"Toplam Skor: {total}")
    
    start_time = time.time()
    end_time = start_time + duration
    played_last_30 = False

    def update_timer():
        nonlocal played_last_30
        remaining = int(end_time - time.time())
        if remaining < 0:
            remaining = 0
        minutes = remaining // 60
        seconds = remaining % 60
        timer_label.config(text=f"Kalan Süre: {minutes}:{seconds:02d}")
        if last30_sound and remaining <= 30 and not played_last_30:
            played_last_30 = True
            threading.Thread(target=play_sound, args=("sounds/last-30.mp3",)).start()
        if remaining > 0:
            root.after(1000, update_timer)
        else:
            disable_robot(conn, mode)
            total = sum(scores[slot] * multipliers[slot] for slot in scores)
            log_phase_result(conn, mode, total, scores)
            root.destroy()
            play_sound("sounds/ENDMATCH.mp3")
    update_timer()
    root.mainloop()
    total = sum(scores[slot] * multipliers[slot] for slot in scores)
    return scores, total

if __name__ == "__main__":
    conn = init_db()
    current_mode = "Autonomous"
    select_autonomous_mode(conn)
    time.sleep(1)
    play_sound("sounds/match_start.mp3")
    enable_robot(conn, current_mode)
    scores_auto, total_auto = run_phase(conn, current_mode, duration=15, multipliers={
        "L1": 3,
        "L2": 4,
        "L3": 6,
        "L4": 7,
        "PROCESSOR": 6,
        "TAKSI": 3
    }, last30_sound=False)
    time.sleep(1)
    current_mode = "Teleop"
    select_teleoperated_mode(conn)
    time.sleep(1)
    play_sound("sounds/teleop_enabled.mp3")
    enable_robot(conn, current_mode)
    scores_teleop, total_teleop = run_phase(conn, current_mode, duration=135, multipliers={
        "L1": 2,
        "L2": 3,
        "L3": 4,
        "L4": 5,
        "PROCESSOR": 6
    }, last30_sound=True)
    overall_total = total_auto + total_teleop
    print(f"Maç Sonu - Toplam Skor: {overall_total}")
    conn.close()
