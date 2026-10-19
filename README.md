# STATCAL ONLINE — Binomial Distribution & Simulation

Aplikasi pembelajaran Statistika Matematika untuk kasus binomial. Dua contoh awal:

- Kasus 1, pendidikan: 3 soal benar/salah, p = 0,5, tepat 2 benar → 37,5%.
- Kasus 2, pertanian: 4 benih, p = 0,8, tepat 3 tumbuh → 40,96%.

## Jalankan di komputer Windows

1. Ekstrak ZIP, buka folder hasil ekstrak.
2. Buka **Command Prompt** atau **PowerShell** di folder yang berisi `app.py`.
3. Pastikan Python sudah terpasang, lalu jalankan:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

4. Buka alamat lokal yang tampil pada terminal (biasanya `http://localhost:8501`).

Untuk menjalankan di Streamlit Community Cloud, unggah `app.py`, `binomial_core.py`, dan `requirements.txt` ke repositori GitHub, lalu gunakan `app.py` sebagai entrypoint.

## Parameter

- `n`: jumlah percobaan (1 s.d. 100).
- `p`: probabilitas sukses per percobaan (0 s.d. 1).
- `y`: banyaknya sukses yang dipilih (0 s.d. n).
- `q = 1 - p`: dihitung otomatis.
- Untuk probabilitas interval, masukkan `a` dan `b` sebagai batas jumlah sukses.

## Kemampuan aplikasi

- Hitung P(Y=y), P(Y≤y), P(Y≥y), P(Y<y), P(Y>y), dan P(a≤Y≤b).
- Visualisasi grafik probabilitas (PMF) dan probabilitas kumulatif (CDF).
- Memperlihatkan penghitungan kombinasi untuk kejadian tepat y.
- Ruang sampel lengkap untuk kasus kecil (n ≤ 8), termasuk probabilitas tiap pola.
- Simulasi Monte Carlo hingga 100.000 pengulangan, dengan seed acak yang dapat diatur.
- Grafik teori versus hasil simulasi.
- Unduhan Excel berisi Ringkasan, Distribusi (rumus Excel), Grafik **native Excel**, Simulasi (jika tersedia), dan Ruang Sampel (n ≤ 8).
- Grafik di Excel bisa diedit dan dicetak. Tata letak cetak Excel sudah disiapkan.

## Catatan pedagogis

Saat p ≠ 0,5, tidak semua pola dalam ruang sampel memiliki peluang sama. Jangan menghitung peluang hanya dengan membagi banyaknya pola yang diinginkan dengan banyaknya seluruh pola. Jumlahkan probabilitas pola yang memenuhi kejadian, atau gunakan rumus binomial.

Acuan: Wackerly, Mendenhall, & Scheaffer, *Mathematical Statistics with Applications*, 7th ed., Subbab 3.4, hal. cetak 100–114.
