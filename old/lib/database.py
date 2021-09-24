import logging
import psycopg2

class Database:
    def __init__(self, host: str, port: int, username: str, password: str, base: str):
        self._host = host
        self._port = port
        self._user = username
        self._pass = password
        self._base = base
        self._conn = None
        self._logger = logging.getLogger(__name__)

    def connect(self):
        self._conn = psycopg2.connect('dbname={} user={} host={} port={} password={}'.format(
            self._base,
            self._user,
            self._host,
            self._port,
            self._pass,
        ))

    def close(self) -> None:
        if self._conn:
            self._conn.close()
        self._conn = None

    def get_or_create_person(self, name: str) -> int:
        c = self._conn.cursor()

        # Fetch person from DB
        c.execute('SELECT id FROM person WHERE name = %(name)s', { 'name': name })
        row = c.fetchone()

        # Create if it does not exist:
        if not row:
            c.execute('INSERT INTO person(name) VALUES(%(name)s) RETURNING id', { 'name': name })
            self._conn.commit()
            row = c.fetchone()
            self._logger.debug('Created new person %s with ID %d', name, row[0])

        c.close()

        return row[0]

    def get_name(self, person_id: int) -> str:
        c = self._conn.cursor()

        # Fetch person from DB
        c.execute('SELECT name FROM person WHERE id = %(id)s', { 'id': person_id })
        row = c.fetchone()

        c.close()

        return row[0] if row else None

    def add_encoding(self, person_id: int, filename: str, encoding: list) -> int:
        c = self._conn.cursor()
        c.execute('INSERT INTO vector(person_id, file, vec_low, vec_high) VALUES(%(person)s, %(file)s, CUBE(%(vec_low)s), CUBE(%(vec_high)s)) RETURNING id', {
            'person': person_id,
            'file': filename,
            'vec_low': list(float(s) for s in encoding[0:64]),
            'vec_high': list(float(s) for s in encoding[64:128]),
        })
        row = c.fetchone()
        self._conn.commit()
        self._logger.debug('Created new encoding #%d for person #%d', row[0], person_id)

        c.close()

        return row[0]

    def search_person(self, encoding: list, threshold: float = 0.6) -> tuple[int, float]:
        c = self._conn.cursor()
        c.execute(
            'SELECT person_id, MIN(SQRT(POWER(CUBE(%(vec_low)s) <-> vec_low, 2) + POWER(CUBE(%(vec_high)s) <-> vec_high, 2))) AS score '
            'FROM vector '
            'WHERE SQRT(POWER(CUBE(%(vec_low)s) <-> vec_low, 2) + POWER(CUBE(%(vec_high)s) <-> vec_high, 2)) <= %(threshold)s '
            'GROUP BY 1 '
            'ORDER BY 2 ASC '
            'LIMIT 1', {
                'vec_low': list(float(s) for s in encoding[0:64]),
                'vec_high': list(float(s) for s in encoding[64:128]),
                'threshold': threshold,
            }
        )
        row = c.fetchone()
        c.close()
        
        return row
