import unittest, tempfile, json, sqlite3, copy
from pathlib import Path
import app as c

class CoreTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.sqlite'
        self.config = json.loads((Path(__file__).resolve().parent / 'scenario.json').read_text(encoding='utf-8'))
        with c.sqlite_session(self.path) as connection:
            connection.execute('SELECT 1')
        with self.assertRaises(sqlite3.ProgrammingError):
            connection.execute('SELECT 1')

    def ledger(self):
        return c.EventLedger(self.path, b'1234567890123456')

    def test_transition(self):
        s = self.ledger()
        s.append('1', 'I', 'SEND', {})
        s.append('2', 'I', 'ACK', {})
        self.assertEqual(s.replay()['states']['I'], 'ACCEPTED')

    def test_illegal(self):
        with self.assertRaises(ValueError):
            self.ledger().append('1', 'I', 'ACK', {})

    def test_idempotency(self):
        s = self.ledger()
        self.assertEqual(s.append('1', 'I', 'SEND', {}), s.append('1', 'I', 'SEND', {}))

    def test_conflict(self):
        s = self.ledger()
        s.append('1', 'I', 'SEND', {})
        with self.assertRaises(ValueError):
            s.append('1', 'I', 'SEND', {'x': 1})

    def test_tamper(self):
        s = self.ledger()
        s.append('1', 'I', 'SEND', {})
        with c.sqlite_session(self.path) as db:
            db.execute("UPDATE events SET payload='changed'")
        with self.assertRaises(ValueError):
            s.replay()

    def test_tail_checkpoint(self):
        s = self.ledger()
        s.append('1', 'I', 'SEND', {})
        s.append('2', 'I', 'ACK', {})
        checkpoint = s.replay()['checkpoint']
        with c.sqlite_session(self.path) as db:
            db.execute('DELETE FROM events WHERE seq=2')
        with self.assertRaises(ValueError):
            s.replay(checkpoint)

    def test_short_key(self):
        with self.assertRaises(ValueError):
            c.EventLedger(self.path, b'short')

    def test_projection_ignored_in_replay(self):
        s = self.ledger()
        s.append('1', 'I', 'SEND', {})
        with c.sqlite_session(self.path) as db:
            db.execute("UPDATE projection SET state='ACCEPTED'")
        self.assertEqual(s.replay()['states']['I'], 'SENDING')
if __name__ == '__main__':
    unittest.main()
