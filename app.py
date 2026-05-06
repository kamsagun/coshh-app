import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# -----------------------------------
# Türkçe karakter temizleme
# -----------------------------------

def temizle(text):

    text = str(text)

    degisim = {
        "İ":"I","ı":"i",
        "Ş":"S","ş":"s",
        "Ğ":"G","ğ":"g",
        "Ü":"U","ü":"u",
        "Ö":"O","ö":"o",
        "Ç":"C","ç":"c"
    }

    for k,v in degisim.items():
        text = text.replace(k,v)

    return text

# -----------------------------------
# Sayfa Ayarı
# -----------------------------------

st.set_page_config(
    page_title="COSHH Risk Sistemi",
    layout="wide"
)

# -----------------------------------
# Excel Oku
# -----------------------------------

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

# -----------------------------------
# Başlık
# -----------------------------------

st.title("COSHH Risk Sistemi")

# -----------------------------------
# Kimyasal Seç
# -----------------------------------

kimyasallar = df["Kimyasal Adı"].dropna().unique()

secili = st.selectbox(
    "Kimyasal Seç",
    sorted(kimyasallar)
)

satir = df[df["Kimyasal Adı"] == secili].iloc[0]

cas = str(satir.get("CAS No","-"))
hkod = str(satir.get("H Kodları","-"))
fiziksel = str(satir.get("Fiziksel Hal","-"))

# -----------------------------------
# Kimyasal Bilgileri
# -----------------------------------

st.subheader("Kimyasal Bilgileri")

st.write("CAS No:", cas)
st.write("H Kodları:", hkod)
st.write("Fiziksel Hal:", fiziksel)

st.divider()

# -----------------------------------
# İş Bilgileri
# -----------------------------------

st.subheader("İş Bilgileri")

islem = st.selectbox(
    "İşlem Türü",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma",
        "Temizlik"
    ]
)

sure = st.slider(
    "Maruziyet Süresi (Saat)",
    0,
    12,
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
        "Dusuk",
        "Orta",
        "Yuksek"
    ]
)

st.divider()

# -----------------------------------
# Personel Bilgileri
# -----------------------------------

st.subheader("Personel Bilgileri")

calisan = st.text_input("Çalışan")
departman = st.text_input("Departman")
degerlendiren = st.text_input("Değerlendiren")

st.divider()

# -----------------------------------
# Havalandırma
# -----------------------------------

st.subheader("Havalandırma")

havalandirma = st.checkbox(
    "Lokal Havalandırma Var"
)

# -----------------------------------
# PPE
# -----------------------------------

st.subheader("PPE")

resp = st.checkbox("Respiratör")
eldiven = st.checkbox("Kimyasal Eldiven")
gozluk = st.checkbox("Koruyucu Gözlük")
yuzsiperi = st.checkbox("Yüz Siperi")
koruyucu = st.checkbox("Koruyucu Kıyafet")

# -----------------------------------
# COSHH Hesaplama
# -----------------------------------

if st.button("COSHH Değerlendir"):

    # -----------------------------------
    # Hazard Group
    # -----------------------------------

    hazard_group = "A"

    if "H350" in hkod or "H340" in hkod:
        hazard_group = "E"

    elif "H330" in hkod or "H310" in hkod:
        hazard_group = "D"

    elif "H315" in hkod or "H319" in hkod:
        hazard_group = "B"

    elif "H335" in hkod or "H336" in hkod:
        hazard_group = "C"

    # -----------------------------------
    # Risk Hesabı
    # -----------------------------------

    risk = 0

    if "H350" in hkod:
        risk += 5

    if "H340" in hkod:
        risk += 5

    if "H330" in hkod:
        risk += 4

    if islem == "Püskürtme":
        risk += 3

    if sure >= 8:
        risk += 4

    elif sure >= 4:
        risk += 2

    if miktar >= 100:
        risk += 4

    elif miktar >= 50:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    if maruziyet == "Yuksek":
        risk += 4

    elif maruziyet == "Orta":
        risk += 2

    if not havalandirma:
        risk += 3

    if not resp:
        risk += 2

    if not eldiven:
        risk += 1

    if not gozluk:
        risk += 1

    if not koruyucu:
        risk += 1

    # -----------------------------------
    # Risk Sonucu
    # -----------------------------------

    if risk <= 5:
        sonuc = "DUSUK RISK"

    elif risk <= 10:
        sonuc = "ORTA RISK"

    else:
        sonuc = "YUKSEK RISK"

    # -----------------------------------
    # Control Approach
    # -----------------------------------

    kontrol = "1"

    if risk >= 15:
        kontrol = "4"

    elif risk >= 10:
        kontrol = "3"

    elif risk >= 5:
        kontrol = "2"

    # -----------------------------------
    # Sonuç Göster
    # -----------------------------------

    st.header(sonuc)

    st.subheader(f"CONTROL APPROACH {kontrol}")

    st.write(f"Hazard Group: {hazard_group}")

    # -----------------------------------
    # Öneriler
    # -----------------------------------

    oneriler = []

    if not havalandirma:
        oneriler.append("Lokal havalandirma onerilir")

    if kontrol == "2":
        oneriler.append("Genel havalandirma yeterli olabilir")

    if kontrol == "3":
        oneriler.append("Lokal emis sistemi gerekli")

    if kontrol == "4":
        oneriler.append("Containment gerekli")

    if not resp:
        oneriler.append("Respirator onerilir")

    if not eldiven:
        oneriler.append("Kimyasal dayanimli eldiven onerilir")

    if not gozluk:
        oneriler.append("Koruyucu gozluk onerilir")

    st.subheader("Öneriler")

    for o in oneriler:
        st.write("•", o)

    # -----------------------------------
    # PDF Oluştur
    # -----------------------------------

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    # Başlık

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(190, 12, "COSHH RISK REPORT", ln=True)

    pdf.ln(8)

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
        ("Control Approach", kontrol),
        ("Risk Result", temizle(sonuc))

    ]

    for label, value in bilgiler:

        pdf.set_font("Helvetica", "B", 12)

        pdf.cell(55, 10, f"{label}:")

        pdf.set_font("Helvetica", "", 12)

        pdf.cell(120, 10, str(value), ln=True)

    pdf.ln(5)

    # PPE

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(190, 10, "PPE", ln=True)

    pdf.set_font("Helvetica", "", 12)

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
            10,
            f"{label}: {value}",
            ln=True
        )

    pdf.ln(5)

    # Öneriler

    pdf.set_font("Helvetica", "B", 14)

    pdf.cell(190, 10, "Recommendations", ln=True)

    pdf.set_font("Helvetica", "", 12)

    for o in oneriler:

        pdf.multi_cell(
            190,
            10,
            f"- {temizle(o)}"
        )

    # Tarih

    pdf.ln(10)

    pdf.set_font("Helvetica", "I", 10)

    pdf.cell(
        190,
        10,
        f"Generated: {datetime.now()}",
        ln=True
    )

    # Kaydet

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    # İndir

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
