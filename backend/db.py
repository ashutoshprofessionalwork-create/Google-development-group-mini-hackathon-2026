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
            "Dewas Naka Chemical Chimney Smoke",
            10,
            0.98,
            22.7712,
            75.9012,
            "http://localhost:8000/mockdatapic/istockphoto-458921925-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Pithampur Industrial Smoke Stack",
            9,
            0.95,
            22.6148,
            75.6811,
            "http://localhost:8000/mockdatapic/istockphoto-1434607739-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Sanwer Road Metal Foundry Exhaust",
            9,
            0.93,
            22.7820,
            75.8940,
            "http://localhost:8000/mockdatapic/istockphoto-1434610444-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Palasia Dump Yard Open Fire",
            8,
            0.92,
            22.7244,
            75.8839,
            "http://localhost:8000/mockdatapic/istockphoto-2175083463-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Vijay Nagar Heavy Commercial Exhaust",
            8,
            0.90,
            22.7533,
            75.8937,
            "http://localhost:8000/mockdatapic/istockphoto-174655376-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Malwa Mill Furnace Black Smoke",
            8,
            0.89,
            22.7301,
            75.8712,
            "http://localhost:8000/mockdatapic/istockphoto-1272077322-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Rau Bypass Stubble & Biomass Fire",
            7,
            0.88,
            22.6321,
            75.8052,
            "http://localhost:8000/mockdatapic/istockphoto-1438168626-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Sapna Sangeeta Plastic Waste Fire",
            7,
            0.87,
            22.7015,
            75.8621,
            "http://localhost:8000/mockdatapic/istockphoto-2175776925-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Bhawarkua Flyover Construction Dust",
            6,
            0.85,
            22.6916,
            75.8672,
            "http://localhost:8000/mockdatapic/istockphoto-2165806976-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "Rajendra Nagar Crop Residue Smoke",
            5,
            0.83,
            22.6781,
            75.8245,
            "http://localhost:8000/mockdatapic/istockphoto-490452539-612x612.jpg",
            False,
            "ADMIN VERIFIED"
        ),
        (
            "Regal Square Roadside Leaf Smoke",
            4,
            0.82,
            22.7180,
            75.8560,
            "http://localhost:8000/mockdatapic/istockphoto-638167868-612x612.jpg",
            False,
            "PENDING REVIEW"
        ),
        (
            "AB Road Uncovered Aggregate Dust",
            3,
            0.81,
            22.7351,
            75.8890,
            "http://localhost:8000/mockdatapic/istockphoto-534781505-612x612.jpg",
            False,
            "REJECTED"
        ),
        (
            "Super Corridor Traffic Haze",
            2,
            0.79,
            22.7610,
            75.8210,
            "http://localhost:8000/mockdatapic/istockphoto-915098414-612x612.jpg",
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
