import streamlit as st
import datetime

st.set_page_config(page_title="Giriş Kalite Kontrol Formu", layout="wide")
st.title("Giriş Kalite Kontrol (GKK) Formu Oluşturucu")
st.markdown("Belge numaralarını, miktarları ve açıklamaları girerek otomatik GKK formunuzu oluşturun. İşlemi bitirdiğinizde en alttaki kodu kopyalayabilirsiniz.")

# Güncel tarih ön tanımlı olarak gelsin
bugun = datetime.datetime.now().strftime("%d.%m.%Y")

with st.form("gkk_formu"):
    st.subheader("1. Genel Bilgiler")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        tarih = st.text_input("Tarih", value=bugun)
    with col2:
        siparis_no = st.text_input("Sipariş No")
    with col3:
        malzeme_no = st.text_input("Malzeme No")
    with col4:
        malzeme_aciklamasi = st.text_input("Malzeme Açıklaması")

    st.subheader("2. Belge ve Ölçüm Kontrolleri")
    st.info("İlgili belge numarasını girdiğinizde Durumunu seçiniz. Belge no boş bırakılırsa otomatik olarak açıklama kısmına not düşülecektir.")
    
    col_b1, col_b2, col_b3 = st.columns(3)
    with col_b1:
        st.markdown("**Hammadde Kalite Belgesi**")
        belgeno1 = st.text_input("Belge No (Hammadde)")
        b1_durum = st.radio("Durum", ["Uygun", "Uygun Değil", "N/A"], key="b1")
    with col_b2:
        st.markdown("**Kaplama/Boya COC Belgesi**")
        belgeno2 = st.text_input("Belge No (Kaplama/Boya)")
        b2_durum = st.radio("Durum", ["Uygun", "Uygun Değil", "N/A"], key="b2")
    with col_b3:
        st.markdown("**Ölçü Kontrolü**")
        belgeno3 = st.text_input("Belge No (Ölçü Kontrol)")
        b3_durum = st.radio("Durum", ["Uygun", "Uygun Değil", "N/A"], key="b3")

    st.subheader("3. Sonuç, Karar ve Miktarlar")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        kontrol_miktari = st.text_input("Kontrol Miktarı")
        kabul_miktar = st.text_input("Kabul Miktarı")
        kabul_miktar_tarih = st.text_input("Kabul Tarih", value=bugun if kabul_miktar else "")
    with col_m2:
        red_iade_miktar = st.text_input("Red/İade Miktarı")
        red_iade_miktar_tarih = st.text_input("Red/İade Tarih", value=bugun if red_iade_miktar else "")
        ayiklama_miktar = st.text_input("Ayıklama Miktarı")
        ayiklama_miktar_tarih = st.text_input("Ayıklama Tarih", value=bugun if ayiklama_miktar else "")
    with col_m3:
        sartli_kabul_miktar = st.text_input("Şartlı Kabul Miktarı")
        sartli_kabul_miktar_tarih = st.text_input("Şartlı Kabul Tarih", value=bugun if sartli_kabul_miktar else "")
        proje_sorumlusu = st.text_input("Proje Sorumlusu")
        proje_sorumlusu_tarih = st.text_input("Proje Sor. Tarih", value=bugun if proje_sorumlusu else "")

    st.subheader("4. Değerlendirme ve Açıklamalar")
    baslik_secenekleri = [
        "1. MALZEMELERİN SEVKİNE İZİN VERİLDİ",
        "2. MALZEMELERİN ŞARTLI KABUL İLE SEVKİNE İZİN VERİLDİ",
        "3. MALZEMELERİN SEVKİNE İZİN VERİLMEDİ."
    ]
    aciklama_baslik = st.selectbox("Değerlendirme Başlığı Seçiniz", baslik_secenekleri)
    aciklama_detay_manuel = st.text_area("Manuel Açıklama / Değerlendirme Detayı (Gerekliyse)")

    submit_button = st.form_submit_button(label="Formu Oluştur")

if submit_button:
    # --- Otomatik Eksik Belge Cümleleri Mantığı ---
    otomatik_notlar = []
    if not belgeno1.strip():
        otomatik_notlar.append("Hammadde CoC evrakları ilgili clickup listesinde görülememiştir.")
    if not belgeno2.strip():
        otomatik_notlar.append("Kaplama/Boya CoC evrakları ilgili clickup listesinde görülememiştir.")
    
    # Manuel girilen metnin altına otomatik notları ekleme
    nihai_aciklama_detay = aciklama_detay_manuel.strip()
    if otomatik_notlar:
        eklenen_cumleler = "\n".join(otomatik_notlar)
        if nihai_aciklama_detay:
            nihai_aciklama_detay += f"\n\n{eklenen_cumleler}"
        else:
            nihai_aciklama_detay = eklenen_cumleler

    # --- Tik İşaretlerini Ayarlama Fonksiyonu ---
    def tik_getir(mevcut_durum, hedef_durum):
        return "☑" if mevcut_durum == hedef_durum else "☐"

    # --- Form Şablonu (Orijinal Format Birebir Korunmuştur) ---
    # Python formatlaması için süslü parantezler kullanılmıştır.
    sablon = f"""![Teknolus Logo](https://upload.wikimedia.org/wikipedia/commons/a/a2/Teknolus_Logo.jpg)
 | Giriş Kalite Kontrol Ürün Değerlendirme Formu
 | Doküman No
 | QLT-F25

 |  | Revizyon Tarihi
 | 15.01.2026

 |  | Revizyon No
 | 0

 |  | Hazırlayan
 | KYS

 |  | Onaylayan
 | KYT

Envanter Belge No / Kalem No
<td colspan=4/> | -
<td colspan=4/> | Tarih
<td colspan=3/> | {tarih}
<td colspan=3/>
Malzeme No 
<td colspan=4/> | {malzeme_no}
<td colspan=4/> | Malzeme Açıklaması
<td colspan=3/> | {malzeme_aciklamasi}
<td colspan=3/>
Sipariş No
<td colspan=4/> | {siparis_no}
<td colspan=4/> | Kontrol Eden GKK Sorumlusu
<td colspan=3/> | ÖTÜKEN AVCI
<td colspan=3/>
KONTROL VE İNCELEMELER
<td colspan=14/>
KONTROL TİPİ
 | KONTROLLER
<td colspan=6/> | Belge No
 | Uygun
<td colspan=2/> | Uygun Değil
<td colspan=3/> | N/A

BELGE
KONT.
 | Ürün Uygunluk Belgesi
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

 | Hammalzeme Kalite Belgesi
<td colspan=6/> | {belgeno1}
 | {tik_getir(b1_durum, "Uygun")}
<td colspan=2/> | {tik_getir(b1_durum, "Uygun Değil")}
<td colspan=3/> | {tik_getir(b1_durum, "N/A")}

 | Kaplama/Boya COC Belgesi
<td colspan=6/> | {belgeno2}
 | {tik_getir(b2_durum, "Uygun")}
<td colspan=2/> | {tik_getir(b2_durum, "Uygun Değil")}
<td colspan=3/> | {tik_getir(b2_durum, "N/A")}

 | Isıl işlem / Kaynak işlemleri COC Belgesi
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

 | İrsaliye/teslim belgesi  
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

GÖZ KONT.
 | Parti miktarı  doğruluğu
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

 | Ürün paketlemesi
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

 | Malzeme göz kontrolü
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

ÖLÇÜ KONT.
 | Ölçü Kontrolü
<td colspan=6/> | {belgeno3}
 | {tik_getir(b3_durum, "Uygun")}
<td colspan=2/> | {tik_getir(b3_durum, "Uygun Değil")}
<td colspan=3/> | {tik_getir(b3_durum, "N/A")}

 | Mastar Kontrolü
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

FONKS. KONT.
 | Ürünün çalışma durumu kontrolünü
<td colspan=6/> |  | ☐
<td colspan=2/> | ☐
<td colspan=3/> | ☐

KONTROL ARACI ADI (DEMİRBAŞ ADI)
<td colspan=5/> | KONTROL ARACI TİPİ                       (Ölçü Aleti/Mastar/Montaj Parçası)
<td colspan=3/> | KONTROL ARACI NO
(Parça No/Seri No/Demirbaş No)
<td colspan=4/> | ÖLÇÜM BELGE NO
<td colspan=2/>
<td colspan=5/> | <td colspan=3/> | <td colspan=4/> | <td colspan=2/>
<td colspan=5/> | <td colspan=3/> | <td colspan=4/> | <td colspan=2/>
<td colspan=5/> | <td colspan=3/> | <td colspan=4/> | <td colspan=2/>
<td colspan=5/> | <td colspan=3/> | <td colspan=4/> | <td colspan=2/>
<td colspan=5/> | <td colspan=3/> | <td colspan=4/> | <td colspan=2/>
SONUÇ
<td colspan=14/>
KONTROL MİKTARI
<td colspan=3/> | {kontrol_miktari}
<td colspan=11/>
KARAR
<td colspan=3/> | ☐ KABUL
<td colspan=3/> | ☐ RED/İADE
<td colspan=2/> | ☐AYIKLAMA
 | ☐ ŞARTLI KABUL
<td colspan=3/> | PROJE SORUMLUSU      (Şartlı Kabul İçin Onay Veren Yetkili)
<td colspan=2/>
MİKTAR
<td colspan=3/> | {kabul_miktar}
<td colspan=3/> | {red_iade_miktar}
<td colspan=2/> | {ayiklama_miktar}
 | {sartli_kabul_miktar}
<td colspan=3/> | {proje_sorumlusu}
<td colspan=2/>
TARİH
<td colspan=3/> | {kabul_miktar_tarih}
<td colspan=3/> | {red_iade_miktar_tarih}
<td colspan=2/> | {ayiklama_miktar_tarih}
 | {sartli_kabul_miktar_tarih}
<td colspan=3/> | {proje_sorumlusu_tarih}
<td colspan=2/>
RED/AYIKLAMA NEDENİ
<td colspan=3/> | ☐ Tedarikçi                   ☐Satın Alma                                ☐ Tasarım                          ☐ Planlama
<td colspan=11/>
DEĞERLENDİRME ve AÇIKLAMALAR
<td colspan=14/>
{aciklama_baslik}
{nihai_aciklama_detay}
<td colspan=14/>
GKK SORUMLUSU  ONAYI
AD SOYAD İMZA TARİH
<td colspan=2/> | ÖTÜKEN AVCI
<td colspan=12/>"""

    st.success("Form başarıyla oluşturuldu! Aşağıdaki kutunun sağ üst köşesindeki kopyalama butonuna tıklayarak kodu alabilirsiniz.")
    st.code(sablon, language="markdown")
