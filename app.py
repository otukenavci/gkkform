import streamlit as st
import datetime

# Google Sheets entegrasyonu
try:
    import gspread
    from google.oauth2.service_account import Credentials
except ImportError:
    st.warning("Depolama için 'gspread' ve 'google-auth' kütüphaneleri yüklü olmalıdır.")

st.set_page_config(page_title="GKK Formu Üretici ve Depocu", layout="wide")
st.title("Giriş Kalite Kontrol (GKK) Form Sihirbazı & Dijital Arşiv")
st.markdown("Verileri doldurun; sistem hem **Word (.doc)** belgesini indirecek hem de **bulut veritabanına** kaydedecektir.")

bugun = datetime.datetime.now().strftime("%d.%m.%Y")

# --- Google Sheets Kayıt Fonksiyonu ---
def verilere_kaydet(veri_listesi):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        sheet = client.open("GKK_Form_Deposu").sheet1
        sheet.append_row(veri_listesi)
        return True
    except Exception as e:
        st.error(f"Depolama bağlantı hatası (Secrets ayarlarınızı kontrol edin): {e}")
        return False

# --- Arayüz Giriş Alanları ---
with st.form("gkk_form_alanlari"):
    st.subheader("📋 Ürün ve Sipariş Bilgileri")
    col1, col2 = st.columns(2)
    with col1:
        tarih = st.text_input("Tarih", value=bugun)
        siparis_no = st.text_input("Sipariş No")
    with col2:
        malzeme_no = st.text_input("Malzeme No")
        malzeme_aciklamasi = st.text_input("Malzeme Açıklaması")

    st.subheader("🔍 Kontroller ve Uygunluk Durumları")
    
    b1_col, b1_rad = st.columns([3, 2])
    belgeno1 = b1_col.text_input("Hammadde Kalite Belgesi No")
    b1_durum = b1_rad.radio("Hammadde Durumu", ["Uygun", "Uygun Değil", "N/A"], horizontal=True, key="h1")
    
    b2_col, b2_rad = st.columns([3, 2])
    belgeno2 = b2_col.text_input("Kaplama/Boya COC Belgesi No")
    b2_durum = b2_rad.radio("Kaplama/Boya Durumu", ["Uygun", "Uygun Değil", "N/A"], horizontal=True, key="k1")
    
    b3_col, b3_rad = st.columns([3, 2])
    belgeno3 = b3_col.text_input("Ölçü Kontrolü Belge No")
    b3_durum = b3_rad.radio("Ölçü Kontrol Durumu", ["Uygun", "Uygun Değil", "N/A"], horizontal=True, key="o1")

    st.subheader("📊 Miktarlar ve Karar")
    m1, m2, m3, m4 = st.columns(4)
    kontrol_miktari = m1.text_input("Kontrol Miktarı")
    kabul_miktar = m2.text_input("Kabul Miktarı")
    red_iade_miktar = m3.text_input("Red/İade Miktarı")
    sartli_kabul_miktar = m4.text_input("Şartlı Kabul Miktarı")
    
    m5, m6 = st.columns(2)
    ayiklama_miktar = m5.text_input("Ayıklama Miktarı")
    proje_sorumlusu = m6.text_input("Şartlı Kabul İçin Onay Veren Proje Sorumlusu")

    st.subheader("📝 Değerlendirme")
    aciklama_baslik = st.selectbox("Değerlendirme Başlığı", [
        "1. MALZEMELERİN SEVKİNE İZİN VERİLDİ",
        "2. MALZEMELERİN ŞARTLI KABUL İLE SEVKİNE İZİN VERİLDİ",
        "3. MALZEMELERİN SEVKİNE İZİN VERİLMEDİ."
    ])
    manuel_detay = st.text_area("Manuel Değerlendirme Notunuz (Varsa)")

    submit = st.form_submit_button("Form Belgesini Hazırla ve Depola")

if submit:
    # Tarih atamaları
    k_tarih = bugun if kabul_miktar else ""
    r_tarih = bugun if red_iade_miktar else ""
    a_tarih = bugun if ayiklama_miktar else ""
    s_tarih = bugun if sartli_kabul_miktar else ""
    p_tarih = bugun if proje_sorumlusu else ""

    # Otomatik ClickUp Uyarı Mantığı
    otomatik_notlar = []
    if not belgeno1.strip():
        otomatik_notlar.append("Hammadde CoC evrakları ilgili clickup listesinde görülememiştir.")
    if not belgeno2.strip():
        otomatik_notlar.append("Kaplama/Boya CoC evrakları ilgili clickup listesinde görülememiştir.")
    
    aciklama_detay = manuel_detay.strip()
    if otomatik_notlar:
        ekler = "<br>".join(otomatik_notlar)
        if aciklama_detay:
            aciklama_detay += f"<br><br>{ekler}"
        else:
            aciklama_detay = ekler

    kabul_box = "☑" if kabul_miktar else "☐"
    red_box = "☑" if red_iade_miktar else "☐"
    ayiklama_box = "☑" if ayiklama_miktar else "☐"
    sartli_box = "☑" if sartli_kabul_miktar else "☐"

    def t(current, target): return "☑" if current == target else "☐"

    # --- Buluta Kaydedilecek Satır Verisi ---
    yeni_satir = [
        tarih, siparis_no, malzeme_no, malzeme_aciklamasi, 
        belgeno1, b1_durum, belgeno2, b2_durum, belgeno3, b3_durum,
        kontrol_miktari, kabul_miktar, red_iade_miktar, sartli_kabul_miktar, 
        proje_sorumlusu, aciklama_baslik, aciklama_detay.replace('<br>', ' ')
    ]
    
    # Veritabanına Yazma İşlemi (Hata vermemesi için sessiz geçebilir veya uyarabilir)
    if "gcp_service_account" in st.secrets:
        basarili_mi = verilere_kaydet(yeni_satir)
        if basarili_mi:
            st.success("✅ Verileriniz başarıyla bulut deposuna (Google Sheets) kaydedildi!")
    else:
        st.info("ℹ️ Form oluşturuldu ancak Google Sheets bağlantı ayarları (Secrets) henüz yapılmadığı için veritabanına kaydedilmedi.")

    # --- Orijinal Word HTML Alanı ---
    word_html = f"""
    <html xmlns:o='urn:schemas-microsoft-com:office:office' xmlns:w='urn:schemas-microsoft-com:office:word' xmlns='http://www.w3.org/TR/REC-html40'>
    <head><meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 5px; }}
        td {{ border: 1px solid #000000; padding: 5px; vertical-align: top; }}
        .header-title {{ font-weight: bold; text-align: center; font-size: 11pt; vertical-align: middle; }}
        .bg-gray {{ background-color: #F2F2F2; font-weight: bold; text-align: center; }}
        .center {{ text-align: center; }}
    </style></head>
    <body>
    <table>
        <tr>
            <td rowspan="5" style="width: 25%; text-align: center; vertical-align: middle;"><img src="https://www.teknolus.com/images/logo.png" width="130"><br><span style="font-size: 8pt;">http://www.teknolus.com</span></td>
            <td rowspan="5" class="header-title" style="width: 45%;">Giriş Kalite Kontrol Ürün Değerlendirme Formu</td>
            <td style="width: 15%; font-weight: bold;">Doküman No</td><td style="width: 15%;">QLT-F25</td>
        </tr>
        <tr><td style="font-weight: bold;">Revizyon Tarihi</td><td>15.01.2026</td></tr>
        <tr><td style="font-weight: bold;">Revizyon No</td><td>0</td></tr>
        <tr><td style="font-weight: bold;">Hazırlayan</td><td>KYS</td></tr>
        <tr><td style="font-weight: bold;">Onaylayan</td><td>KYT</td></tr>
    </table>
    <table>
        <tr><td style="font-weight: bold; width: 25%;">Envanter Belge No / Kalem No</td><td style="width: 25%;">-</td><td style="font-weight: bold; width: 25%;">Tarih</td><td style="width: 25%;">{tarih}</td></tr>
        <tr><td style="font-weight: bold;">Malzeme No</td><td>{malzeme_no}</td><td style="font-weight: bold;">Malzeme Açıklaması</td><td>{malzeme_aciklamasi}</td></tr>
        <tr><td style="font-weight: bold;">Sipariş No</td><td>{siparis_no}</td><td style="font-weight: bold;">Kontrol Eden GKK Sorumlusu</td><td>ÖTÜKEN AVCI</td></tr>
    </table>
    <table>
        <tr><td colspan="7" class="bg-gray">KONTROL VE İNCELEMELER</td></tr>
        <tr style="font-weight: bold; background-color: #E6E6E6;">
            <td style="width: 12%;">KONTROL TİPİ</td><td style="width: 12%;">KONTROLLER</td><td style="width: 36%;">Belge No</td><td class="center">Uygun</td><td class="center">Uygun Değil</td><td colspan="2" class="center">N/A</td>
        </tr>
        <tr><td>BELGE KONT.</td><td>Ürün Uygunluk Belgesi</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2"></td><td>Hammalzeme Kalite Belgesi</td><td>{belgeno1}</td><td class="center">{t(b1_durum, 'Uygun')}</td><td class="center">{t(b1_durum, 'Uygun Değil')}</td><td colspan="2" class="center">{t(b1_durum, 'N/A')}</td></tr>
        <tr><td colspan="2"></td><td>Kaplama/Boya COC Belgesi</td><td>{belgeno2}</td><td class="center">{t(b2_durum, 'Uygun')}</td><td class="center">{t(b2_durum, 'Uygun Değil')}</td><td colspan="2" class="center">{t(b2_durum, 'N/A')}</td></tr>
        <tr><td colspan="2"></td><td>Isıl işlem / Kaynak işlemleri COC Belgesi</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2"></td><td>İrsaliye/teslim belgesi</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2">GÖZ KONT.</td><td>Parti miktarı doğruluğu</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2"></td><td>Ürün paketlemesi</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2"></td><td>Malzeme göz kontrolü</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2">ÖLÇÜ KONT.</td><td>Ölçü Kontrolü</td><td>{belgeno3}</td><td class="center">{t(b3_durum, 'Uygun')}</td><td class="center">{t(b3_durum, 'Uygun Değil')}</td><td colspan="2" class="center">{t(b3_durum, 'N/A')}</td></tr>
        <tr><td colspan="2"></td><td>Mastar Kontrolü</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
        <tr><td colspan="2">FONKS. KONT.</td><td>Ürünün çalışma durumu kontrolünü</td><td></td><td></td><td class="center">☐</td><td class="center">☐</td><td colspan="2" class="center">☐</td></tr>
    </table>
    <table>
        <tr style="font-weight: bold; background-color: #E6E6E6; font-size: 8.5pt;">
            <td style="width: 25%;">KONTROL ARACI ADI</td><td style="width: 35%;">KONTROL ARACI TİPİ</td><td style="width: 20%;">KONTROL ARACI NO</td><td style="width: 20%;">ÖLÇÜM BELGE NO</td>
        </tr>
        <tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr><tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
    </table>
    <table>
        <tr><td colspan="6" class="bg-gray">SONUÇ</td></tr>
        <tr><td style="font-weight: bold; width: 20%;">KONTROL MİKTARI</td><td colspan="5">{kontrol_miktari}</td></tr>
        <tr style="font-weight: bold;"><td>KARAR</td><td>{kabul_box} KABUL</td><td>{red_box} RED/İADE</td><td>{ayiklama_box} AYIKLAMA</td><td>{sartli_box} ŞARTLI KABUL</td><td style="font-size:8pt;">PROJE SORUMLUSU</td></tr>
        <tr><td style="font-weight: bold;">MİKTAR</td><td>{kabul_miktar}</td><td>{red_iade_miktar}</td><td>{ayiklama_miktar}</td><td>{sartli_kabul_miktar}</td><td>{proje_sorumlusu}</td></tr>
        <tr><td style="font-weight: bold;">TARİH</td><td>{k_tarih}</td><td>{r_tarih}</td><td>{a_tarih}</td><td>{s_tarih}</td><td>{p_tarih}</td></tr>
    </table>
    <table>
        <tr><td class="bg-gray" style="text-align: left;">DEĞERLENDİRME ve AÇIKLAMALAR</td></tr>
        <tr><td style="height: 120px; padding: 8px; vertical-align: top;"><b>{aciklama_baslik}</b><br><br>{aciklama_detay}</td></tr>
    </table>
    <table>
        <tr><td style="width: 25%; font-weight: bold;">GKK SORUMLUSU ONAYI</td><td style="width: 25%;">AD SOYAD İMZA TARİH</td><td style="width: 50%; font-weight: bold;">ÖTÜKEN AVCI</td></tr>
    </table>
    </body></html>
    """

    st.download_button(
        label="📥 Hazırlanan GKK Formunu Word Olarak İndir (.doc)",
        data=word_html,
        file_name=f"GKK_FORMU_{malzeme_no if malzeme_no else 'Belge'}.doc",
        mime="application/msword"
    )
