# Tasarım kararları

## Alan motorunu CLI'dan ayırmak

`run(config)` orkestrasyonu kaynak kodun doğrudan test edilebilmesini sağlar. JSON arayüz taşınabilirliği artırır; bu sürüm kullanıcı arayüzü barındırmaz.

## Seçilen yöntem

HMAC zinciri, durum makinesi, dış checkpoint. Zincir anahtarı ve güvenilir checkpoint veritabanından bağımsız korunmalıdır.

## Bilinçli sınır

Yerel SQLite değiştirilemez kayıt deposu değildir; demo anahtarı üretimde kullanılmamalıdır.

## Önerilen sonraki doğrulama

Gerçek kullanım hacmiyle testten önce mevcut kabul ve ret örneklerinin alan uzmanı tarafından onaylanması gerekir. Sonraki sürüm performans ölçümleri, dış adaptör sözleşmesi ve üretim gözlemlenebilirliğini ayrı karar kayıtlarında ele almalıdır.
