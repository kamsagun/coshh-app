import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# =====================================================
# TÜRKÇE KARAKTER TEMİZLE
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
# SAYFA
# =====================================================

st.set_page_config(
    page_title="COSHH Risk Sistemi",
    layout="wide"
)

st.title("COSHH Risk Sistemi")

# =====================================================
# EXCEL
# =====================================================

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

# =====================================================
# KİMYASAL
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

# =====================================================
# FORM
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

# =====================================================
# QUANTITY BAND
# =====================================================

if miktar < 1:

    miktar_band = "Small"

elif miktar < 100:

    miktar_band = "Medium"

else:

    miktar_band = "Large"

maruziyet = st.selectbox(
    "Maruziyet Seviyesi",
    [
        "Düşük",
        "Orta",
        "Yüksek"
    ]
)

ucuculuk = st.selectbox(
    "Uçuculuk / Tozuma",
    [
        "Düşük",
        "Orta",
        "Yüksek"
    ]
)

# =====================================================
# PERSONEL
# =====================================================

st.subheader("Personel Bilgileri")

calisan = st.text_input("Çalışan")
departman = st.text_input("Departman")
degerlendiren = st.text_input("Değerlendiren")

# =====================================================
# HAVALANDIRMA
# =====================================================

st.subheader("Havalandırma")

lokal = st.checkbox("Lokal Havalandırma")
genel = st.checkbox("Genel Havalandırma")

# =====================================================
# PPE
# =====================================================

st.subheader("PPE")

resp = st.checkbox("Respiratör")
eldiven = st.checkbox("Kimyasal Eldiven")
gozluk = st.checkbox("Koruyucu Gözlük")
yuzsiperi = st.checkbox("Yüz Siperi")
koruyucu = st.checkbox("Koruyucu Kıyafet")

# =====================================================
# BİLGİLER
# =====================================================

st.divider()

st.write("CAS:", cas)
st.write("H Kodları:", hkod)
st.write("Fiziksel Hal:", fiziksel)
st.write("Miktar Bandı:", miktar_band)

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

    if "H314" in hkod:
        risk += 3

    # =====================================================
    # İŞLEM
    # =====================================================

    if islem == "Püskürtme":
        risk += 3

    elif islem == "Isıtma":
        risk += 2

    # =====================================================
    # SÜRE
    # =====================================================

    if sure >= 4:
        risk += 2

    # =====================================================
    # MİKTAR
    # =====================================================

    if miktar >= 100:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    # =====================================================
    # FİZİKSEL HAL
    # =====================================================

    fiziksel_lower = fiziksel.lower()

    if "gaz" in fiziksel_lower:
        risk += 3

    elif "buhar" in fiziksel_lower:
        risk += 2

    elif "toz" in fiziksel_lower:
        risk += 2

    elif "sivi" in fiziksel_lower:
        risk += 1

    # =====================================================
    # MARUZİYET
    # =====================================================

    if maruziyet == "Yüksek":
        risk += 3

    elif maruziyet == "Orta":
        risk += 2

    # =====================================================
    # UÇUCULUK
    # =====================================================

    if ucuculuk == "Yüksek":
        risk += 3

    elif ucuculuk == "Orta":
        risk += 2

    # =====================================================
    # PPE ETKİSİ
    # =====================================================

    if not lokal:
        risk += 2

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

    if (
        "H300" in hkod or
        "H310" in hkod or
        "H330" in hkod or
        "H340" in hkod or
        "H350" in hkod
    ):

        hazard_group = "E"

    elif (
        "H301" in hkod or
        "H311" in hkod or
        "H331" in hkod
    ):

        hazard_group = "D"

    elif (
        "H314" in hkod or
        "H318" in hkod
    ):

        hazard_group = "C"

    elif (
        "H315" in hkod or
        "H319" in hkod
    ):

        hazard_group = "B"

    # =====================================================
    # CONTROL APPROACH
    # =====================================================

    if hazard_group == "E":

        kontrol = "Control Approach 4"

    elif hazard_group == "D":

        if ucuculuk == "Yüksek":

            kontrol = "Control Approach 4"

        elif miktar_band == "Large":

            kontrol = "Control Approach 4"

        else:

            kontrol = "Control Approach 3"

    elif hazard_group == "C":

        if miktar_band == "Large":

            kontrol = "Control Approach 3"

        elif ucuculuk == "Yüksek":

            kontrol = "Control Approach 3"

        else:

            kontrol = "Control Approach 2"

    elif hazard_group == "B":

        if ucuculuk == "Yüksek":

            kontrol = "Control Approach 2"

        else:

            kontrol = "Control Approach 1"

    else:

        kontrol = "Control Approach 1"

    # =====================================================
    # GEREKLİ PPE
    # =====================================================

    gerekli_ppe = []

    if "gaz" in fiziksel_lower:
        gerekli_ppe.append("Respirator")

    if "H314" in hkod:
        gerekli_ppe.append("Kimyasal Eldiven")

    if islem == "Püskürtme":
        gerekli_ppe.append("Koruyucu Gozluk")

    if hazard_group in ["D", "E"]:
        gerekli_ppe.append("Yuz Siperi")

    # =====================================================
    # CONTROL MEASURES
    # =====================================================

    kontrol_onlemleri = []

    if kontrol == "Control Approach 4":

        kontrol_onlemleri.append(
            "Containment sistemi kullanilmali"
        )

    if kontrol == "Control Approach 3":

        kontrol_onlemleri.append(
            "Local Exhaust Ventilation gerekli"
        )

    if hazard_group in ["D", "E"]:

        kontrol_onlemleri.append(
            "Yetkili personel ile calisilmali"
        )

    if "gaz" in fiziksel_lower:

        kontrol_onlemleri.append(
            "Gaz detector sistemi onerilir"
        )

    if islem == "Püskürtme":

        kontrol_onlemleri.append(
            "Kapali sistem onerilir"
        )

    # =====================================================
    # ÖNERİLER
    # =====================================================

    oneriler = []

    if not lokal:

        oneriler.append(
            "Lokal havalandirma onerilir"
        )

    if not genel:

        oneriler.append(
            "Genel havalandirma yeterli olmayabilir"
        )

    if not resp:

        oneriler.append(
            "Respirator onerilir"
        )

    if not eldiven:

        oneriler.append(
            "Kimyasal dayanimli eldiven onerilir"
        )

    if not gozluk:

        oneriler.append(
            "Koruyucu gozluk onerilir"
        )

    # =====================================================
    # EKRAN SONUÇ
    # =====================================================

    if sonuc == "DUSUK RISK":

        st.success(sonuc)

    elif sonuc == "ORTA RISK":

        st.warning(sonuc)

    else:

        st.error(sonuc)

    st.subheader("Hazard Group")
    st.write(hazard_group)

    st.subheader("Control Approach")
    st.write(kontrol)

    st.subheader("Control Measures")

    for k in kontrol_onlemleri:

        st.write("•", k)

    st.subheader("Recommendations")

    for o in oneriler:

        st.write("•", o)

    # =====================================================
    # PDF
    # =====================================================

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # =====================================================
    # BAŞLIK
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        18
    )

    pdf.cell(
        190,
        10,
        "COSHH RISK REPORT",
        ln=True,
        align="C"
    )

    pdf.ln(10)

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
        ("Quantity Band", miktar_band),
        ("Exposure", temizle(maruziyet)),
        ("Volatility", temizle(ucuculuk)),
        ("Employee", temizle(calisan)),
        ("Department", temizle(departman)),
        ("Evaluator", temizle(degerlendiren)),
        ("Hazard Group", hazard_group),
        ("Risk Result", sonuc),
        ("Control Approach", kontrol)

    ]

    for label, value in bilgiler:

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        pdf.cell(
            60,
            8,
            f"{label}:",
            0,
            0
        )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        pdf.cell(
            100,
            8,
            str(value),
            0,
            1
        )

    pdf.ln(5)

    # =====================================================
    # PPE PDF
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "Current PPE",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    ppe_list = [

        ("Respirator", resp),
        ("Gloves", eldiven),
        ("Goggles", gozluk),
        ("Face Shield", yuzsiperi),
        ("Protective Clothing", koruyucu)

    ]

    for label, value in ppe_list:

        pdf.cell(
            190,
            8,
            f"{label}: {value}",
            ln=True
        )

    pdf.ln(5)

    # =====================================================
    # CONTROL MEASURES PDF
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "Control Measures",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for k in kontrol_onlemleri:

        pdf.cell(
            190,
            8,
            "- " + temizle(k),
            ln=True
        )

    pdf.ln(5)

    # =====================================================
    # ÖNERİLER PDF
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "Recommendations",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for o in oneriler:

        pdf.cell(
            190,
            8,
            "- " + temizle(o),
            ln=True
        )

    pdf.ln(10)

    # =====================================================
    # TARİH
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "I",
        9
    )

    pdf.cell(
        190,
        8,
        f"Generated: {datetime.now()}",
        ln=True
    )

    # =====================================================
    # PDF KAYDET
    # =====================================================

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    # =====================================================
    # DOWNLOAD
    # =====================================================

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
