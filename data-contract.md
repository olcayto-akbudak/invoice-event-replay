# Girdi ve çıktı sözleşmesi

UTF-8 JSON nesnesi; örnek dosya alanların tam iç içe yapısını gösterir. Zamanlar bu laboratuvarda sayısal sanal zaman/gün değeridir; saat dilimi dönüşümü yapılmaz.

| Üst alan | Tür | Örnek |
|---|---|---|
| `events` | `list` | [{'id': 'E1', 'entity': 'I1', 'kind': 'SEND'}, {'id': 'E2', 'entity': 'I1', 'kind': 'TIMEOUT'}, {'id': 'E3', 'entity': 'I1', 'kind': 'RECONCILE'}] |

## Semantik

Zincir anahtarı ve güvenilir checkpoint veritabanından bağımsız korunmalıdır.

Alan motorunun doğrulamaları `app.py` içinde açıkça bulunur. Eksik zorunlu anahtarlar hata verir. Satır bazında karantina/bulgu üreten motorlar rapora yazar; yapısal konfigürasyon hataları işlemi keser. Tam JSON Schema dosyası bu sürümün kapsamında değildir.

## Çıktı

Gerçek çıktı şeması ve örnek değerler `sample-report.json` içinde yer alır. Örnek işleme özgü sonuçlar `results.md` içinde açıklanır. Dış tüketici alan adlarını ve birimleri değiştirmeden sözleşmeyi sürümlemelidir.
