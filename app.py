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

# -----------------------------------
# Sayfa
# -----------------------------------

st.set_page_config(
    page_title="COSHH Risk Sistemi",
    layout="wide"
)

st.title("COSHH Risk Sistemi")

# -----------------------------------
# Excel oku
# -----------------------------------

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(FILE, sheet_name="DB")

df.columns = df.columns.astype(str)

# -----------------------------------
# Kimyasal seç
# -----------------------------------

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

# -----------------------------------
# İşlem
# -----------------------------------

islem = st.selectbox(
    "İşlem",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma"
    ]
)

# -----------------------------------
# Süre
# -----------------------------------

sure = st.slider(
    "Süre (Saat)",
    0,
    8,
    1
)

# -----------------------------------
# Miktar
# -----------------------------------

miktar = st.number_input(
    "Kullanım Miktarı (kg/L)",
    min_value=0.0,
    value=1.0
)

# -----------------------------------
# Maruziyet
# -----------------------------------

maruziyet = st.selectbox(
    "Maruziyet",
    [
        "Dusuk",
        "Orta",
        "Yuksek"
    ]
)

# -----------------------------------
# Banding
# -----------------------------------

banding = "Dusuk"

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

# -----------------------------------
# Havalandırma
# -----------------------------------

st.subheader("Havalandırma")

lokal = st.checkbox("Lokal Havalandırma")

genel = st.checkbox("Genel Havalandırma")

st.divider()

# -----------------------------------
# PPE
# -----------------------------------

st.subheader("PPE")

resp = st.checkbox("Respiratör")

eldiven = st.checkbox("Kimyasal Eldiven")

gozluk = st.checkbox("Koruyucu Gözlük")

yuzsiperi = st.checkbox("Yüz Siperi")

koruyucu = st.checkbox("Koruyucu Kıyafet")

st.divider()

# -----------------------------------
# Personel bilgileri
# -----------------------------------

calisan = st.text_input("Çalışan Adı")

departman = st.text_input("Departman")

degerlendiren = st.text_input("Değerlendiren")

st.divider()

# -----------------------------------
# Değerlendirme
# -----------------------------------

if st.button("COSHH Değerlendir"):

    risk = 0

    # -----------------------------------
    # H kodları
    # -----------------------------------

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

    # -----------------------------------
    # İşlem
    # -----------------------------------

    if islem == "Püskürtme":
        risk += 4

    elif islem == "Isıtma":
        risk += 3

    elif islem == "Transfer":
        risk += 2

    # -----------------------------------
    # Süre
    # -----------------------------------

    if sure >= 4:
        risk += 3

    elif sure >= 2:
        risk += 2

    # -----------------------------------
    # Miktar
    # -----------------------------------

    if miktar >= 50:
        risk += 3

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    # -----------------------------------
    # Maruziyet
    # -----------------------------------

    if maruziyet == "Yuksek":
        risk += 4

    elif maruziyet == "Orta":
        risk += 2

    # -----------------------------------
    # Banding
    # -----------------------------------

    if banding == "Yuksek":
        risk += 4

    elif banding == "Orta":
        risk += 2

    # -----------------------------------
    # Havalandırma
    # -----------------------------------

    if not lokal:
        risk += 2

    if not genel:
        risk += 1

    # -----------------------------------
    # PPE
    # -----------------------------------

    if not resp:
        risk += 2

    if not eldiven:
        risk += 1

    if not gozluk:
        risk += 1

    # -----------------------------------
    # Sonuç
    # -----------------------------------

    if risk <= 5:
        sonuc = "DUSUK RISK"

    elif risk <= 10:
        sonuc = "ORTA RISK"

    else:
        sonuc = "YUKSEK RISK"

    # -----------------------------------
    # Hazard Group
    # -----------------------------------

    hazard_group = "A"

    if "H315" in hkod or "H319" in hkod:
        hazard_group = "B"

    if "H331" in hkod or "H311" in hkod:
        hazard_group = "C"

    if "H350" in hkod or "H340" in hkod:
        hazard_group = "E"

    # -----------------------------------
    # Control Approach
    # -----------------------------------

    kontrol = "Control Approach 1"

    if hazard_group == "B":
        kontrol = "Control Approach 2"

    elif hazard_group == "C":
        kontrol = "Control Approach 3"

    elif hazard_group == "E":
        kontrol = "Control Approach 4"

    # -----------------------------------
    # Ekran Sonuç
    # -----------------------------------

    st.header(sonuc)

    st.write(f"Hazard Group: {hazard_group}")

    st.write(f"Control Approach: {kontrol}")

    st.write(f"Banding: {banding}")

    # -----------------------------------
    # Öneriler
    # -----------------------------------

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

    st.subheader("Öneriler")

    for o in oneriler:
        st.write("•", o)

    st.divider()

    # -----------------------------------
    # PDF
    # -----------------------------------

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(auto=True, margin=15)

    # Başlık

    pdf.set_font("Helvetica", "B", 18)

    pdf.cell(190, 10, "COSHH RISK REPORT", ln=True)

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

        pdf.cell(60, 10, f"{label}:", 0, 0)

        pdf.set_font("Helvetica", "", 12)

        pdf.multi_cell(120, 10, value)

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

        pdf.cell(190, 10, f"{label}: {value}", ln=True)

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

    pdf.ln(10)

    pdf.set_font("Helvetica", "I", 10)

    pdf.cell(
        190,
        10,
        f"Generated: {datetime.now()}",
        ln=True
    )

    # -----------------------------------
    # Kaydet
    # -----------------------------------

    filename = "COSHH_REPORT.pdf"

    pdf.output(filename)

    # -----------------------------------
    # İndir
    # -----------------------------------

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
