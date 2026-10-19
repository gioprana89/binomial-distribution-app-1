# STATCAL ONLINE — Binomial Distribution & Simulation

Aplikasi pembelajaran Statistika Matematika untuk kasus binomial.

## Pembaruan: Tab Probabilitas Kumulatif (CDF)

Kini tersedia tab khusus **📈 Probabilitas Kumulatif (CDF)** yang bekerja secara mandiri dari pilihan jenis kejadian di sidebar. Anda memasukkan n dan p di sidebar, kemudian memilih batas k (0 sampai n) pada tab CDF.

- Hasil utama: **P(Y ≤ k)** atau peluang *paling banyak k* sukses, dengan PMF tepat k dan peluang komplemen P(Y > k).
- Langkah hitung manual: P(Y ≤ k) = jumlah P(Y = 0), ..., P(Y = k), tabel kombinasi dan nilai probabilitas, serta substitusi rumus untuk k kecil.
- Dua grafik interaktif: batang PMF yang menandai semua nilai ≤ k; grafik CDF yang menyorot F(k).
- Ekspor `.xlsx` dari tab CDF dan dari tab Ekspor Excel; lembar **Kumulatif** baru memuat rumus, tabel, serta dua grafik native Excel yang bisa diedit dan dicetak.
- Di lembar **Kumulatif**, pengguna dapat mengubah angka **k** pada **B5**. Probabilitas **p** dapat diubah melalui lembar **Ringkasan** sel **B6**. Nilai **n** pada file Excel tetap; ubah n dari Streamlit dan ekspor ulang.
- Semua fitur lama (PMF, simulasi, ruang sampel, Excel, dan pilihan jenis kejadian) dipertahankan.

Empat preset pembelajaran:

- Kasus 1, pendidikan: 3 soal benar/salah, p = 0,5, tepat 2 benar → 37,5%.
- Kasus 2, pertanian: 4 benih, p = 0,8, tepat 3 tumbuh → 40,96%.
- Kasus 3, industri: 4 lampu, p(cacat) = 0,1, paling sedikit 1 cacat → 34,39%.
- Kasus 4, kesehatan (ilustrasi matematika): 5 pasien, p(efek samping) = 0,2, paling banyak 2 mengalami efek samping → **94,208%**.

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
- Visualisasi grafik probabilitas (PMF) dan probabilitas kumulatif (CDF), dengan tab pembelajaran CDF tersendiri.
- Memperlihatkan penghitungan kombinasi untuk kejadian tepat y.
- Ruang sampel lengkap untuk kasus kecil (n ≤ 8), termasuk probabilitas tiap pola.
- Simulasi Monte Carlo hingga 100.000 pengulangan, dengan seed acak yang dapat diatur.
- Grafik teori versus hasil simulasi.
- Unduhan Excel berisi Ringkasan, Distribusi (rumus Excel), **Kumulatif (tabel, rumus, dua grafik asli Excel)**, Grafik, Simulasi (jika tersedia), dan Ruang Sampel (n ≤ 8).
- Grafik di Excel bisa diedit dan dicetak. Tata letak cetak Excel sudah disiapkan.

## Catatan pedagogis

Saat p ≠ 0,5, tidak semua pola dalam ruang sampel memiliki peluang sama. Jangan menghitung peluang hanya dengan membagi banyaknya pola yang diinginkan dengan banyaknya seluruh pola. Jumlahkan probabilitas pola yang memenuhi kejadian, atau gunakan rumus binomial.

Acuan: Wackerly, Mendenhall, & Scheaffer, *Mathematical Statistics with Applications*, 7th ed., Subbab 3.4, hal. cetak 100–114.

## Jalankan pengujian

```powershell
python -m unittest discover -s tests -v
```

Pengujian memeriksa hasil kasus 1–4, sifat CDF, kasus batas p=0 dan p=1, serta struktur dan rumus workbook Excel. Tampilan grafis Streamlit memerlukan pengujian tambahan langsung pada browser Anda.
