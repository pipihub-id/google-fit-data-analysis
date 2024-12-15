from flask import Flask, render_template, request, send_file
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os

app = Flask(__name__)

# Load Dataset
df = pd.read_csv("Metrik aktivitas harian.csv", parse_dates=["Tanggal"])
df['Tanggal'] = pd.to_datetime(df['Tanggal'])
df.set_index('Tanggal', inplace=True)

# Fungsi untuk membuat semua grafik
def generate_plots(year=None):
    plots_folder = "static/plots"
    os.makedirs(plots_folder, exist_ok=True)

    # Filter berdasarkan tahun jika ada
    filtered_df = df.copy()
    if year and year != "all":
        filtered_df = df.loc[df.index.year == int(year)].copy()

    # Plot 1: Jumlah Menit Bergerak per Bulan
    filtered_df['Month'] = filtered_df.index.month_name()
    monthly_move = filtered_df.groupby('Month')['Jumlah Menit Bergerak'].sum()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_move = monthly_move.reindex(month_order)
    plt.figure(figsize=(10, 6))
    monthly_move.plot(kind='bar', color='skyblue')
    plt.title("Jumlah Menit Bergerak per Bulan")
    plt.ylabel("Jumlah Menit Bergerak")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/plot1.png")
    plt.close()

    # Plot 2: Line Chart Jumlah Langkah
    plt.figure(figsize=(12, 6))
    plt.plot(filtered_df.index, filtered_df['Jumlah langkah'], color='purple')
    plt.title("Jumlah Langkah per Hari")
    plt.ylabel("Jumlah Langkah")
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/plot2.png")
    plt.close()

    # Plot 3: Pie Chart Kontribusi
    plt.figure(figsize=(8, 8))
    if year and year != "all":
        pie_data = filtered_df.groupby('Month')['Jumlah Menit Bergerak'].sum()
        plt.title(f"Kontribusi Menit Bergerak per Bulan - {year}")
    else:
        pie_data = df.groupby(df.index.year)['Jumlah Menit Bergerak'].sum()
        plt.title("Kontribusi Menit Bergerak per Tahun")
    
    plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/plot3.png")
    plt.close()

    # Plot 4: Detak Jantung
    plt.figure(figsize=(12, 6))
    plt.plot(filtered_df.index, filtered_df['Detak jantung rata-rata (dpm)'], label='Rata-rata', color='blue')
    plt.plot(filtered_df.index, filtered_df['Detak jantung maks (dpm)'], label='Maksimum', color='red')
    plt.plot(filtered_df.index, filtered_df['Detak jantung min (dpm)'], label='Minimum', color='green')
    plt.title("Detak Jantung Rata-rata, Maksimum, dan Minimum")
    plt.ylabel("Detak Jantung (dpm)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{plots_folder}/plot4.png")
    plt.close()

    return plots_folder

# Route Utama
@app.route("/", methods=["GET", "POST"])
def index():
    year = request.form.get("year") if request.method == "POST" else "all"
    plots_folder = generate_plots(year)
    plots = [f"/{plots_folder}/plot{i}.png" for i in range(1, 5)]
    return render_template("report.html", plots=plots, year=year)

# Route Simpan PDF
@app.route("/download-pdf")
def download_pdf():
    plots_folder = generate_plots()
    pdf_path = "GoogleFit_Report.pdf"
    with PdfPages(pdf_path) as pdf:
        for i in range(1, 5):
            img = plt.imread(f"{plots_folder}/plot{i}.png")
            plt.imshow(img)
            plt.axis('off')
            pdf.savefig()
            plt.close()
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
