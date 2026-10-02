"""Fatura Olay Kaydı ve Replay.

Problem: Geçersiz durum geçişlerini ve olay geçmişinin değiştirilmesini fark ederek projeksiyonu yeniden üretmek.
Method: HMAC zinciri, durum makinesi, dış checkpoint
Invariant: Zincir anahtarı ve güvenilir checkpoint veritabanından bağımsız korunmalıdır.
Boundary: Yerel SQLite değiştirilemez kayıt deposu değildir; demo anahtarı üretimde kullanılmamalıdır."""
import hashlib, hmac, json, sqlite3, tempfile
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def sqlite_session(path, **kwargs):
    """Commit or roll back, then always close the OS file handle."""
    connection = sqlite3.connect(path, **kwargs)
    try:
        with connection:
            yield connection
    finally:
        connection.close()
ALLOWED = {'NEW': {'SEND': 'SENDING'}, 'SENDING': {'ACK': 'ACCEPTED', 'TIMEOUT': 'UNKNOWN', 'REJECT': 'REJECTED'}, 'UNKNOWN': {'RECONCILE': 'ACCEPTED'}, 'ACCEPTED': {}, 'REJECTED': {}}

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

class EventLedger:

    def __init__(self, path, key):
        if len(key) < 16:
            raise ValueError('key must be at least 16 bytes')
        self.path = str(path)
        self.key = key
        with sqlite_session(self.path) as db:
            db.executescript('CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY,event_id TEXT UNIQUE,entity TEXT,kind TEXT,payload TEXT,prev TEXT,digest TEXT);\n          CREATE TABLE IF NOT EXISTS projection(entity TEXT PRIMARY KEY,state TEXT,seq INTEGER);')

    def _signature(self, seq, event_id, entity, kind, payload, previous):
        return hmac.new(self.key, canonical([seq, event_id, entity, kind, payload, previous]).encode(), hashlib.sha256).hexdigest()

    def append(self, event_id, entity, kind, payload):
        with sqlite_session(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT entity,kind,payload,seq FROM events WHERE event_id=?', (event_id,)).fetchone()
            body = canonical(payload)
            if existing:
                if existing[:3] != (entity, kind, body):
                    raise ValueError('event ID conflict')
                return existing[3]
            row = db.execute('SELECT state FROM projection WHERE entity=?', (entity,)).fetchone()
            state = row[0] if row else 'NEW'
            if kind not in ALLOWED[state]:
                raise ValueError(f'illegal transition {state}/{kind}')
            last = db.execute('SELECT seq,digest FROM events ORDER BY seq DESC LIMIT 1').fetchone()
            seq = last[0] + 1 if last else 1
            prev = last[1] if last else 'GENESIS'
            digest = self._signature(seq, event_id, entity, kind, body, prev)
            db.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?)', (seq, event_id, entity, kind, body, prev, digest))
            db.execute('INSERT INTO projection VALUES (?,?,?) ON CONFLICT(entity) DO UPDATE SET state=excluded.state,seq=excluded.seq', (entity, ALLOWED[state][kind], seq))
            return seq

    def replay(self, checkpoint=None):
        previous = 'GENESIS'
        states = {}
        expected = 1
        with sqlite_session(self.path) as db:
            for seq, eid, entity, kind, payload, prev, digest in db.execute('SELECT * FROM events ORDER BY seq'):
                if seq != expected or prev != previous:
                    raise ValueError('broken event sequence')
                actual = self._signature(seq, eid, entity, kind, payload, prev)
                if not hmac.compare_digest(actual, digest):
                    raise ValueError('event chain tampered')
                state = states.get(entity, 'NEW')
                if kind not in ALLOWED[state]:
                    raise ValueError('illegal historical transition')
                states[entity] = ALLOWED[state][kind]
                previous = digest
                expected += 1
            if checkpoint and checkpoint != {'seq': expected - 1, 'digest': previous}:
                raise ValueError('checkpoint mismatch: possible tail truncation')
        return {'states': states, 'checkpoint': {'seq': expected - 1, 'digest': previous}}

def run(config):
    with tempfile.TemporaryDirectory() as temp:
        ledger = EventLedger(Path(temp) / 'events.sqlite', b'SYNTHETIC-DEMO-KEY-DO-NOT-USE')
        for e in config['events']:
            ledger.append(e['id'], e['entity'], e['kind'], e.get('payload', {}))
        report = ledger.replay()
        report['scope'] = 'Integrity verification needs an externally trusted checkpoint; local storage is not immutable.'
        return report
import argparse, json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Run reproducible synthetic project scenario')
    parser.add_argument('command', choices=['demo'])
    parser.add_argument('--input', default='scenario.json')
    parser.add_argument('--output', default='report.json')
    args = parser.parse_args()
    report = run(json.loads(Path(args.input).read_text(encoding='utf-8')))
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print(f'Report: {target}')
if __name__ == '__main__':
    main()
