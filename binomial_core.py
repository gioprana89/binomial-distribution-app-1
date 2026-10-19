"""Inti komputasi & ekspor Excel untuk STATCAL Binomial Simulator."""
from __future__ import annotations

from io import BytesIO
from itertools import product
from math import comb, sqrt
from typing import Any

import numpy as np
from scipy.stats import binom
import xlsxwriter

MODES = {
    "Tepat y": "Y = y",
    "Paling banyak y": "Y ≤ y",
    "Paling sedikit y": "Y ≥ y",
    "Kurang dari y": "Y < y",
    "Lebih dari y": "Y > y",
    "Antara a dan b": "a ≤ Y ≤ b",
}


def event_mask(n: int, mode: str, y: int, a: int = 0, b: int = 0) -> np.ndarray:
    """Kondisi yang dipilih untuk setiap kemungkinan Y = 0, ..., n."""
    if mode not in MODES:
        raise ValueError(f"Jenis kejadian tidak dikenal: {mode}")
    k = np.arange(n + 1)
    if mode == "Tepat y":
        return k == y
    if mode == "Paling banyak y":
        return k <= y
    if mode == "Paling sedikit y":
        return k >= y
    if mode == "Kurang dari y":
        return k < y
    if mode == "Lebih dari y":
        return k > y
    return (k >= a) & (k <= b)


def describe_event(mode: str, y: int, a: int = 0, b: int = 0) -> str:
    return {
        "Tepat y": f"P(Y = {y})",
        "Paling banyak y": f"P(Y ≤ {y})",
        "Paling sedikit y": f"P(Y ≥ {y})",
        "Kurang dari y": f"P(Y < {y})",
        "Lebih dari y": f"P(Y > {y})",
        "Antara a dan b": f"P({a} ≤ Y ≤ {b})",
    }[mode]


def compute(n: int, p: float, mode: str, y: int, a: int = 0, b: int = 0) -> dict[str, Any]:
    if not (1 <= n <= 100 and 0 <= p <= 1 and 0 <= y <= n and 0 <= a <= b <= n):
        raise ValueError("Pastikan 1 ≤ n ≤ 100, 0 ≤ p ≤ 1, 0 ≤ y ≤ n, dan 0 ≤ a ≤ b ≤ n.")
    ks = np.arange(n + 1)
    pmf = np.asarray(binom.pmf(ks, n, p), dtype=float)
    cdf = np.asarray(binom.cdf(ks, n, p), dtype=float)
    mask = event_mask(n, mode, y, a, b)
    prob = float(np.sum(pmf[mask]))
    return {
        "n": n, "p": p, "q": 1.0 - p, "y": y, "a": a, "b": b,
        "mode": mode, "label": describe_event(mode, y, a, b),
        "ks": ks, "pmf": pmf, "cdf": cdf, "mask": mask,
        "prob": max(0.0, min(1.0, prob)),
        "mean": n * p, "variance": n * p * (1 - p),
        "sd": sqrt(n * p * (1 - p)),
    }


def enumerate_space(n: int, p: float, mode: str, y: int, a: int, b: int,
                    success: str = "T", failure: str = "G") -> list[dict[str, Any]]:
    """Boleh untuk n≤8, sehingga tampilan/Excel tetap ringkas."""
    if n > 8:
        return []
    mask = event_mask(n, mode, y, a, b)
    rows = []
    for choices in product((failure, success), repeat=n):
        k = sum(c == success for c in choices)
        pr = (p ** k) * ((1 - p) ** (n - k))
        rows.append({"Pola": "".join(choices), "Jumlah sukses": k,
                     "Probabilitas pola": pr,
                     "Masuk kejadian": bool(mask[k])})
    return sorted(rows, key=lambda r: (r["Jumlah sukses"], r["Pola"]))


def simulate(n: int, p: float, replications: int, seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    draws = rng.binomial(n, p, size=replications)
    counts = np.bincount(draws, minlength=n + 1)
    return {"counts": counts, "replications": replications, "seed": seed, "n": n, "p": p}


def export_excel(result: dict[str, Any], sim: dict[str, Any] | None = None,
                 space: list[dict[str, Any]] | None = None,
                 case_label: str = "Kasus bebas") -> bytes:
    """Ekspor xlsx termasuk grafik Excel asli yang dapat diedit/dicetak.

    Parameter n/p terdapat di Ringkasan. Distribusi memakai formula Excel,
    sehingga mengubah p di Excel memperbarui probabilitas dan grafik otomatis.
    Untuk mengubah n atau kejadian, ulangi ekspor dari aplikasi.
    """
    n = result["n"]
    p = result["p"]
    mask = result["mask"]
    pmf = result["pmf"]
    cdf = result["cdf"]
    reps = int(sim["replications"]) if sim is not None else 0
    counts = np.asarray(sim["counts"], dtype=int) if sim is not None else np.zeros(n + 1, dtype=int)
    buffer = BytesIO()
    book = xlsxwriter.Workbook(buffer, {"in_memory": True})
    book.set_properties({"title": "STATCAL ONLINE - Distribusi Binomial",
                         "subject": "Bahan kuliah Statistika Matematika dan Simulasi Binomial",
                         "author": "STATCAL ONLINE"})
    navy = "#142B49"
    teal = "#047F80"
    pale = "#EAF5F4"
    green = "#DFF4E7"
    white = "#FFFFFF"
    title = book.add_format({"bold": True, "font_size": 17, "font_color": white,
                             "bg_color": navy, "valign": "vcenter"})
    subtitle = book.add_format({"font_size": 10, "font_color": "#51647C", "italic": True})
    header = book.add_format({"bold": True, "font_color": white, "bg_color": teal,
                              "align": "center", "valign": "vcenter", "text_wrap": True,
                              "border": 1, "border_color": "#C7DEDE"})
    txt = book.add_format({"font_color": navy})
    value = book.add_format({"font_color": navy, "num_format": "0.000000"})
    pct = book.add_format({"font_color": navy, "num_format": "0.00%"})
    integer = book.add_format({"font_color": navy, "num_format": "0"})
    label = book.add_format({"font_color": navy, "bold": True})
    inp = book.add_format({"bg_color": "#FFF1C1", "bold": True, "font_color": navy,
                           "num_format": "0.00%", "border": 1, "border_color": "#E9D99A"})
    inp_int = book.add_format({"bg_color": "#FFF1C1", "bold": True, "font_color": navy,
                               "num_format": "0", "border": 1, "border_color": "#E9D99A"})
    highlight = book.add_format({"bg_color": green, "font_color": "#136A39", "num_format": "0.000000"})
    highlight_pct = book.add_format({"bg_color": green, "font_color": "#136A39", "num_format": "0.00%"})
    note = book.add_format({"font_color": "#52617A", "italic": True, "text_wrap": True, "valign": "top"})
    text_center = book.add_format({"align": "center", "font_color": navy})
    yes = book.add_format({"align": "center", "bg_color": green, "bold": True, "font_color": "#136A39"})

    summary = book.add_worksheet("Ringkasan")
    data = book.add_worksheet("Distribusi")
    graph = book.add_worksheet("Grafik")
    simsheet = book.add_worksheet("Simulasi") if sim is not None else None
    samplesheet = book.add_worksheet("Ruang Sampel") if space else None

    summary.hide_gridlines(2)
    summary.set_column("A:A", 37)
    summary.set_column("B:B", 28)
    summary.set_column("C:J", 13)
    summary.set_row(0, 32)
    summary.merge_range("A1:J1", "STATCAL ONLINE  |  DISTRIBUSI BINOMIAL", title)
    summary.merge_range("A2:J2", "Eksplorasi kasus, solusi matematis, dan simulasi", subtitle)
    fields = [(3, "Contoh kasus", case_label), (4, "Jumlah percobaan (n)", n),
              (5, "Probabilitas sukses (p)", p), (6, "Probabilitas gagal (q)", 1-p),
              (7, "Jumlah simulasi", reps), (8, "Kejadian yang dihitung", result["label"]),
              (9, "Probabilitas kejadian", result["prob"]),
              (10, "Nilai harapan E(Y)", result["mean"]),
              (11, "Varians Var(Y)", result["variance"]),
              (12, "Standar deviasi", result["sd"])]
    for row0, name, val in fields:
        summary.write(row0, 0, name, label)
        if row0 == 4:
            summary.write_number(row0, 1, int(val), inp_int)
        elif row0 == 5:
            summary.write_number(row0, 1, float(val), inp)
        elif row0 == 6:
            summary.write_formula(row0, 1, "=1-B6", pct, 1-p)
        elif row0 == 9:
            pass  # Formula dari tabel Distribusi, ditulis setelah data.
        elif row0 == 10:
            summary.write_formula(row0, 1, "=B5*B6", value, result["mean"])
        elif row0 == 11:
            summary.write_formula(row0, 1, "=B5*B6*(1-B6)", value, result["variance"])
        elif row0 == 12:
            summary.write_formula(row0, 1, "=SQRT(B12)", value, result["sd"])
        elif isinstance(val, str):
            summary.write_string(row0, 1, val, txt)
        else:
            summary.write_number(row0, 1, int(val), integer)
    summary.write(14, 0, "Probabilitas hasil simulasi", label)
    if reps:
        summary.write_formula(14, 1, "=SUM(Distribusi!J5:J%d)" % (n + 5), pct,
                              float(np.sum(counts[mask]) / reps))
    else:
        summary.write(14, 1, "Belum ada simulasi", txt)
    summary.merge_range("A18:J19", "Cara membaca: kolom berwarna kuning adalah parameter. "
                        "Anda dapat mengubah p pada B6 untuk menghitung ulang nilai probabilitas dan grafik; "
                        "untuk mengubah n atau jenis kejadian, ekspor ulang dari aplikasi Streamlit.", note)
    summary.set_row(17, 30)
    summary.set_row(18, 24)
    summary.freeze_panes(3, 0)
    summary.fit_to_pages(1, 1)
    summary.set_landscape()
    summary.print_area("A1:J19")

    data.hide_gridlines(2)
    data.set_column("A:A", 10)
    data.set_column("B:D", 19)
    data.set_column("E:E", 18)
    data.set_column("F:J", 19)
    data.merge_range("A1:J1", "DISTRIBUSI PROBABILITAS BINOMIAL", title)
    data.merge_range("A2:J2", "Nilai Y = 0, 1, ..., n | hijau: nilai yang termasuk kejadian", subtitle)
    columns = ["y", "P(Y=y) teori", "P lainnya", "P kejadian", "Dipilih?", "P(Y≤y) teori",
               "Jumlah simulasi", "P simulasi", "Selisih sim - teori", "P sim kejadian"]
    for j, name in enumerate(columns):
        data.write(3, j, name, header)
    data.set_row(3, 37)
    data.freeze_panes(4, 1)
    for k in range(n + 1):
        r0 = k + 4
        excelrow = r0 + 1
        chosen = bool(mask[k])
        pmf_val = float(pmf[k])
        p_sim = float(counts[k] / reps) if reps else 0.0
        fmt = highlight if chosen else value
        data.write_number(r0, 0, k, integer)
        formula = f"=COMBIN(Ringkasan!$B$5,A{excelrow})*(Ringkasan!$B$6^A{excelrow})*((1-Ringkasan!$B$6)^(Ringkasan!$B$5-A{excelrow}))"
        data.write_formula(r0, 1, formula, fmt, pmf_val)
        data.write_formula(r0, 2, f"=B{excelrow}-D{excelrow}", pct, 0 if chosen else pmf_val)
        data.write_formula(r0, 3, f'=IF(E{excelrow}="YA",B{excelrow},0)', highlight_pct if chosen else pct,
                           pmf_val if chosen else 0.0)
        data.write_string(r0, 4, "YA" if chosen else "TIDAK", yes if chosen else text_center)
        data.write_formula(r0, 5, f"=SUM(B$5:B{excelrow})", pct, float(cdf[k]))
        data.write_number(r0, 6, int(counts[k]), integer)
        if reps:
            data.write_formula(r0, 7, f"=G{excelrow}/Ringkasan!$B$8", pct, p_sim)
            data.write_formula(r0, 8, f"=H{excelrow}-B{excelrow}", pct, p_sim - pmf_val)
            data.write_formula(r0, 9, f'=IF(E{excelrow}="YA",H{excelrow},0)', pct, p_sim if chosen else 0.0)
        else:
            data.write_number(r0, 7, 0.0, pct)
            data.write_number(r0, 8, 0.0, pct)
            data.write_number(r0, 9, 0.0, pct)
    end_row = n + 5
    data.write(n + 5, 0, "TOTAL", label)
    data.write_formula(n + 5, 1, f"=SUM(B5:B{end_row})", pct, float(sum(pmf)))
    data.write_formula(n + 5, 3, f"=SUM(D5:D{end_row})", pct, result["prob"])
    data.write_formula(n + 5, 7, f"=SUM(H5:H{end_row})", pct, 1.0 if reps else 0.0)
    summary.write_formula(9, 1, f"=SUM(Distribusi!D5:D{end_row})", pct, result["prob"])
    data.autofilter(3, 0, n + 4, 9)
    data.fit_to_pages(1, 0)
    data.set_landscape()
    data.repeat_rows(0, 3)
    data.print_area(0, 0, n + 5, 9)

    graph.hide_gridlines(2)
    graph.set_column("A:A", 3)
    graph.set_column("B:Q", 12)
    graph.merge_range("B1:Q1", "GRAFIK DISTRIBUSI BINOMIAL", title)
    graph.write("B2", f"n = {n}, p = {p:.3f} | {result['label']}", subtitle)
    chart1 = book.add_chart({"type": "column", "subtype": "stacked"})
    for col, name, color in [("C", "Probabilitas lainnya", "#BFD3E8"),
                              ("D", "Probabilitas kejadian", teal)]:
        chart1.add_series({"name": name,
                           "categories": f"=Distribusi!$A$5:$A${end_row}",
                           "values": f"=Distribusi!${col}$5:${col}${end_row}",
                           "fill": {"color": color}, "border": {"none": True}})
    chart1.set_title({"name": "Distribusi Probabilitas Teoretis"})
    chart1.set_x_axis({"name": "Jumlah sukses (y)"})
    chart1.set_y_axis({"name": "Probabilitas", "num_format": "0%", "min": 0})
    chart1.set_legend({"position": "bottom"})
    chart1.set_size({"width": 820, "height": 370})
    graph.insert_chart("B4", chart1)
    if reps:
        chart2 = book.add_chart({"type": "column"})
        for col, name, color in [("B", "Teori", "#1B6CA8"), ("H", "Simulasi", "#F59E0B")]:
            chart2.add_series({"name": name,
                               "categories": f"=Distribusi!$A$5:$A${end_row}",
                               "values": f"=Distribusi!${col}$5:${col}${end_row}",
                               "fill": {"color": color}, "border": {"none": True}})
        chart2.set_title({"name": "Teori vs Simulasi"})
        chart2.set_x_axis({"name": "Jumlah sukses (y)"})
        chart2.set_y_axis({"name": "Frekuensi relatif", "num_format": "0%", "min": 0})
        chart2.set_size({"width": 820, "height": 370})
        chart2.set_legend({"position": "bottom"})
        graph.insert_chart("B24", chart2)
        graph.print_area("A1:Q44")
    else:
        graph.print_area("A1:Q23")
    graph.set_landscape()
    graph.fit_to_pages(1, 2 if reps else 1)

    if simsheet is not None:
        simsheet.hide_gridlines(2)
        simsheet.set_column("A:A", 32)
        simsheet.set_column("B:B", 20)
        simsheet.set_column("C:F", 19)
        simsheet.merge_range("A1:F1", "SIMULASI MONTE CARLO", title)
        simsheet.write("A3", "Pengulangan", label)
        simsheet.write_number("B3", reps, integer)
        simsheet.write("A4", "Random seed", label)
        simsheet.write_number("B4", int(sim["seed"]), integer)
        simsheet.write("A5", "Probabilitas eksak", label)
        simsheet.write_number("B5", result["prob"], pct)
        simsheet.write("A6", "Probabilitas hasil simulasi", label)
        simsheet.write_formula("B6", f"=SUM(Distribusi!J5:J{end_row})", pct, float(np.sum(counts[mask])/reps))
        simsheet.write("A7", "Galat mutlak", label)
        simsheet.write_formula("B7", "=ABS(B6-B5)", pct,
                               abs(float(np.sum(counts[mask])/reps) - result["prob"]))
        simsheet.merge_range("A10:F11", "Simulasi bersifat acak. Hasil tidak harus identik dengan teori; "
                                 "cenderung mendekati nilai teoritis ketika pengulangan meningkat.", note)
        simsheet.fit_to_pages(1, 1)
        simsheet.print_area("A1:F11")

    if samplesheet is not None:
        samplesheet.hide_gridlines(2)
        samplesheet.set_column("A:A", 24)
        samplesheet.set_column("B:B", 18)
        samplesheet.set_column("C:C", 22)
        samplesheet.set_column("D:D", 19)
        samplesheet.merge_range("A1:D1", "RUANG SAMPEL (n ≤ 8)", title)
        for j, column in enumerate(["Susunan", "Jumlah sukses", "P(susunan)", "Kejadian?"]):
            samplesheet.write(2, j, column, header)
        for i, row in enumerate(space or [], start=3):
            count_success = row["Jumlah sukses"]
            chosen = row["Masuk kejadian"]
            samplesheet.write_string(i, 0, row["Pola"], label if chosen else txt)
            samplesheet.write_number(i, 1, count_success, integer)
            samplesheet.write_formula(i, 2,
                f"=(Ringkasan!$B$6^B{i+1})*((1-Ringkasan!$B$6)^(Ringkasan!$B$5-B{i+1}))",
                highlight_pct if chosen else pct, row["Probabilitas pola"])
            samplesheet.write_string(i, 3, "YA" if chosen else "TIDAK", yes if chosen else text_center)
        samplesheet.freeze_panes(3, 0)
        samplesheet.autofilter(2, 0, len(space or []) + 2, 3)
        samplesheet.fit_to_pages(1, 0)
        samplesheet.repeat_rows(0, 2)
    book.close()
    buffer.seek(0)
    return buffer.getvalue()


def combination(n: int, y: int) -> int:
    return comb(n, y)
