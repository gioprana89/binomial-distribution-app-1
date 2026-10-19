"""STATCAL ONLINE — Binomial Probability Distribution & Simulation.
Jalankan: streamlit run app.py
"""
from __future__ import annotations

from math import comb

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from binomial_core import (
    MODES, compute, describe_event, enumerate_space, export_excel, simulate
)

st.set_page_config(
    page_title="STATCAL ONLINE | Binomial Distribution",
    page_icon="📊", layout="wide", initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.block-container {padding-top: 1.65rem; padding-bottom: 2.5rem; max-width: 1450px;}
.title-sub {color:#5b7183; margin-top:-10px;}
div[data-testid="stMetric"] {background:#eef7f7; border:1px solid #d9eeed;
    padding:13px 16px; border-radius:12px;}
div[data-testid="stMetricLabel"] {font-weight:600;}
.small-label {font-size:0.91rem; color:#536a80;}
</style>
""", unsafe_allow_html=True)

PRESETS = {
    "Kasus 2 — Pertanian: benih tumbuh (80%)": {
        "n": 4, "p": 0.8, "y": 3, "a": 2, "b": 3,
        "success": "T", "failure": "G",
        "description": "Dari 4 benih independen, setiap benih berpeluang 80% tumbuh. Berapa peluang tepat 3 benih tumbuh?",
        "success_meaning": "T = benih tumbuh", "failure_meaning": "G = gagal tumbuh",
    },
    "Kasus 1 — Pendidikan: soal benar/salah (50%)": {
        "n": 3, "p": 0.5, "y": 2, "a": 1, "b": 2,
        "success": "B", "failure": "S",
        "description": "Mahasiswa menebak 3 soal Benar/Salah secara independen. Berapa peluang tepat 2 jawaban benar?",
        "success_meaning": "B = jawaban benar", "failure_meaning": "S = jawaban salah",
    },
    "Kasus bebas — masukkan parameter sendiri": {
        "n": 10, "p": 0.3, "y": 3, "a": 2, "b": 5,
        "success": "T", "failure": "G",
        "description": "Definisikan 'sukses' dan 'gagal' sesuai bidang ilmu yang sedang dipelajari.",
        "success_meaning": "T = sukses", "failure_meaning": "G = gagal",
    },
}


def apply_preset() -> None:
    preset = PRESETS[st.session_state["case_choice"]]
    for name in ("n", "p", "y", "a", "b"):
        st.session_state[f"input_{name}"] = preset[name]
    st.session_state["mode"] = "Tepat y"
    st.session_state["sim_result"] = None


if "case_choice" not in st.session_state:
    st.session_state["case_choice"] = next(iter(PRESETS))
if "input_n" not in st.session_state:
    apply_preset()

st.title("📊 STATCAL ONLINE — Distribusi Binomial")
st.markdown('<div class="title-sub">Belajar dari kasus → ruang sampel → penyelesaian manual → rumus → grafik → simulasi → Excel</div>',
            unsafe_allow_html=True)
st.caption("Bahan kuliah Statistika Matematika | Acuan materi: Wackerly, Mendenhall & Scheaffer, Mathematical Statistics with Applications, edisi 7, §3.4")

with st.sidebar:
    st.header("🎛️ Pengaturan")
    st.selectbox("Pilih contoh kasus", list(PRESETS), key="case_choice", on_change=apply_preset)
    st.markdown("**Tiga input utama dalam rumus binomial**")
    st.number_input("① Banyak percobaan (n)", min_value=1, max_value=100, step=1,
                    key="input_n", help="Jumlah percobaan independen; misalnya 4 benih.")
    n = int(st.session_state["input_n"])
    for key in ("input_y", "input_a", "input_b"):
        st.session_state[key] = min(n, int(st.session_state[key]))
    st.number_input("② Probabilitas sukses (p)", min_value=0.0, max_value=1.0,
              step=0.01, format="%.4f", key="input_p",
              help="Peluang sukses pada setiap percobaan; misalnya 0,80 berarti 80%.")
    p = float(st.session_state["input_p"])
    st.metric("Probabilitas gagal (q = 1 − p)", f"{1 - p:.2f}")
    st.selectbox("Jenis kejadian yang ingin dihitung", list(MODES), key="mode")
    mode = st.session_state["mode"]
    if mode == "Antara a dan b":
        st.number_input("Batas bawah a", min_value=0, max_value=n, step=1, key="input_a")
        a = int(st.session_state["input_a"])
        if st.session_state["input_b"] < a:
            st.session_state["input_b"] = a
        st.number_input("Batas atas b", min_value=a, max_value=n, step=1, key="input_b")
        b = int(st.session_state["input_b"])
        y = int(st.session_state["input_y"])
    else:
        st.number_input("③ Banyak sukses (y)", min_value=0, max_value=n, step=1,
                        key="input_y", help="Banyaknya sukses yang ingin diamati.")
        y = int(st.session_state["input_y"])
        a, b = 0, n
    st.divider()
    st.markdown("**Makna parameter**")
    st.markdown("- **n:** jumlah percobaan (bilangan bulat positif)\n- **p:** probabilitas sukses (0–1)\n- **y:** banyaknya sukses (0–n)\n- **q = 1 − p:** dihitung otomatis, **bukan input keempat**.")
    st.info("Asumsi binomial: jumlah percobaan tetap, dua hasil per percobaan, p konstan, dan percobaan independen.")

case_label = st.session_state["case_choice"]
meta = PRESETS[case_label]
result = compute(n, p, mode, y, a, b)
mask = result["mask"]
ks = result["ks"]
pmf = result["pmf"]
label_event = result["label"]
space = enumerate_space(n, p, mode, y, a, b, meta["success"], meta["failure"])

st.info(f"**Konteks kasus:** {meta['description']}  Jika parameter diubah, perhitungan mengikuti parameter terbaru.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Probabilitas kejadian", f"{result['prob'] * 100:.4f}%")
k2.metric("Nilai harapan E(Y)", f"{result['mean']:.4f}")
k3.metric("Varians Var(Y)", f"{result['variance']:.4f}")
k4.metric("Standar deviasi", f"{result['sd']:.4f}")
st.caption(f"**Peristiwa yang dihitung:** {label_event}  |  n = {n}; p = {p:.2f}; q = {1-p:.2f}")


def theoretical_chart() -> go.Figure:
    colors = ["#047F80" if mask[k] else "#B8D1E5" for k in ks]
    fig = go.Figure(go.Bar(
        x=ks, y=pmf * 100, marker_color=colors,
        customdata=np.round(pmf, 8),
        hovertemplate="y = %{x}<br>P(Y=y) = %{customdata:.6f}<br>%{y:.4f}%<extra></extra>",
    ))
    fig.update_layout(
        title=f"Distribusi Binomial: n={n}, p={p:.2f}",
        xaxis_title="Banyak sukses (y)", yaxis_title="Probabilitas (%)",
        xaxis=dict(dtick=1 if n <= 30 else None),
        margin=dict(l=20, r=25, t=50, b=20), height=410,
        plot_bgcolor="white", paper_bgcolor="white", font=dict(color="#18334A")
    )
    fig.update_yaxes(rangemode="tozero", showgrid=True, gridcolor="#EDF2F6")
    return fig


def cumulative_chart() -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=ks, y=result["cdf"] * 100, mode="lines+markers",
        line=dict(color="#2E86AB", shape="hv", width=2),
        marker=dict(size=5),
        hovertemplate="y ≤ %{x}<br>P(Y≤y) = %{y:.4f}%<extra></extra>"
    ))
    fig.update_layout(title="Probabilitas Kumulatif P(Y ≤ y)",
                      xaxis_title="Banyak sukses (y)", yaxis_title="Probabilitas kumulatif (%)",
                      yaxis=dict(range=[0, 103]), height=370,
                      margin=dict(l=20, r=25, t=50, b=20), plot_bgcolor="white")
    return fig


def data_table() -> pd.DataFrame:
    return pd.DataFrame({
        "y (jumlah sukses)": ks,
        "P(Y=y)": pmf,
        "Persentase (%)": np.round(pmf * 100, 6),
        "P(Y≤y)": result["cdf"],
        "Termasuk kejadian?": np.where(mask, "YA", "Tidak"),
    })


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Grafik & Tabel", "✏️ Perhitungan Bertahap",
    "🎲 Simulasi Monte Carlo", "🧩 Ruang Sampel", "📥 Ekspor Excel"
])

with tab1:
    st.subheader("Visualisasi probabilitas teoretis")
    st.plotly_chart(theoretical_chart(), use_container_width=True)
    st.caption("Batang hijau = jumlah sukses yang memenuhi kejadian pilihan; batang biru muda = di luar kejadian.")
    if p == 0.5:
        st.markdown("**Pengamatan:** ketika p = 0,5, bentuk distribusi binomial simetris.")
    elif p > 0.5:
        st.markdown("**Pengamatan:** ketika p > 0,5, probabilitas cenderung lebih besar pada banyaknya sukses yang tinggi.")
    else:
        st.markdown("**Pengamatan:** ketika p < 0,5, probabilitas cenderung lebih besar pada banyaknya sukses yang rendah.")
    st.plotly_chart(cumulative_chart(), use_container_width=True)
    st.subheader("Tabel distribusi")
    st.dataframe(data_table(), hide_index=True, use_container_width=True,
                 column_config={"P(Y=y)": st.column_config.NumberColumn(format="%.8f"),
                                "P(Y≤y)": st.column_config.NumberColumn(format="%.8f")})
    st.caption(f"Cek: Σ P(Y=y) = {np.sum(pmf):.8f} (harus sama dengan 1).")

with tab2:
    st.subheader("Menghubungkan cara manual dengan rumus binomial")
    st.markdown("**Tahap 1 — Tentukan parameter:**")
    st.latex(fr"n={n},\qquad p={p:.2f},\qquad q=1-p={1-p:.2f}")
    st.markdown("**Tahap 2 — Rumus distribusi binomial:**")
    st.latex(r"P(Y=k)=\binom{n}{k}p^{k}(1-p)^{n-k},\qquad k=0,1,\ldots,n")
    if mode == "Tepat y":
        combination = comb(n, y)
        single_seq_probability = p ** y * (1-p) ** (n-y)
        st.markdown("**Tahap 3 — Hitung banyak susunan dengan kombinasi:**")
        st.latex(fr"\binom{{{n}}}{{{y}}}=\frac{{{n}!}}{{{y}!\,({n}-{y})!}}={combination:,}".replace(",", "{,}"))
        st.markdown("**Tahap 4 — Hitung probabilitas satu susunan dan gabungkan:**")
        st.latex(fr"p^y(1-p)^{{n-y}}=({p:.2f})^{{{y}}}({1-p:.2f})^{{{n-y}}}={single_seq_probability:.8f}")
        st.latex(fr"P(Y={y})={combination}\times {single_seq_probability:.8f}\approx\boxed{{{result['prob']:.8f}}}")
        if n <= 8:
            st.caption(f"Terdapat {combination} susunan dengan tepat {y} sukses. Lihat tab Ruang Sampel untuk memeriksanya.")
        if abs(p - 0.5) < 1e-12:
            st.success(f"Karena p = 0,5, semua {2**n:,} susunan setara: P(Y={y}) = {combination}/{2**n} = {result['prob']:.6f}.")
        else:
            st.warning("Karena p ≠ 0,5, jangan gunakan jumlah susunan yang diinginkan / jumlah seluruh susunan. "
                       "Kalikan banyak susunan dengan probabilitas masing-masing susunan.")
    else:
        indexes = list(ks[mask])
        terms = " + ".join(f"P(Y={k})" for k in indexes)
        if len(indexes) <= 12:
            st.markdown(f"**Tahap 3 — Jumlahkan kejadian yang memenuhi:** {terms if terms else 'tidak ada nilai Y yang memenuhi'}.")
        else:
            st.markdown(f"**Tahap 3 — Jumlahkan probabilitas untuk {len(indexes)} nilai sukses yang memenuhi kejadian.**")
        label_latex = label_event.replace("≤", "\\leq").replace("≥", "\\geq")
        st.latex(fr"{label_latex}\;=\;\boxed{{{result['prob']:.8f}}}")
        st.caption("Probabilitas tersebut merupakan jumlah P(Y=k) untuk seluruh nilai k yang masuk kejadian.")
    st.markdown("**Tahap 5 — Makna hasil:**")
    st.success(f"Dalam model binomial dengan n={n} dan p={p:.2f}, probabilitas {label_event} adalah **{result['prob']*100:.4f}%**.")
    with st.expander("Kode Python dan R untuk verifikasi"):
        pcode = {
            "Tepat y": f"binom.pmf({y}, {n}, {p})",
            "Paling banyak y": f"binom.cdf({y}, {n}, {p})",
            "Paling sedikit y": f"binom.sf({y}-1, {n}, {p})",
            "Kurang dari y": f"binom.cdf({y}-1, {n}, {p})",
            "Lebih dari y": f"binom.sf({y}, {n}, {p})",
            "Antara a dan b": f"binom.cdf({b}, {n}, {p}) - binom.cdf({a}-1, {n}, {p})",
        }[mode]
        st.code(f"from scipy.stats import binom\nhasil = {pcode}\nprint(hasil)", language="python")
        rcode = {
            "Tepat y": f"dbinom({y}, size={n}, prob={p})",
            "Paling banyak y": f"pbinom({y}, size={n}, prob={p})",
            "Paling sedikit y": f"pbinom({y}-1, size={n}, prob={p}, lower.tail=FALSE)",
            "Kurang dari y": f"pbinom({y}-1, size={n}, prob={p})",
            "Lebih dari y": f"pbinom({y}, size={n}, prob={p}, lower.tail=FALSE)",
            "Antara a dan b": f"pbinom({b}, size={n}, prob={p}) - pbinom({a}-1, size={n}, prob={p})",
        }[mode]
        st.code(f"hasil <- {rcode}\nprint(hasil)", language="r")

with tab3:
    st.subheader("Simulasi: ulangi eksperimen secara acak")
    st.markdown("Komputer melakukan percobaan binomial berkali-kali dan menghitung **frekuensi relatif empiris**. "
                "Angka simulasi umumnya **tidak persis sama** dengan probabilitas teoretis.")
    sa, sb, sc = st.columns(3)
    with sa:
        reps = st.select_slider("Jumlah pengulangan", options=[100, 500, 1000, 5000, 10000, 50000, 100000], value=1000, key="sim_reps")
    with sb:
        seed = st.number_input("Random seed (agar bisa diulang)", min_value=0, max_value=99999999, value=2026, step=1, key="sim_seed")
    with sc:
        st.write(" ")
        st.write(" ")
        run_sim = st.button("▶ Jalankan simulasi", type="primary", use_container_width=True)
    signature = (n, p, int(reps), int(seed))
    if run_sim:
        st.session_state["sim_result"] = simulate(n, p, int(reps), int(seed))
    current = st.session_state.get("sim_result")
    valid_sim = current is not None and (
        current["n"], current["p"], current["replications"], current["seed"]
    ) == signature
    if valid_sim:
        counts = np.asarray(current["counts"], dtype=int)
        frequencies = counts / reps
        observed = float(np.sum(frequencies[mask]))
        c1, c2, c3 = st.columns(3)
        c1.metric("Hasil teoretis", f"{100*result['prob']:.4f}%")
        c2.metric("Hasil simulasi", f"{100*observed:.4f}%")
        c3.metric("Selisih absolut", f"{100*abs(observed-result['prob']):.4f} poin persentase")
        compare = go.Figure()
        compare.add_bar(x=ks, y=pmf*100, name="Teori", marker_color="#047F80")
        compare.add_bar(x=ks, y=frequencies*100, name="Simulasi", marker_color="#F4AB3B")
        compare.update_layout(barmode="group", height=400, xaxis_title="Jumlah sukses (y)",
                              yaxis_title="Probabilitas / frekuensi relatif (%)",
                              title=f"Teori vs {reps:,} Pengulangan", plot_bgcolor="white",
                              margin=dict(l=15,r=10,t=50,b=20))
        st.plotly_chart(compare, use_container_width=True)
        st.caption("Untuk parameter dan seed yang sama, hasil dapat direproduksi. Ubah seed untuk eksperimen acak baru.")
    else:
        st.info("Klik **Jalankan simulasi** untuk melihat hasil percobaan acak dan grafik perbandingannya.")

with tab4:
    st.subheader("Daftar susunan kejadian")
    st.markdown(f"**Notasi:** {meta['success_meaning']}; {meta['failure_meaning']}.")
    if n <= 8:
        frame = pd.DataFrame(space)
        frame["Termasuk kejadian"] = frame["Masuk kejadian"].map({True: "YA", False: "Tidak"})
        frame = frame.drop(columns=["Masuk kejadian"])
        st.dataframe(frame, hide_index=True, use_container_width=True,
                     column_config={"Probabilitas pola": st.column_config.NumberColumn(format="%.8f")})
        chosen = [row for row in space if row["Masuk kejadian"]]
        st.markdown(f"**Jumlah seluruh susunan:** {2**n:,} | "
                    f"**Susunan yang memenuhi kejadian:** {len(chosen):,}")
        if chosen:
            st.markdown("**Pemeriksaan secara manual:** jumlah probabilitas pola terpilih")
            st.latex(fr"\sum_{{\omega\in A}}P(\omega)={sum(row['Probabilitas pola'] for row in chosen):.8f}")
        st.caption("Perhatikan: untuk p ≠ 0,5, pola dengan jumlah sukses berbeda memiliki probabilitas berbeda. "
                   "Peluang kasus dihitung dengan menjumlahkan probabilitas polanya, bukan membagi jumlah pola.")
    else:
        st.warning(f"Karena n={n}, ruang sampel memiliki 2^{n} kemungkinan. Untuk menjaga aplikasi cepat, "
                   "daftar seluruh susunan hanya ditampilkan ketika n ≤ 8. "
                   "Rumus binomial tetap bisa dipakai hingga n = 100.")

with tab5:
    st.subheader("Unduh hasil ke Microsoft Excel (.xlsx)")
    st.markdown("File Excel berisi **Ringkasan**, **Distribusi** (dengan rumus Excel), "
                "**Grafik** yang bisa diedit dan dicetak, serta **Simulasi** jika sudah dijalankan. "
                "Untuk n ≤ 8 juga terdapat lembar **Ruang Sampel**.")
    st.info("Lembar Ringkasan berisi parameter n dan p. Mengubah p pada Excel akan menghitung ulang tabel "
            "dan grafik; untuk mengubah n atau jenis kejadian, ekspor ulang dari aplikasi.")
    st.markdown("**Isi data yang diekspor:**")
    st.dataframe(data_table(), hide_index=True, use_container_width=True)
    sim_result = st.session_state.get("sim_result")
    sim_ok = sim_result is not None and (
        sim_result["n"], sim_result["p"], sim_result["replications"], sim_result["seed"]
    ) == (n, p, int(st.session_state["sim_reps"]), int(st.session_state["sim_seed"]))
    # Cegah ekspor data simulasi lama apabila jumlah pengulangan/seed berubah di tab simulasi.
    # Dalam situasi itu, pengguna dapat menjalankan ulang simulasi sebelum mengekspor.
    try:
        excel_bytes = export_excel(result, sim_result if sim_ok else None, space, case_label)
        filename = f"STATCAL_Binomial_n{n}_p{p:.2f}.xlsx"
        st.download_button("⬇️ Unduh hasil + grafik Excel", data=excel_bytes,
                           file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True, type="primary")
    except Exception as exc:
        st.error("Ekspor Excel gagal. Periksa dependensi XlsxWriter dan jalankan ulang aplikasi.")
        st.exception(exc)

st.divider()
st.caption("STATCAL ONLINE | Dibuat untuk pembelajaran Statistika Matematika. "
           "Hasil probabilitas eksak mengikuti distribusi binomial; simulasi bersifat acak.")
