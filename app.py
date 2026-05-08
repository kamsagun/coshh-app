# =====================================================
# IMPORTS
# =====================================================

import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import random

# =====================================================
# TURKCE KARAKTER
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
# PAGE
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
# CHEMICAL
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
# H CODE CLEAN
# =====================================================

if "SDS gerekir" in hkod:

    hkod = ""

# =====================================================
# AUTO H-CODE DATABASE
# =====================================================

otomatik_h = {

    "AKRILONITRIL": "H350 H340 H330",
    "FORMALDEHIT": "H350 H341 H314",
    "BENZEN": "H350 H340",
    "TOLUEN": "H373",
    "KSILEN": "H373",
    "METANOL": "H301 H311 H331",
    "N,N-DIMETILASETAMID": "H373"

}

if hkod == "":

    kimyasal_buyuk = temizle(secili).upper()

    if kimyasal_buyuk in otomatik_h:

        hkod = otomatik_h[
            kimyasal_buyuk
        ]

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
        "Temizlik"
    ]
)

sure = st.slider(
    "Çalışma Süresi",
    1,
    12,
    1
)

miktar = st.number_input(
    "Kullanım Miktarı",
    min_value=0.0,
    value=1.0
)

maruziyet = st.selectbox(
    "Maruziyet",
    [
        "Düşük",
        "Orta",
        "Yüksek"
    ]
)

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
# INFO
# =====================================================

st.divider()

st.write("CAS:", cas)
st.write("H Kodları:", hkod)
st.write("Fiziksel Hal:", fiziksel)

# =====================================================
# BUTTON
# =====================================================

if st.button("COSHH Değerlendir"):

    # =====================================================
    # REPORT NUMBER
    # =====================================================

    rapor_no = (
        "COSHH-" +
        str(datetime.now().year) +
        "-" +
        str(random.randint(10000,99999))
    )

    # =====================================================
    # RISK
    # =====================================================

    risk = 0

    if "H350" in hkod:
        risk += 6

    if "H340" in hkod:
        risk += 5

    if "H330" in hkod:
        risk += 5

    if "H314" in hkod:
        risk += 4

    if "H373" in hkod:
        risk += 3

    if islem == "Püskürtme":
        risk += 4

    if sure >= 8:
        risk += 3

    if miktar >= 100:
        risk += 3

    if maruziyet == "Yüksek":
        risk += 4

    if not resp:
        risk += 2

    # =====================================================
    # RESULT
    # =====================================================

    if risk <= 10:

        sonuc = "DUSUK RISK"

    elif risk <= 20:

        sonuc = "ORTA RISK"

    else:

        sonuc = "YUKSEK RISK"

    # =====================================================
    # PRIORITY
    # =====================================================

    if risk >= 25:

        priority = "P1 - Critical"

    elif risk >= 15:

        priority = "P2 - High"

    elif risk >= 8:

        priority = "P3 - Medium"

    else:

        priority = "P4 - Low"

    # =====================================================
    # REPORT STATUS
    # =====================================================

    if sonuc == "DUSUK RISK":

        rapor_durumu = "ACCEPTABLE"

    elif sonuc == "ORTA RISK":

        rapor_durumu = "REVIEW REQUIRED"

    else:

        rapor_durumu = "IMMEDIATE ACTION REQUIRED"

    # =====================================================
    # HAZARD GROUP
    # =====================================================

    hazard_group = "A"

    if (
        "H350" in hkod or
        "H340" in hkod
    ):

        hazard_group = "E"

    elif "H330" in hkod:

        hazard_group = "D"

    elif "H314" in hkod:

        hazard_group = "C"

    elif "H373" in hkod:

        hazard_group = "B"

    # =====================================================
    # CONTROL APPROACH
    # =====================================================

    if hazard_group == "E":

        kontrol = "Control Approach 4"

    elif hazard_group == "D":

        kontrol = "Control Approach 3"

    elif hazard_group == "C":

        kontrol = "Control Approach 2"

    else:

        kontrol = "Control Approach 1"

    # =====================================================
    # GHS
    # =====================================================

    ghs = []

    if "H314" in hkod:

        ghs.append("GHS05")

    if (
        "H315" in hkod or
        "H319" in hkod
    ):

        ghs.append("GHS07")

    if "H330" in hkod:

        ghs.append("GHS06")

    if (
        "H340" in hkod or
        "H350" in hkod or
        "H373" in hkod
    ):

        ghs.append("GHS08")

    # =====================================================
    # PPE VALIDATION
    # =====================================================

    ppe_uyari = []

    if "H314" in hkod:

        if not gozluk:

            ppe_uyari.append(
                "H314 icin koruyucu gozluk gerekli"
            )

        if not yuzsiperi:

            ppe_uyari.append(
                "H314 icin yuz siperi gerekli"
            )

    if "H330" in hkod:

        if not resp:

            ppe_uyari.append(
                "H330 icin respirator gerekli"
            )

    # =====================================================
    # ACTION PLAN
    # =====================================================

    aksiyon_plani = []

    if priority == "P1 - Critical":

        aksiyon_plani.append(
            "Calisma derhal durdurulmali"
        )

        aksiyon_plani.append(
            "Yonetim bilgilendirilmeli"
        )

    if priority == "P2 - High":

        aksiyon_plani.append(
            "Kontrol onlemleri hizla iyilestirilmeli"
        )

    if not resp:

        aksiyon_plani.append(
            "Respirator temin edilmeli"
        )

    if not eldiven:

        aksiyon_plani.append(
            "Kimyasal eldiven saglanmali"
        )

    if islem == "Püskürtme":

        aksiyon_plani.append(
            "LEV sistemi kurulumu degerlendirilmeli"
        )

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    oneriler = []

    if sonuc == "YUKSEK RISK":

        oneriler.append(
            "Kapali sistem dusunulmeli"
        )

    if islem == "Püskürtme":

        oneriler.append(
            "LEV sistemi onerilir"
        )

    if not resp:

        oneriler.append(
            "Respirator onerilir"
        )

    if not eldiven:

        oneriler.append(
            "Kimyasal eldiven onerilir"
        )

    # =====================================================
    # EXPOSURE ROUTES
    # =====================================================

    maruziyet_yollari = []

    if (
        "H330" in hkod or
        "gaz" in fiziksel.lower() or
        "buhar" in fiziksel.lower()
    ):

        maruziyet_yollari.append(
            "Inhalasyon Riski"
        )

    if (
        "H314" in hkod or
        "H315" in hkod
    ):

        maruziyet_yollari.append(
            "Deri Temasi Riski"
        )

    if (
        "H318" in hkod or
        "H319" in hkod or
        "H314" in hkod
    ):

        maruziyet_yollari.append(
            "Goz Temasi Riski"
        )

    # =====================================================
    # FIRST AID
    # =====================================================

    ilk_yardim = []

    if "Inhalasyon Riski" in maruziyet_yollari:

        ilk_yardim.append(
            "Kisiyi temiz havaya cikar"
        )

    if "Deri Temasi Riski" in maruziyet_yollari:

        ilk_yardim.append(
            "Bol su ile yika"
        )

    if "Goz Temasi Riski" in maruziyet_yollari:

        ilk_yardim.append(
            "Gozleri 15 dakika yika"
        )

    # =====================================================
    # RESULT SCREEN
    # =====================================================

    st.subheader("Rapor No")
    st.code(rapor_no)

    st.subheader("Risk Score")

    st.metric(
        "Total Risk Score",
        risk
    )

    st.progress(
        min(risk / 30, 1.0)
    )

    if sonuc == "DUSUK RISK":

        st.success(sonuc)

    elif sonuc == "ORTA RISK":

        st.warning(sonuc)

    else:

        st.error(sonuc)

    # =====================================================
    # PRIORITY SCREEN
    # =====================================================

    st.subheader("Priority Level")

    if priority == "P1 - Critical":

        st.error(priority)

    elif priority == "P2 - High":

        st.warning(priority)

    elif priority == "P3 - Medium":

        st.info(priority)

    else:

        st.success(priority)

    # =====================================================
    # REPORT STATUS
    # =====================================================

    st.subheader("Report Status")

    if rapor_durumu == "ACCEPTABLE":

        st.success(rapor_durumu)

    elif rapor_durumu == "REVIEW REQUIRED":

        st.warning(rapor_durumu)

    else:

        st.error(rapor_durumu)

    st.subheader("Hazard Group")
    st.write(hazard_group)

    st.subheader("Control Approach")
    st.write(kontrol)

    # =====================================================
    # PPE WARNINGS
    # =====================================================

    if len(ppe_uyari) > 0:

        st.subheader("PPE Uyarıları")

        for u in ppe_uyari:

            st.error(u)

    # =====================================================
    # ACTION PLAN SCREEN
    # =====================================================

    st.subheader("Aksiyon Planı")

    for a in aksiyon_plani:

        st.warning(a)

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    st.subheader("Öneriler")

    for o in oneriler:

        st.write("•", o)

    # =====================================================
    # EXPOSURE ROUTES
    # =====================================================

    st.subheader("Maruziyet Yolları")

    for m in maruziyet_yollari:

        st.info(m)

    # =====================================================
    # FIRST AID
    # =====================================================

    st.subheader("İlk Yardım")

    for i in ilk_yardim:

        st.success(i)

    # =====================================================
    # GHS PICTOGRAMS
    # =====================================================

    st.subheader("GHS Pictograms")

    cols = st.columns(4)

    for i, g in enumerate(ghs):

        if g == "GHS05":

            with cols[i % 4]:

                st.image(
                    "ghs05.png",
                    width=120
                )

                st.caption("Corrosive")

        elif g == "GHS06":

            with cols[i % 4]:

                st.image(
                    "ghs06.png",
                    width=120
                )

                st.caption("Toxic")

        elif g == "GHS07":

            with cols[i % 4]:

                st.image(
                    "ghs07.png",
                    width=120
                )

                st.caption("Irritant")

        elif g == "GHS08":

            with cols[i % 4]:

                st.image(
                    "ghs08.png",
                    width=120
                )

                st.caption("Health Hazard")

    # =====================================================
    # PDF
    # =====================================================

    pdf = FPDF()

    pdf.add_page()

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    pdf.set_font(
        "Helvetica",
        "B",
        18
    )

    pdf.cell(
        190,
        12,
        "COSHH PROFESSIONAL REPORT",
        ln=True,
        align="C"
    )

    pdf.ln(10)

    bilgiler = [

        ("Report No", rapor_no),
        ("Chemical", temizle(secili)),
        ("CAS No", temizle(cas)),
        ("H Codes", temizle(hkod)),
        ("Physical State", temizle(fiziksel)),
        ("Process", temizle(islem)),
        ("Duration", f"{sure} hours"),
        ("Amount", str(miktar)),
        ("Exposure", temizle(maruziyet)),
        ("Hazard Group", hazard_group),
        ("Risk Result", sonuc),
        ("Report Status", rapor_durumu),
        ("Risk Score", risk),
        ("Priority Level", priority),
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

    # =====================================================
    # PDF ACTION PLAN
    # =====================================================

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        "B",
        14
    )

    pdf.cell(
        190,
        10,
        "Action Plan",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        11
    )

    for a in aksiyon_plani:

        pdf.multi_cell(
            180,
            8,
            f"- {temizle(a)}"
        )

    # =====================================================
    # PDF RECOMMENDATIONS
    # =====================================================

    pdf.ln(5)

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

        pdf.multi_cell(
            180,
            8,
            f"- {temizle(o)}"
        )

    # =====================================================
    # PDF GHS
    # =====================================================

    pdf.ln(5)

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

        if g == "GHS05":

            pdf.cell(
                190,
                8,
                "GHS05 - Corrosive",
                ln=True
            )

        elif g == "GHS06":

            pdf.cell(
                190,
                8,
                "GHS06 - Toxic",
                ln=True
            )

        elif g == "GHS07":

            pdf.cell(
                190,
                8,
                "GHS07 - Irritant",
                ln=True
            )

        elif g == "GHS08":

            pdf.cell(
                190,
                8,
                "GHS08 - Health Hazard",
                ln=True
            )

    # =====================================================
    # DATE
    # =====================================================

    pdf.ln(5)

    pdf.set_font(
        "Helvetica",
        "B",
        12
    )

    pdf.cell(
        190,
        10,
        "Generated:",
        ln=True
    )

    pdf.set_font(
        "Helvetica",
        "",
        10
    )

    pdf.cell(
        190,
        8,
        str(datetime.now()),
        ln=True
    )

    # =====================================================
    # SAVE PDF
    # =====================================================

    filename = "COSHH_PRO_REPORT.pdf"

    pdf.output(filename)

    with open(filename, "rb") as f:

        st.download_button(
            "PDF Indir",
            f,
            file_name=filename
        )
