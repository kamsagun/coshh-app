import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# =====================================================
# TÜRKÇE KARAKTER TEMİZLEME
# =====================================================

def temizle(text):

    text = str(text)

    degisim = {
        "İ":"I",
        "ı":"i",
        "Ş":"S",
        "ş":"s",
        "Ğ":"G",
        "ğ":"g",
        "Ü":"U",
        "ü":"u",
        "Ö":"O",
        "ö":"o",
        "Ç":"C",
        "ç":"c"
    }

    for k, v in degisim.items():
        text = text.replace(k, v)

    return text

# =====================================================
# SAYFA AYARI
# =====================================================

st.set_page_config(
    page_title="COSHH Risk Sistemi",
    layout="wide"
)

st.title("COSHH Risk Sistemi")

# =====================================================
# EXCEL OKU
# =====================================================

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

# =====================================================
# KİMYASAL SEÇ
# =====================================================

kimyasallar = df["Kimyasal Adı"].dropna().unique()

secili = st.selectbox(
    "Kimyasal Seç",
    sorted(kimyasallar)
)

satir = df[df["Kimyasal Adı"] == secili].iloc[0]

cas = str(satir.get("CAS No", "-"))
hkod = str(satir.get("H Kodları", "-"))
fiziksel = str(satir.get("Fiziksel Hal", "-"))

st.write("CAS:", cas)
st.write("H Kodları:", hkod)
st.write("Fiziksel Hal:", fiziksel)

st.divider()

# =====================================================
# İŞLEM
# =====================================================

islem = st.selectbox(
    "İşlem",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma"
    ]
)

# =====================================================
# SÜRE
# =====================================================

sure = st.slider(
    "Süre (Saat)",
    0,
    8,
    1
)

# =====================================================
# MİKTAR
# =====================================================

miktar = st.number_input(
    "Kullanım Miktarı (kg/L)",
    min_value=0.0,
    value=1.0
)

# =====================================================
# MARUZİYET
# =====================================================

maruziyet = st.selectbox(
    "Maruziyet",
    [
        "Dusuk",
        "Orta",
        "Yuksek"
    ]
)

# =====================================================
# BANDING
# =====================================================

if "Sivi" in fiziksel or "sivi" in fiziksel:

    banding = st.selectbox(
        "Uçuculuk",
        [
            "Dusuk",
            "Orta",
            "Yuksek"
        ]
    )

else:

    banding = st.selectbox(
        "Tozluluk",
        [
            "Dusuk",
            "Orta",
            "Yuksek"
        ]
    )

st.divider()

# =====================================================
# HAVALANDIRMA
# =====================================================

st.subheader("Havalandırma")

lokal = st.checkbox("Lokal Havalandırma")

genel = st.checkbox("Genel Havalandırma")

st.divider()

# =====================================================
# PPE
# =====================================================

st.subheader("PPE")

resp = st.checkbox("Respiratör")

eldiven = st.checkbox("Kimyasal Eldiven")

gozluk = st.checkbox("Koruyucu Gözlük")

yuzsiperi = st.checkbox("Yüz Siperi")

koruyucu = st.checkbox("Koruyucu Kıyafet")

st.divider()

# =====================================================
# PERSONEL
# =====================================================

calisan = st.text_input("Çalışan Adı")

departman = st.text_input("Departman")

degerlendiren = st.text_input("Değerlendiren")

st.divider()

# =====================================================
# DEĞERLENDİR
# =====================================================

if st.button("COSHH Değerlendir"):

    risk = 0

    # =====================================================
    # H KODLARI
    # =====================================================

    if "H350" in hkod:
        risk += 5

    if "H340" in hkod:
        risk += 5

    if "H330" in hkod:
        risk += 4

    if "H310" in hkod:
        risk += 4

    if "H314" in hkod:
        risk += 2

    # =====================================================
    # İŞLEM
    # =====================================================

    if islem == "Püskürtme":
        risk += 4

    elif islem == "Isıtma":
        risk += 3

    elif islem == "Transfer":
        risk += 2

    # =====================================================
    # SÜRE
    # =====================================================

    if sure >= 4:
        risk += 3

    elif sure >= 2:
        risk += 2

    # =====================================================
    # MİKTAR
    # =====================================================

    if miktar >= 50:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    # =====================================================
    # MARUZİYET
    # =====================================================

    if maruziyet == "Yuksek":
        risk += 4

    elif maruziyet == "Orta":
        risk += 2

    # =====================================================
    # BANDING
    # =====================================================

    if banding == "Yuksek":
        risk += 4

    elif banding == "Orta":
        risk += 2

    # =====================================================
    # HAVALANDIRMA
    # =====================================================

    if not lokal:
        risk += 2

    if not genel:
        risk += 1

    # =====================================================
    # PPE
    # =====================================================

    if not resp:
        risk += 2

    if not eldiven:
        risk += 1

    if not gozluk:
        risk += 1

    # =====================================================
    # SONUÇ
    # =====================================================

    if risk <= 5:
        sonuc = "DUSUK RISK"

    elif risk <= 10:
        sonuc = "ORTA RISK"

    else:
        sonuc = "YUKSEK RISK"

    # =====================================================
    # HAZARD GROUP
    # =====================================================

    hazard_group = "A"

    if "H315" in hkod or "H319" in hkod:
        hazard_group = "B"

    if "H331" in hkod or "H311" in hkod:
        hazard_group = "C"

    if "H350" in hkod or "H340" in hkod:
        hazard_group = "E"

    # =====================================================
    # CONTROL APPROACH
    # =====================================================

    kontrol = "Control Approach 1"

    if hazard_group == "B":
        kontrol = "Control Approach 2"

    elif hazard_group == "C":
        kontrol = "Control Approach 3"

    elif hazard_group == "E":
        kontrol = "Control Approach 4"

    # =====================================================
    # ÖNERİLER
    # =====================================================

    oneriler = []

    if not lokal:
        oneriler.append("Lokal havalandirma onerilir")

    if not genel:
        oneriler.append("Genel havalandirma yeterli olmayabilir")

    if not resp:
        oneriler.append("Respirator onerilir")

    if not eldiven:
        oneriler.append("Kimyasal dayanimli eldiven onerilir")

    if not gozluk:
        oneriler.append("Koruyucu gozluk onerilir")

    if hazard_group == "E":
        oneriler.append("Kanserojen proseduru uygulanmali")

    if kontrol == "Control Approach 4":
        oneriler.append("Containment sistemi gerekli")

    if banding == "Yuksek":
        oneriler.append("Local exhaust ventilation gerekli")

    if maruziyet == "Yuksek":
        oneriler.append("Maruziyet suresi azaltilmali")

    if fiziksel.lower() == "sivi":
        oneriler.append("Sicrama riskine dikkat edilmeli")

    # =====================================================
    # EKRAN SONUÇ
    # =====================================================

    st.subheader("Risk Sonucu")

    if risk <= 5:

        st.success(f"{sonuc} | Risk Skoru: {risk}")

    elif risk <= 10:

        st.warning(f"{sonuc} | Risk Skoru: {risk}")

    else:

        st.error(f"{sonuc} | Risk Skoru: {risk}")

    st.write("Hazard Group:", hazard_group)

    st.write("Control Approach:", kontrol)

    st.write("Banding:", banding)

    st.subheader("Öneriler")

    for o in oneriler:
        st.write("•", o)

    st.divider()

    # =====================================================
    # PDF
    # =====================================================

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    # =====================================================
    # BAŞLIK
    # =====================================================

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(190, 12, "COSHH RISK REPORT", 0, 1)

    pdf.ln(5)

    # =====================================================
    # RAPOR BİLGİLERİ
    # =====================================================

    bilgiler = [

        ("Chemical", temizle(secili)),
        ("CAS No", temizle(cas)),
        ("H Codes", temizle(hkod)),
        ("Physical State", temizle(fiziksel)),
        ("Process", temizle(islem)),
        ("Duration", f"{sure} hours"),
        ("Amount", str(miktar)),
        ("Exposure", temizle(maruziyet)),
        ("Banding", temizle(banding)),
        ("Employee", temizle(calisan)),
        ("Department", temizle(departman)),
        ("Evaluator", temizle(degerlendiren)),
        ("Hazard Group", hazard_group),
        ("Risk Result", temizle(sonuc)),
        ("Control Approach", kontrol)

    ]

    for label, value in bilgiler:

        pdf.set_font("Helvetica", "B", 12)

        pdf.cell(60, 8, f"{label}:", 0, 0)

        pdf.set_font("Helvetica", "", 12)

        pdf.cell(120, 8, value, 0, 1)

    pdf.ln(5)

    # =====================================================
    # PPE
    # =====================================================

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(190, 10, "PPE", 0, 1)

    pdf.set_font("Helvetica", "", 12)

    ppe_list = [

        ("Respirator", resp),
        ("Gloves", eldiven),
        ("Goggles", gozluk),
        ("Face Shield", yuzsiperi),
        ("Protective Clothing", koruyucu)

    ]

    for label, value in ppe_list:

        pdf.cell(190, 8, f"{label}: {value}", 0, 1)

    pdf.ln(5)

    # =====================================================
    # ÖNERİLER
    # =====================================================

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(190, 10, "Recommendations", 0, 1)

    pdf.set_font("Helvetica", "", 12)

    for o in oneriler:

        pdf.multi_cell(
            190,
            8,
            f"- {temizle(o)}"
        )

    # =====================================================
    # TARİH
    # =====================================================

    pdf.ln(10)

    pdf.set_font("Helvetica", "I", 10)

    pdf.cell(
        190,
        8,
        f"Generated: {datetime.now()}",
        0,
        1
    )

    # =====================================================
    # KAYDET
    # =====================================================

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    # =====================================================
    # İNDİR
    # =====================================================

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
