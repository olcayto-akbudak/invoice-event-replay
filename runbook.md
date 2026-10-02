# İşletim ve hata inceleme

1. `python --version` ile 3.12 veya daha yeni sürümü doğrulayın.
2. Depo kökünde testleri çalıştırın; başarısız test varken senaryoyu referans kabul etmeyin.
3. `scenario.json` dosyasının bir kopyasını değiştirin; referans örneği koruyun.
4. `python app.py demo --input <dosya> --output deney.json` çalıştırın.
5. Beklenen ret/inceleme ile beklenmeyen exception durumunu ayırın.
6. Çıktıyı `sample-report.json` ile karşılaştırın; sentetik negatif örnekleri otomatik başarıya çevirmeyin.

## Projeye özgü kontrol

append transaction → HMAC chain → legal transition → replay/checkpoint

Zincir anahtarı ve güvenilir checkpoint veritabanından bağımsız korunmalıdır.

## Arıza çözümü

JSON parse hatasında girdi biçimini; eksik alan hatasında sözleşmeyi; kural ihlalinde alan bulgusunu; SQLite kilidinde eşzamanlı yazıcı sayısını inceleyin. Gerçek veriyi paylaşmadan önce anonimleştirin. Başarı iddiasını raporun gate/valid/fit/correct/state alanının ilgili semantiğiyle ilişkilendirin; sadece exit code yeterli değildir.

## Üretim açığı

Yerel SQLite değiştirilemez kayıt deposu değildir; demo anahtarı üretimde kullanılmamalıdır.
