import streamlit as st
import datetime
import io
try:
    from docxtpl import DocxTemplate
except ImportError:
    st.error("Lütfen requirements.txt dosyanıza 'docxtpl' ekleyin ve uygulamayı yeniden başlatın.")

# Google Sheets entegrasyonu (Opsiyonel)
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    pass

st.set_page_config(page_title="GKK Form Doldurucu", layout="wide")
st.title("Giriş Kalite Kontrol (GKK) Orijinal Form Doldurucu")
st.markdown("Verileri girin. Sistem orijinal **gkkform.docx** dosyanızı bozmadan sadece içindeki boşlukları ve tikleri dolduracaktır.")

bugun = datetime.datetime.now().strftime("%d.%m.%Y")

def verilere_kaydet(veri_listesi):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("GKK_Form_Deposu").sheet1
        sheet.append_row(veri_listesi)
        return True
    except Exception:
        return False

with st.form("gkk_form_alanlari"):
    st.subheader("1. Bilgiler")
    col1, col2 = st.columns(2)
    with col1:
        tarih = st.text_input("Tarih", value=bugun)
        siparis_no = st.text_input("Sipariş No")
    with col2:
        malzeme_no = st.text_input("Malzeme No")
        malzeme_aciklamasi = st.text_input("Malzeme Açıklaması")

    st.subheader("2. Kontroller")
    b1_col, b1_rad = st.columns([3, 2])
    belgeno1 = b1_col.text_input("Hammadde Kalite Belgesi No")
    b1_durum = b1_rad.radio("Hammadde Durumu", ["Uygun", "Uygun Değil", "N/A", "Boş Bırak"], index=3, horizontal=True)
    
    b2_col, b2_rad = st.columns([3, 2])
    belgeno2 = b2_col.text_input("Kaplama/Boya COC Belgesi No")
    b2_durum = b2_rad.radio("Kaplama/Boya Durumu", ["Uygun", "Uygun Değil", "N/A", "Boş Bırak"], index=3, horizontal=True)
    
    b3_col, b3_rad = st.columns([3, 2])
    belgeno3 = b3_col.text_input("Ölçü Kontrolü Belge No")
    b3_durum = b3_rad.radio("Ölçü Kontrol Durumu", ["Uygun", "Uygun Değil", "N/A", "Boş Bırak"], index=3, horizontal=True)

    b4_col, b4_rad = st.columns([3, 2])
    st.write("") # Hizalama boşluğu
    b4_durum = b4_rad.radio("Mastar Kontrolü Durumu", ["Uygun", "Uygun Değil", "N/A", "Boş Bırak"], index=3, horizontal=True)

    st.subheader("3. Miktarlar")
    m1, m2, m3, m4 = st.columns(4)
    kontrol_miktari = m1.text_input("Kontrol Miktarı")
    kabul_miktar = m2.text_input("Kabul Miktarı")
    red_iade_miktar = m3.text_input("Red/İade Miktarı")
    sartli_kabul_miktar = m4.text_input("Şartlı Kabul Miktarı")
    
    m5, m6 = st.columns(2)
    ayiklama_miktar = m5.text_input("Ayıklama Miktarı")
    proje_sorumlusu = m6.text_input("Şartlı Kabul İçin Onay Veren Proje Sorumlusu")

    st.subheader("4. Değerlendirme")
    aciklama_baslik = st.selectbox("Değerlendirme Başlığı", [
        "1. MALZEMELERİN SEVKİNE İZİN VERİLDİ",
        "2. MALZEMELERİN ŞARTLI KABUL İLE SEVKİNE İZİN VERİLDİ",
        "3. MALZEMELERİN SEVKİNE İZİN VERİLMEDİ."
    ])
    manuel_detay = st.text_area("Manuel Değerlendirme Notunuz (Varsa)")

    submit = st.form_submit_button("Formu Doldur ve İndir")

if submit:
    # Otomatik ClickUp uyarıları
    otomatik_notlar = []
    if not belgeno1.strip():
        otomatik_notlar.append("Hammadde CoC evrakları ilgili clickup listesinde görülememiştir.")
    if not belgeno2.strip():
        otomatik_notlar.append("Kaplama/Boya CoC evrakları ilgili clickup listesinde görülememiştir.")
    
    nihai_detay = manuel_detay.strip()
    if otomatik_notlar:
        ekler = "\n".join(otomatik_notlar)
        nihai_detay = f"{nihai_detay}\n\n{ekler}" if nihai_detay else ekler

    # Tik atma mantığı (☑ ve ☐)
    def t(secilen, hedef): return "☑" if secilen == hedef else "☐"

    # Veritabanına kaydet (Ayarlar yapılmışsa)
    yeni_satir = [
        tarih, siparis_no, malzeme_no, malzeme_aciklamasi, 
        belgeno1, b1_durum, belgeno2, b2_durum, belgeno3, b3_durum,
        kontrol_miktari, kabul_miktar, red_iade_miktar, sartli_kabul_miktar, 
        proje_sorumlusu, aciklama_baslik, nihai_detay.replace('\n', ' ')
    ]
    if "gcp_service_account" in st.secrets:
        if verilere_kaydet(yeni_satir):
            st.success("✅ Verileriniz başarıyla bulut deposuna kaydedildi!")

    # Word dosyasına gönderilecek veriler (Anahtarlar senin dosyadaki isimlerle birebir aynı)
    context = {
        "tarih": tarih,
        "siparis_no": siparis_no,
        "malzeme_no": malzeme_no,
        "malzeme_aciklaması": malzeme_aciklamasi,
        
        "belgeno1": belgeno1,
        "b1_u": t(b1_durum, "Uygun"),
        "b1_ud": t(b1_durum, "Uygun Değil"),
        "b1_na": t(b1_durum, "N/A"),
        
        "belgeno2": belgeno2,
        "b2_u": t(b2_durum, "Uygun"),
        "b2_ud": t(b2_durum, "Uygun Değil"),
        "b2_na": t(b2_durum, "N/A"),
        
        "belgeno3": belgeno3,
        "b3_u": t(b3_durum, "Uygun"),
        "b3_ud": t(b3_durum, "Uygun Değil"),
        "b3_na": t(b3_durum, "N/A"),
        
        "b4_u": t(b4_durum, "Uygun"),
        "b4_ud": t(b4_durum, "Uygun Değil"),
        "b4_na": t(b4_durum, "N/A"),
        
        "kontrol_miktari": kontrol_miktari,
        "kabul_miktar": kabul_miktar,
        "red_iade_miktar": red_iade_miktar,
        "ayıklama_miktar": ayiklama_miktar,
        "sartli_kabul_miktar": sartli_kabul_miktar,
        "proje_sorumlusu": proje_sorumlusu,
        
        "kabul_miktar_tarih": bugun if kabul_miktar else "",
        "red_iade_miktar_tarih": bugun if red_iade_miktar else "",
        "ayıklama_miktar_tarih": bugun if ayiklama_miktar else "",
        "sartli_kabul_miktar_tarih": bugun if sartli_kabul_miktar else "",
        "proje_sorumlusu_tarih": bugun if proje_sorumlusu else "",
        
        "kabultik": "☑" if kabul_miktar else "☐",
        "redtik": "☑" if red_iade_miktar else "☐",
        "ayiklanmatik": "☑" if ayiklama_miktar else "☐",
        "sartlitik": "☑" if sartli_kabul_miktar else "☐",
        
        "aciklama_ve_degerlendirme_basligi": aciklama_baslik,
        "aciklama_ve_degerlendirme_detay": nihai_detay
    }

    try:
        # Şablonu okuma ve doldurma (Dosya adını gkkform.docx olarak ayarladım)
        doc = DocxTemplate("gkkform.docx")
        doc.render(context)
        
        hafiza_dosyasi = io.BytesIO()
        doc.save(hafiza_dosyasi)
        hafiza_dosyasi.seek(0)
        
        st.success("Orijinal form bozulmadan başarıyla dolduruldu! Aşağıdan indirebilirsiniz.")
        st.download_button(
            label="📥 Doldurulmuş Orijinal Formu İndir (.docx)",
            data=hafiza_dosyasi,
            file_name=f"GKK_FORMU_{malzeme_no if malzeme_no else 'Doldurulmus'}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except FileNotFoundError:
        st.error("HATA: 'gkkform.docx' dosyası bulunamadı. Lütfen hazırladığınız Word şablonunu projeye ekleyin.")
