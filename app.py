import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# =========================================
# TÜRKÇE KARAKTER TEMİZLE
# =========================================

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

# =========================================
# SAYFA
# =========================================

st.set_page_config(
    page_title="COSHH Risk Sistemi",
    layout="wide"
)

st.title("COSHH Risk Sistemi")

# =========================================
# EXCEL
# =========================================

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

# =========================================
# KİMYASAL
# =========================================

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

# =========================================
# İŞLEM
# =========================================

islem = st.selectbox(
    "İşlem",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma"
    ]
)

sure = st.slider(
    "Süre (Saat)",
    1,
    8,
    1
)

miktar = st.number_input(
    "Kullanım Miktarı (kg/L)",
    min_value=0.0,
    value=1.0
)

maruziyet = st.selectbox(
    "Maruziyet Seviyesi",
    [
        "Düşük",
        "Orta",
        "Yüksek"
    ]
)

# =========================================
# PERSONEL
# =========================================

st.subheader("Personel Bilgileri")

calisan = st.text_input("Çalışan")
departman = st.text_input("Departman")
degerlendiren = st.text_input("Değerlendiren")

# =========================================
# HAVALANDIRMA
# =========================================

st.subheader("Havalandırma")

lokal = st.checkbox("Lokal Havalandırma")
genel = st.checkbox("Genel Havalandırma")

# =========================================
# PPE
# =========================================

st.subheader("PPE")

resp = st.checkbox("Respiratör")
eldiven = st.checkbox("Kimyasal Eldiven")
gozluk = st.checkbox("Koruyucu Gözlük")
yuzsiperi = st.checkbox("Yüz Siperi")
koruyucu = st.checkbox("Koruyucu Kıyafet")

# =========================================
# HESAPLA
# =========================================

if st.button("COSHH Değerlendir"):

    risk = 0

    # H Kodları

    if "H350" in hkod:
        risk += 5

    if "H340" in hkod:
        risk += 5

    if "H330" in hkod:
        risk += 4

    if "H314" in hkod:
        risk += 3

    # İşlem

    if islem == "Püskürtme":
        risk += 3

    elif islem == "Isıtma":
        risk += 2

    # Süre

    if sure >= 4:
        risk += 2

    # Miktar

    if miktar >= 100:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    # Maruziyet

    if maruziyet == "Yüksek":
        risk += 3

    elif maruziyet == "Orta":
        risk += 2

    # PPE

    if not lokal:
        risk += 2

    if not resp:
        risk += 2

    if not eldiven:
        risk += 1

    if not gozluk:
        risk += 1

    # =========================================
    # SONUÇ
    # =========================================

    if risk <= 5:
        sonuc = "DUSUK RISK"

    elif risk <= 10:
        sonuc = "ORTA RISK"

    else:
        sonuc = "YUKSEK RISK"

    # =========================================
    # HAZARD GROUP
    # =========================================

    if risk >= 12:
        hazard_group = "A"

    elif risk >= 8:
        hazard_group = "B"

    else:
        hazard_group = "C"

    # =========================================
    # CONTROL APPROACH
    # =========================================

    if hazard_group == "A":
        kontrol = "Control Approach 1"

    elif hazard_group == "B":
        kontrol = "Control Approach 2"

    else:
        kontrol = "Control Approach 3"

    # =========================================
    # EKRAN
    # =========================================

    if sonuc == "DUSUK RISK":

    st.success(sonuc)

elif sonuc == "ORTA RISK":

    st.warning(sonuc)

else:

    st.error(sonuc)

    st.subheader(kontrol)

    # =========================================
    # ÖNERİLER
    # =========================================

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

    st.subheader("Oneriler")

    for o in oneriler:
        st.write("•", o)

    # =========================================
    # PDF
    # =========================================

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    # Başlık

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(
        190,
        12,
        "COSHH RISK REPORT",
        ln=True
    )

    pdf.ln(10)

    # Bilgiler

    bilgiler = [

        ("Chemical", temizle(secili)),
        ("CAS No", temizle(cas)),
        ("H Codes", temizle(hkod)),
        ("Physical State", temizle(fiziksel)),
        ("Process", temizle(islem)),
        ("Duration", f"{sure} hours"),
        ("Amount", str(miktar)),
        ("Exposure", temizle(maruziyet)),
        ("Employee", temizle(calisan)),
        ("Department", temizle(departman)),
        ("Evaluator", temizle(degerlendiren)),
        ("Hazard Group", hazard_group),
        ("Risk Result", temizle(sonuc)),
        ("Control Approach", kontrol)

    ]

    for label, value in bilgiler:

        pdf.set_x(20)

        pdf.set_font("Helvetica", "B", 11)

        pdf.cell(
            45,
            8,
            f"{label}:",
            0,
            0
        )

        pdf.set_font("Helvetica", "", 11)

        pdf.cell(
            100,
            8,
            str(value),
            0,
            1
        )

    pdf.ln(5)

    # PPE

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(
        190,
        10,
        "PPE",
        ln=True
    )

    pdf.set_font("Helvetica", "", 11)

    ppe_list = [

        ("Respirator", resp),
        ("Gloves", eldiven),
        ("Goggles", gozluk),
        ("Face Shield", yuzsiperi),
        ("Protective Clothing", koruyucu)

    ]

    for label, value in ppe_list:

        pdf.set_x(20)

        pdf.cell(
            190,
            8,
            f"{label}: {value}",
            ln=True
        )

    pdf.ln(5)

    # ÖNERİLER

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(
        190,
        10,
        "Recommendations",
        ln=True
    )

    pdf.set_font("Helvetica", "", 11)

    for o in oneriler:

        pdf.set_x(20)

        pdf.cell(
            190,
            8,
            f"- {temizle(o)}",
            ln=True
        )

    pdf.ln(10)

    # Tarih

    pdf.set_font("Helvetica", "I", 9)

    pdf.set_x(20)

    pdf.cell(
        190,
        8,
        f"Generated: {datetime.now()}",
        ln=True
    )

    # =========================================
    # KAYDET
    # =========================================

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    # =========================================
    # DOWNLOAD
    # =========================================

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
