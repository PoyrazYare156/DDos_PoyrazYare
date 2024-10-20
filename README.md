# PoyrazYare DDoS Simülasyon Aracı

PoyrazYare, basit bir DDoS simülasyon aracı olup, UDP ve TCP protokolleri ile hedef IP adreslerine saldırı gerçekleştirmek için tasarlanmıştır. Bu araç, öğrenme ve test amaçlı olarak kullanılmalıdır. Herhangi bir yasa dışı etkinlikte kullanılmamalıdır.

## Özellikler

- UDP ve TCP protokolleri ile saldırı yapma
- Hedef IP adresi ve port belirleme
- Belirli bir süre boyunca saldırı yapma
- Saldırı hızını ayarlama
- Gönderilecek veri yükünü özelleştirme
- Başarı ve hata oranlarını raporlama
- Saldırı sonuçlarını dosyaya kaydetme

## Gereksinimler

Python 3.x ve aşağıdaki kütüphaneler:

- numpy
- requests

## Kurulum

1. **Gereksinimleri kontrol edin ve yükleyin:**
   ```bash
   python -m pip install numpy requests
