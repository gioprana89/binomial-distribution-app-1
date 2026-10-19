"""Uji regresi komputasi binomial & keluaran Excel (tanpa perlu menjalankan UI)."""
import sys
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
from xml.etree import ElementTree as ET
import unittest

import numpy as np
from scipy.stats import binom

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from binomial_core import compute, export_excel, enumerate_space, simulate

class TestBinomialCdf(unittest.TestCase):
    def test_contoh_kasus_4(self):
        r = compute(5, .2, "Paling banyak y", 2)
        self.assertAlmostEqual(r["prob"], .94208, places=12)
        self.assertAlmostEqual(r["cdf"][2], .94208, places=12)
        self.assertAlmostEqual(sum(r["pmf"][:3]), .94208, places=12)
        self.assertAlmostEqual(sum(r["pmf"]), 1., places=12)
        self.assertAlmostEqual(r["pmf"][0], .32768, places=12)
        self.assertAlmostEqual(r["pmf"][1], .40960, places=12)
        self.assertAlmostEqual(r["pmf"][2], .20480, places=12)

    def test_preserve_old_cases(self):
        r1 = compute(3, .5, "Tepat y", 2)
        r2 = compute(4, .8, "Tepat y", 3)
        r3 = compute(4, .1, "Paling sedikit y", 1)
        self.assertAlmostEqual(r1["prob"], .375)
        self.assertAlmostEqual(r2["prob"], .4096)
        self.assertAlmostEqual(r3["prob"], .3439)

    def test_edges_and_monotonicity(self):
        for n in [1, 5, 50, 100]:
            for p in [0, 0.1, 0.2, 0.5, 0.8, 1]:
                r = compute(n, p, "Paling banyak y", n//2)
                self.assertTrue(np.all(np.diff(r["cdf"]) >= -1e-12))
                self.assertAlmostEqual(r["cdf"][-1], 1., places=12)
                for k in [0, n//2, n]:
                    self.assertAlmostEqual(float(r["cdf"][k]), float(binom.cdf(k,n,p)), places=12)

    def test_excel_cdf_sheet_and_editable_charts(self):
        r = compute(5, .2, "Paling banyak y", 2)
        space = enumerate_space(5, .2, "Paling banyak y", 2, 0, 5, "E", "T")
        sim = simulate(5, .2, 1000, 2026)
        data = export_excel(r, sim, space, "Kasus 4 — Kesehatan", cdf_k=2)
        self.assertGreater(len(data), 10000)
        with ZipFile(BytesIO(data)) as archive:
            members = archive.namelist()
            self.assertIn('xl/worksheets/sheet3.xml', members)
            charts = [m for m in members if m.startswith('xl/charts/chart') and m.endswith('.xml')]
            self.assertGreaterEqual(len(charts), 4)
            workbook = archive.read('xl/workbook.xml').decode()
            self.assertIn('name="Kumulatif"', workbook)
            cumul = ET.fromstring(archive.read('xl/worksheets/sheet3.xml'))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            cells = {c.attrib['r']: c for c in cumul.findall('.//x:c',ns)}
            self.assertAlmostEqual(float(cells['B6'].find('x:v',ns).text), .94208, places=12)
            self.assertEqual(cells['B5'].find('x:v',ns).text, '2')
            self.assertIn('SUM(D11:D16)', cells['B6'].find('x:f',ns).text)
            self.assertIn('IF(A13<=$B$5', cells['D13'].find('x:f',ns).text)
            self.assertIn('Distribusi!F7', cells['C13'].find('x:f',ns).text)

    def test_excel_probability_boundary_formula(self):
        for p in [0.0, 1.0]:
            r = compute(3, p, "Paling banyak y", 1)
            data = export_excel(r, None, [], "Kasus batas", cdf_k=1)
            with ZipFile(BytesIO(data)) as archive:
                ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
                dist = ET.fromstring(archive.read('xl/worksheets/sheet2.xml'))
                cells = {c.attrib['r']: c for c in dist.findall('.//x:c', ns)}
                self.assertIn('IF(Ringkasan!$B$6=0', cells['B5'].find('x:f',ns).text)
                self.assertAlmostEqual(float(cells['B5'].find('x:v',ns).text), float(binom.pmf(0,3,p)))

    def test_no_sim_excel(self):
        r = compute(4, .8, "Tepat y", 3)
        data = export_excel(r, None, [], "Kasus 2", cdf_k=3)
        with ZipFile(BytesIO(data)) as archive:
            self.assertIn('name="Kumulatif"', archive.read('xl/workbook.xml').decode())
            cumul = ET.fromstring(archive.read('xl/worksheets/sheet3.xml'))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            cells = {c.attrib['r']: c for c in cumul.findall('.//x:c',ns)}
            self.assertAlmostEqual(float(cells['B6'].find('x:v',ns).text), .5904, places=12) # P(Y≤3)=1-(.8)^4

if __name__ == '__main__':
    unittest.main()
