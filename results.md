# Çalıştırılmış kabul sonuçları

Python 3.12.14, sentetik `scenario.json`; yerel test sayısı **8**, tümü başarılı. Ham test günlüğü `test-log.txt`.

Replay durumu {'I1': 'ACCEPTED'}; checkpoint sıra 3.

Sonuçlar yalnız bu örneğe aittir; üretim doğruluğu veya performans garantisi olarak yorumlanmamalıdır. Ölçülen iş sonucunu kontrol edin; örnek negatif vaka içeriyorsa ret beklenir. Tam çıktı `sample-report.json`.

## Sınanan davranışlar

| Test | Kontrol |
|---|---|
| `test_transition` | transition |
| `test_illegal` | illegal |
| `test_idempotency` | idempotency |
| `test_conflict` | conflict |
| `test_tamper` | tamper |
| `test_tail_checkpoint` | tail checkpoint |
| `test_short_key` | short key |
| `test_projection_ignored_in_replay` | projection ignored in replay |

## Gelişmiş deney planı

1. Checkpoint dosyasını farklı güven alanında saklayan adaptör ekleyin.
2. Anahtar rotasyonunu key-id ve eski zincir doğrulamasıyla tasarlayın.
3. Projeksiyonu tamamen silip olaylardan atomik yeniden kurun.
4. Ortadan olay silinmesi ile kuyruktan olay silinmesini ayrı tehdit olarak sınayın.
