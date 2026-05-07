import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from PIL import Image
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
    page_title="COSHH Professional",
    layout="wide"
)

st.title("COSHH Professional Risk Assessment")

# =====================================================
# EXCEL
# =====================================================

FILE = "020526 COSHH MAKRO.xlsm"

df = pd.read_excel(
    FILE,
    sheet_name="DB"
)

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
    "İşlem Türü",
    [
        "Karıştırma",
        "Transfer",
        "Püskürtme",
        "Isıtma",
        "Dolum",
        "Numune Alma",
        "Temizlik"
    ]
)

sure = st.slider(
    "Çalışma Süresi (Saat)",
    1,
    12,
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

# =====================================================
# MARUZİYET
# =====================================================

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
# ÇALIŞMA ORTAMI
# =====================================================

st.subheader("Çalışma Ortamı")

kapali_alan = st.checkbox("Kapalı Alan")
sicak_islem = st.checkbox("Sıcak İşlem")
vardiya = st.checkbox("Uzun Vardiya")
yetersiz_hijyen = st.checkbox("Yetersiz Hijyen")
dar_alan = st.checkbox("Dar Alan")

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
lev = st.checkbox("LEV Sistemi")

# =====================================================
# PPE
# =====================================================

st.subheader("Kullanılan PPE")

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
        risk += 6

    if "H340" in hkod:
        risk += 5

    if "H330" in hkod:
        risk += 5

    if "H334" in hkod:
        risk += 5

    if "H317" in hkod:
        risk += 3

    if "H314" in hkod:
        risk += 4

    if "H315" in hkod:
        risk += 2

    if "H319" in hkod:
        risk += 2

    # =====================================================
    # İŞLEM
    # =====================================================

    if islem == "Püskürtme":
        risk += 5

    elif islem == "Isıtma":
        risk += 4

    elif islem == "Dolum":
        risk += 2

    elif islem == "Temizlik":
        risk += 2

    # =====================================================
    # SÜRE
    # =====================================================

    if sure >= 8:
        risk += 3

    elif sure >= 4:
        risk += 2

    # =====================================================
    # MİKTAR
    # =====================================================

    if miktar >= 100:
        risk += 4

    elif miktar >= 10:
        risk += 2

    elif miktar >= 1:
        risk += 1

    # =====================================================
    # FİZİKSEL HAL
    # =====================================================

    fiziksel_lower = fiziksel.lower()

    if "gaz" in fiziksel_lower:
        risk += 5

    elif "buhar" in fiziksel_lower:
        risk += 4

    elif "toz" in fiziksel_lower:
        risk += 4

    elif "sivi" in fiziksel_lower:
        risk += 1

    # =====================================================
    # MARUZİYET
    # =====================================================

    if maruziyet == "Yüksek":
        risk += 4

    elif maruziyet == "Orta":
        risk += 2

    # =====================================================
    # UÇUCULUK
    # =====================================================

    if ucuculuk == "Yüksek":
        risk += 4

    elif ucuculuk == "Orta":
        risk += 2

    # =====================================================
    # ORTAM
    # =====================================================

    if kapali_alan:
        risk += 3

    if sicak_islem:
        risk += 2

    if vardiya:
        risk += 1

    if yetersiz_hijyen:
        risk += 2

    if dar_alan:
        risk += 2

    # =====================================================
    # PPE ETKİSİ
    # =====================================================

    if not lokal:
        risk += 2

    if not lev:
        risk += 3

    if not resp:
        risk += 2

    # =====================================================
    # RİSK SONUCU
    # =====================================================

    if risk <= 10:

        sonuc = "DUSUK RISK"

    elif risk <= 22:

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
        "H331" in hkod or
        "H334" in hkod
    ):

        hazard_group = "D"

    elif (
        "H314" in hkod or
        "H318" in hkod
    ):

        hazard_group = "C"

    elif (
        "H315" in hkod or
        "H319" in hkod or
        "H317" in hkod
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

        else:

            kontrol = "Control Approach 3"

    elif hazard_group == "C":

        kontrol = "Control Approach 2"

    else:

        kontrol = "Control Approach 1"

    # =====================================================
    # GEREKLİ PPE
    # =====================================================

    gerekli_ppe = []

    eksik_ppe = []

    if "gaz" in fiziksel_lower:

        gerekli_ppe.append("Respirator")

    if "toz" in fiziksel_lower:

        gerekli_ppe.append("Respirator")

    if "H314" in hkod:

        gerekli_ppe.append("Kimyasal Eldiven")

    if "H317" in hkod:

        gerekli_ppe.append("Kimyasal Eldiven")

    if islem == "Püskürtme":

        gerekli_ppe.append("Koruyucu Gozluk")

    if hazard_group in ["D", "E"]:

        gerekli_ppe.append("Yuz Siperi")

    if kontrol == "Control Approach 4":

        gerekli_ppe.append("Koruyucu Kiyafet")

    # =====================================================
    # PPE UYGUNLUK
    # =====================================================

    if "Respirator" in gerekli_ppe and not resp:

        eksik_ppe.append("Respirator")

    if "Kimyasal Eldiven" in gerekli_ppe and not eldiven:

        eksik_ppe.append("Kimyasal Eldiven")

    if "Koruyucu Gozluk" in gerekli_ppe and not gozluk:

        eksik_ppe.append("Koruyucu Gozluk")

    if "Yuz Siperi" in gerekli_ppe and not yuzsiperi:

        eksik_ppe.append("Yuz Siperi")

    if "Koruyucu Kiyafet" in gerekli_ppe and not koruyucu:

        eksik_ppe.append("Koruyucu Kiyafet")

    # =====================================================
    # CONTROL MEASURES
    # =====================================================

    kontrol_onlemleri = []

    if kontrol == "Control Approach 4":

        kontrol_onlemleri.append(
            "Containment sistemi kullanilmali"
        )

    if kontrol in [
        "Control Approach 3",
        "Control Approach 4"
    ]:

        kontrol_onlemleri.append(
            "LEV sistemi zorunlu"
        )

    if kapali_alan:

        kontrol_onlemleri.append(
            "Kapali alan proseduru uygulanmali"
        )

    if dar_alan:

        kontrol_onlemleri.append(
            "Gaz olcum sistemi gerekli"
        )

    if hazard_group in ["D", "E"]:

        kontrol_onlemleri.append(
            "Yetkili personel ile calisilmali"
        )

    if "gaz" in fiziksel_lower:

        kontrol_onlemleri.append(
            "Gaz detector sistemi onerilir"
        )

    if yetersiz_hijyen:

        kontrol_onlemleri.append(
            "Hijyen prosedurleri iyilestirilmeli"
        )

    # =====================================================
    # OEL / WEL
    # =====================================================

    oel_durumu = "Kontrol Gerekli"

    if sonuc == "DUSUK RISK":

        oel_durumu = "Muhtemel Uygun"

    elif sonuc == "YUKSEK RISK":

        oel_durumu = "OEL/WEL Asim Riski"

    # =====================================================
    # GHS PİKTOGRAMLARI
    # =====================================================

    ghs = []

    if "H350" in hkod or "H340" in hkod:
        ghs.append("GHS08 - Health Hazard")

    if "H314" in hkod:
        ghs.append("GHS05 - Corrosion")

    if "H315" in hkod or "H319" in hkod:
        ghs.append("GHS07 - Irritant")

    if "H330" in hkod:
        ghs.append("GHS06 - Toxic")

    # =====================================================
    # EKRAN
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

    st.subheader("OEL / WEL Durumu")
    st.write(oel_durumu)

    # =====================================================
    # GHS
    # =====================================================

    st.subheader("GHS Pictograms")
    for g in ghs:

    st.write("•", g)

    if "GHS05" in g:

        st.image(
            "ghs05.png",
            width=100
        )

    if "GHS06" in g:

        st.image(
            "ghs06.png",
            width=100
        )

    if "GHS07" in g:

        st.image(
            "ghs07.png",
            width=100
        )

    if "GHS08" in g:

        st.image(
            "ghs08.png",
            width=100
        )
    # =====================================================
    # PPE
    # =====================================================

    st.subheader("Gerekli PPE")

    for g in gerekli_ppe:

        st.write("•", g)

    st.subheader("PPE Uygunluk")

    if len(eksik_ppe) == 0:

        st.success("PPE UYGUN")

    else:

        st.error("PPE UYGUN DEGIL")

        for e in eksik_ppe:

            st.write("•", e)

    # =====================================================
    # CONTROL MEASURES
    # =====================================================

    st.subheader("Control Measures")

    for k in kontrol_onlemleri:

        st.write("•", k)

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
        "COSHH PROFESSIONAL REPORT",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    # =====================================================
    # RAPOR
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
        ("Hazard Group", hazard_group),
        ("Risk Result", sonuc),
        ("Control Approach", kontrol),
        ("OEL/WEL", oel_durumu)

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
    # GHS PDF
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "GHS Pictograms",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for g in ghs:

        pdf.cell(
            190,
            8,
            "- " + temizle(g),
            ln=True
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
        "Required PPE",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for g in gerekli_ppe:

        pdf.cell(
            190,
            8,
            "- " + temizle(g),
            ln=True
        )

    pdf.ln(5)

    # =====================================================
    # PPE STATUS PDF
    # =====================================================

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "PPE Status",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    if len(eksik_ppe) == 0:

        pdf.cell(
            190,
            8,
            "PPE UYGUN",
            ln=True
        )

    else:

        pdf.cell(
            190,
            8,
            "PPE UYGUN DEGIL",
            ln=True
        )

        for e in eksik_ppe:

            pdf.cell(
                190,
                8,
                "- " + temizle(e),
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
    # KAYDET
    # =====================================================

    filename = "COSHH_PRO_REPORT.pdf"

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
