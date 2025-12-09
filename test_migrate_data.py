"""
Unit tests for migrate_data module

Run with: pytest test_migrate_data.py -v

Note: These tests change the current working directory to test the migration
"""
import os
import sqlite3
import tempfile
import shutil
import pytest


@pytest.mark.unit
class TestMigrateDatabase:
    """Tests for database migration functionality"""

    @pytest.fixture
    def isolated_dir(self):
        """Create isolated temp directory and change to it"""
        original_dir = os.getcwd()
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        yield temp_dir
        # Cleanup
        os.chdir(original_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    def create_old_database(self, with_data=True, new_schema=False):
        """Helper to create an old database"""
        conn = sqlite3.connect("emotions.db")
        cursor = conn.cursor()

        if new_schema:
            # Create with new schema
            cursor.execute("""
                CREATE TABLE emotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    emotion TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            # Create with old schema
            cursor.execute("""
                CREATE TABLE emotions (
                    timestamp REAL,
                    emotion TEXT
                )
            """)

        if with_data:
            if new_schema:
                sample_data = [
                    (1638360000.0, "HAPPY"),
                    (1638360060.0, "SAD"),
                ]
                cursor.executemany(
                    "INSERT INTO emotions (timestamp, emotion) VALUES (?, ?)",
                    sample_data
                )
            else:
                sample_data = [
                    (1638360000.0, "HAPPY"),
                    (1638360060.0, "SAD"),
                    (1638360120.0, "ANGRY"),
                    (1638360180.0, "HAPPY"),
                ]
                cursor.executemany("INSERT INTO emotions VALUES (?, ?)", sample_data)

        conn.commit()
        conn.close()

    def test_migrate_no_old_database(self, isolated_dir, capsys):
        """Test migration when old database doesn't exist"""
        from migrate_data import migrate_database

        migrate_database()
        captured = capsys.readouterr()
        assert "No existing emotions.db found" in captured.out

    def test_migrate_creates_data_directory(self, isolated_dir, capsys):
        """Test that migration creates data directory if it doesn't exist"""
        self.create_old_database()
        from migrate_data import migrate_database

        assert not os.path.exists("data")
        migrate_database()
        assert os.path.exists("data")
        assert os.path.exists("data/emotions.db")

    def test_migrate_backs_up_existing_database(self, isolated_dir, capsys):
        """Test that existing new database is backed up before migration"""
        self.create_old_database()

        # Create existing new database
        os.makedirs("data", exist_ok=True)
        shutil.copy("emotions.db", "data/emotions.db")

        from migrate_data import migrate_database
        migrate_database()

        captured = capsys.readouterr()
        assert "backed up" in captured.out.lower()

        # Check that a backup file was created
        backup_files = [f for f in os.listdir("data") if ".backup_" in f]
        assert len(backup_files) > 0

    def test_migrate_copies_database(self, isolated_dir, capsys):
        """Test that old database is copied to new location"""
        self.create_old_database()
        from migrate_data import migrate_database

        migrate_database()
        assert os.path.exists("data/emotions.db")

        captured = capsys.readouterr()
        assert "Copied" in captured.out or "copied" in captured.out

    def test_migrate_updates_schema(self, isolated_dir):
        """Test that old schema is updated to new schema"""
        self.create_old_database()
        from migrate_data import migrate_database

        migrate_database()

        # Check that new schema has all columns
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(emotions)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        assert "id" in columns
        assert "timestamp" in columns
        assert "emotion" in columns
        assert "created_at" in columns

    def test_migrate_preserves_data(self, isolated_dir):
        """Test that data is preserved during migration"""
        self.create_old_database()

        # Get original data
        conn = sqlite3.connect("emotions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, emotion FROM emotions ORDER BY timestamp")
        original_data = cursor.fetchall()
        conn.close()

        from migrate_data import migrate_database
        migrate_database()

        # Get migrated data
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, emotion FROM emotions ORDER BY timestamp")
        migrated_data = cursor.fetchall()
        conn.close()

        # Verify data matches
        assert len(original_data) == len(migrated_data)
        for orig, migr in zip(original_data, migrated_data):
            assert orig[0] == migr[0]  # timestamp
            assert orig[1] == migr[1]  # emotion

    def test_migrate_shows_statistics(self, isolated_dir, capsys):
        """Test that migration displays statistics"""
        self.create_old_database()
        from migrate_data import migrate_database

        migrate_database()
        captured = capsys.readouterr()
        output = captured.out

        assert "Migration complete" in output
        assert "Total emotions migrated" in output
        assert "Emotion distribution" in output
        assert "HAPPY" in output

    def test_migrate_already_new_schema(self, isolated_dir, capsys):
        """Test migration when database already has new schema"""
        self.create_old_database(new_schema=True)
        from migrate_data import migrate_database

        migrate_database()

        # Verify migration completes successfully
        assert os.path.exists("data/emotions.db")

        # Verify schema is correct
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(emotions)")
        columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        assert "id" in columns

        captured = capsys.readouterr()
        assert "Migration complete" in captured.out

    def test_migrate_error_handling(self, isolated_dir, capsys):
        """Test error handling during migration"""
        # Create a corrupted database
        with open("emotions.db", "w") as f:
            f.write("This is not a valid SQLite database")

        from migrate_data import migrate_database
        migrate_database()

        captured = capsys.readouterr()
        # The migration should handle errors gracefully
        assert "Error" in captured.out or "error" in captured.out

    def test_migrate_empty_database(self, isolated_dir, capsys):
        """Test migration of empty database"""
        self.create_old_database(with_data=False)
        from migrate_data import migrate_database

        migrate_database()

        captured = capsys.readouterr()
        assert "Migration complete" in captured.out
        assert "Total emotions migrated: 0" in captured.out

    def test_migrate_large_database(self, isolated_dir, capsys):
        """Test migration of database with many records"""
        conn = sqlite3.connect("emotions.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE emotions (
                timestamp REAL,
                emotion TEXT
            )
        """)

        # Insert 1000 records
        import time
        base_time = time.time()
        emotions = ["HAPPY", "SAD", "ANGRY", "SURPRISED", "CALM"]
        data = [(base_time + i, emotions[i % len(emotions)]) for i in range(1000)]
        cursor.executemany("INSERT INTO emotions VALUES (?, ?)", data)
        conn.commit()
        conn.close()

        from migrate_data import migrate_database
        migrate_database()

        # Verify all records migrated
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emotions")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == 1000

        captured = capsys.readouterr()
        assert "Total emotions migrated: 1000" in captured.out

    def test_migrate_special_characters_in_emotions(self, isolated_dir):
        """Test migration handles special characters in emotion data"""
        conn = sqlite3.connect("emotions.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE emotions (
                timestamp REAL,
                emotion TEXT
            )
        """)

        # Insert data with special characters
        special_data = [
            (1638360000.0, "HAPPY"),
            (1638360060.0, "test'quote"),
            (1638360120.0, "test\"doublequote"),
        ]
        cursor.executemany("INSERT INTO emotions VALUES (?, ?)", special_data)
        conn.commit()
        conn.close()

        from migrate_data import migrate_database
        migrate_database()

        # Verify data with special characters migrated correctly
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT emotion FROM emotions ORDER BY timestamp")
        emotions = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert "test'quote" in emotions
        assert "test\"doublequote" in emotions

    def test_migrate_preserves_timestamps(self, isolated_dir):
        """Test that timestamps are preserved accurately"""
        import time

        # Create database with precise timestamps
        conn = sqlite3.connect("emotions.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE emotions (
                timestamp REAL,
                emotion TEXT
            )
        """)

        timestamps = [
            1638360000.123456,
            1638360060.654321,
            1638360120.999999,
        ]
        data = [(ts, "HAPPY") for ts in timestamps]
        cursor.executemany("INSERT INTO emotions VALUES (?, ?)", data)
        conn.commit()
        conn.close()

        from migrate_data import migrate_database
        migrate_database()

        # Verify timestamps preserved
        conn = sqlite3.connect("data/emotions.db")
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM emotions ORDER BY timestamp")
        migrated_timestamps = [row[0] for row in cursor.fetchall()]
        conn.close()

        for orig, migr in zip(timestamps, migrated_timestamps):
            assert abs(orig - migr) < 0.000001  # Allow tiny floating point error
