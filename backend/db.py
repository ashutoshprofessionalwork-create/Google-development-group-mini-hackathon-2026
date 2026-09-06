import sqlite3


def get_db():
    conn = sqlite3.connect("vayunetra.db", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def seed_mock_data(conn):
    cursor = conn.cursor()
    # Clear old data
    cursor.execute("DELETE FROM reports")
    
    mock_items = [
        (
            "Chemical Chimney Smoke",
            10,
            0.96,
            22.7712,
            75.9012,
            "http://localhost:8000/mockdatapic/istockphoto-458921925-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Industrial Factory Smoke Stack",
            9,
            0.94,
            22.6148,
            75.6811,
            "http://localhost:8000/mockdatapic/istockphoto-1434607739-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Garbage Dump Fire Emission",
            8,
            0.91,
            22.7244,
            75.8839,
            "http://localhost:8000/mockdatapic/istockphoto-2175083463-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Heavy Diesel Exhaust Plume",
            8,
            0.89,
            22.7533,
            75.8937,
            "http://localhost:8000/mockdatapic/istockphoto-174655376-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Biomass & Open Straw Burning",
            7,
            0.88,
            22.6321,
            75.8052,
            "http://localhost:8000/mockdatapic/istockphoto-1438168626-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Construction Dust Cloud",
            6,
            0.85,
            22.6916,
            75.8672,
            "http://localhost:8000/mockdatapic/istockphoto-2165806976-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Agricultural Stubble Smoke",
            5,
            0.83,
            22.6781,
            75.8245,
            "http://localhost:8000/mockdatapic/istockphoto-490452539-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Uncovered Cement Dust",
            3,
            0.81,
            22.7351,
            75.8890,
            "http://localhost:8000/mockdatapic/istockphoto-534781505-612x612.jpg",
            False,
            "REJECTED"
        )
    ]

    cursor.executemany(
        """
        INSERT INTO reports (pollution_type, severity, confidence, lat, lon, image_url, is_spam, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        mock_items
    )
    conn.commit()


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pollution_type TEXT,
            severity INTEGER,
            confidence FLOAT,
            lat REAL,
            lon REAL,
            image_url TEXT,
            is_spam BOOLEAN,
            status TEXT DEFAULT 'PENDING REVIEW'
        )
    """)
    try:
        conn.execute("ALTER TABLE reports ADD COLUMN status TEXT DEFAULT 'PENDING REVIEW'")
    except sqlite3.OperationalError:
        pass
    
    # Always seed clean mock data with mockdatapic images
    seed_mock_data(conn)
    conn.commit()
