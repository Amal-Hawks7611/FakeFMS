import sqlite3
import numpy as np
import matplotlib.pyplot as plt

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
            auto, tele = rows[i], rows[i+1]
            match_id = len(matches) + 1
            auto_score, tele_score = auto[3], tele[3]
            overall = auto_score + tele_score
            auto_details = [auto[4], auto[5], auto[6], auto[7], auto[8], auto[9]]
            tele_details = [tele[4], tele[5], tele[6], tele[7], tele[8], tele[9]]
            matches.append({"match_id": match_id, "timestamp": tele[1], 
                            "auto_score": auto_score, "tele_score": tele_score, 
                            "overall": overall, "auto_details": auto_details, 
                            "tele_details": tele_details})
            i += 2
        else:
            i += 1
    return matches

def plot_graphs():
    matches = fetch_match_records()
    
    match_ids = [m["match_id"] for m in matches]
    auto_scores = [m["auto_score"] for m in matches]
    tele_scores = [m["tele_score"] for m in matches]
    overall_scores = [m["overall"] for m in matches]

    categories = ["L1", "L2", "L3", "L4", "PROCESSOR", "PARK"]
    auto_totals = np.zeros(len(categories))
    tele_totals = np.zeros(len(categories))

    for m in matches:
        auto_data = np.array(m["auto_details"] + [0] * (len(categories) - len(m["auto_details"])))
        tele_data = np.array(m["tele_details"] + [0] * (len(categories) - len(m["tele_details"])))

        auto_totals += auto_data
        tele_totals += tele_data

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    axs[0, 0].bar(match_ids, auto_scores, label="Otonom", color='blue', alpha=0.7)
    axs[0, 0].bar(match_ids, tele_scores, label="Teleop", color='red', alpha=0.7, bottom=auto_scores)
    axs[0, 0].set_xlabel("Maç ID")
    axs[0, 0].set_ylabel("Skor")
    axs[0, 0].set_title("Otonom ve Teleop Skorları")
    axs[0, 0].legend()

    axs[0, 1].plot(match_ids, overall_scores, marker="o", linestyle="-", color="purple")
    axs[0, 1].set_xlabel("Maç ID")
    axs[0, 1].set_ylabel("Genel Skor")
    axs[0, 1].set_title("Zaman İçinde Skor Değişimi")

    axs[1, 0].bar(np.arange(len(categories)) - 0.2, auto_totals, width=0.4, label="Otonom", color="blue")
    axs[1, 0].bar(np.arange(len(categories)) + 0.2, tele_totals, width=0.4, label="Teleop", color="red")
    axs[1, 0].set_xticks(np.arange(len(categories)))
    axs[1, 0].set_xticklabels(categories)
    axs[1, 0].set_ylabel("Toplam Skor")
    axs[1, 0].set_title("Oyun Elemanlarına Göre Skor Dağılımı")
    axs[1, 0].legend()

    axs[1, 1].hist(overall_scores, bins=10, color="green", alpha=0.7)
    axs[1, 1].set_xlabel("Genel Skor Aralığı")
    axs[1, 1].set_ylabel("Maç Sayısı")
    axs[1, 1].set_title("Genel Skorların Dağılımı")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_graphs()
