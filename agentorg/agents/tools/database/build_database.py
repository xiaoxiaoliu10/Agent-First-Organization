import sqlite3
import argparse
from pathlib import Path
import os


def build_database(folder_path):
    db_path = Path(folder_path) / "show_booking_db.sqlite"
    if os.path.exists(db_path):
        os.remove(db_path)
    # Creating the database with a .sqlite extension
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables based on the provided schema
    cursor.execute('''
        CREATE TABLE show (
            id VARCHAR(40) PRIMARY KEY,
            show_name VARCHAR(100),
            genre VARCHAR(40),
            date DATE,
            time TIME,
            description TEXT,
            location VARCHAR(100),
            price DECIMAL,
            available_seats INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE user (
            id VARCHAR(40) PRIMARY KEY,
            first_name VARCHAR(40),
            last_name VARCHAR(40),
            email VARCHAR(60),
            register_at TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE booking (
            id VARCHAR(40) PRIMARY KEY,
            show_id VARCHAR(40),
            user_id VARCHAR(40),
            created_at TIMESTAMP,
            FOREIGN KEY (show_id) REFERENCES show(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
        )
    ''')

    # Populate sample data
    shows = [
        {
            "show_name": "La Traviata",
            "genre": "Opera",
            "date": "2024-11-10",
            "time": "19:30:00",
            "description": "A classic opera by Giuseppe Verdi.",
            "location": "Metropolitan Opera House, New York, NY",
            "price": 150.0,
            "available_seats": 200,
            "id": "show_8406f0c6-6644-4a19-9448-670c9941b8d8"
        },
        {
            "show_name": "La Traviata",
            "genre": "Opera",
            "date": "2024-11-15",
            "time": "19:30:00",
            "description": "A classic opera by Giuseppe Verdi.",
            "location": "Metropolitan Opera House, New York, NY",
            "price": 150.0,
            "available_seats": 200,
            "id": "show_06d03f1d-c38c-4ab2-b210-3342c76425f5"
        },
        {
            "show_name": "Carmen",
            "genre": "Opera",
            "date": "2024-11-12",
            "time": "20:00:00",
            "description": "A passionate opera by Georges Bizet.",
            "location": "San Francisco Opera, San Francisco, CA",
            "price": 120.0,
            "available_seats": 150,
            "id": "show_c32f2e1f-798a-406d-979b-733c2b37d90c"
        },
        {
            "show_name": "The Magic Flute",
            "genre": "Opera",
            "date": "2024-11-15",
            "time": "18:30:00",
            "description": "A whimsical opera by Wolfgang Amadeus Mozart.",
            "location": "Lyric Opera of Chicago, Chicago, IL",
            "price": 130.0,
            "available_seats": 180,
            "id": "show_84c92d38-1f01-4251-ac57-334fb8244477"
        },
        {
            "show_name": "The Magic Flute",
            "genre": "Opera",
            "date": "2024-11-20",
            "time": "18:30:00",
            "description": "A whimsical opera by Wolfgang Amadeus Mozart.",
            "location": "Lyric Opera of Chicago, Chicago, IL",
            "price": 130.0,
            "available_seats": 180,
            "id": "show_44df967e-e4ef-44ec-923a-a118be06240d"
        },
        {
            "show_name": "The Magic Flute",
            "genre": "Opera",
            "date": "2024-11-25",
            "time": "18:30:00",
            "description": "A whimsical opera by Wolfgang Amadeus Mozart.",
            "location": "Lyric Opera of Chicago, Chicago, IL",
            "price": 130.0,
            "available_seats": 180,
            "id": "show_c7ac8410-e03d-45e8-9b50-6a9c72b87805"
        },
        {
            "show_name": "Madama Butterfly",
            "genre": "Opera",
            "date": "2024-11-18",
            "time": "19:00:00",
            "description": "A tragic opera by Giacomo Puccini.",
            "location": "Houston Grand Opera, Houston, TX",
            "price": 140.0,
            "available_seats": 160,
            "id": "show_851cd9f3-734d-414e-b75c-5a389dc6a380"
        },
        {
            "show_name": "Don Giovanni",
            "genre": "Opera",
            "date": "2024-11-20",
            "time": "19:30:00",
            "description": "A dramatic opera by Wolfgang Amadeus Mozart.",
            "location": "Los Angeles Opera, Los Angeles, CA",
            "price": 155.0,
            "available_seats": 170,
            "id": "show_0a3babd6-d153-41f7-bab0-8a6a995ffb5a"
        },
        {
            "show_name": "Don Giovanni",
            "genre": "Opera",
            "date": "2024-11-20",
            "time": "19:30:00",
            "description": "A dramatic opera by Wolfgang Amadeus Mozart.",
            "location": "Washington National Opera, Washington, D.C.",
            "price": 155.0,
            "available_seats": 170,
            "id": "show_2be3c426-2822-45dc-84f0-68609ca53f86"
        },
        {
            "show_name": "Don Giovanni",
            "genre": "Opera",
            "date": "2024-11-20",
            "time": "19:30:00",
            "description": "A dramatic opera by Wolfgang Amadeus Mozart.",
            "location": "Metropolitan Opera House, New York, NY",
            "price": 155.0,
            "available_seats": 170,
            "id": "show_11604b40-6058-4264-8c80-95d774596d12"
        },
        {
            "show_name": "Rigoletto",
            "genre": "Opera",
            "date": "2024-11-22",
            "time": "20:00:00",
            "description": "A compelling opera by Giuseppe Verdi.",
            "location": "Washington National Opera, Washington, D.C.",
            "price": 145.0,
            "available_seats": 190,
            "id": "show_1ebd551f-3fa6-41c4-88f5-e7a9e82cc876"
        },
        {
            "show_name": "Turandot",
            "genre": "Opera",
            "date": "2024-11-25",
            "time": "19:00:00",
            "description": "A powerful opera by Giacomo Puccini.",
            "location": "San Francisco Opera, San Francisco, CA",
            "price": 160.0,
            "available_seats": 175,
            "id": "show_81c12485-a9eb-4721-bee4-e4c89b046678"
        },
        {
            "show_name": "Aida",
            "genre": "Opera",
            "date": "2024-11-28",
            "time": "19:30:00",
            "description": "An epic opera by Giuseppe Verdi.",
            "location": "Metropolitan Opera House, New York, NY",
            "price": 170.0,
            "available_seats": 200,
            "id": "show_ea2f97be-05bf-4640-b6eb-47118a42ab9d"
        },
        {
            "show_name": "The Barber of Seville",
            "genre": "Opera",
            "date": "2024-11-30",
            "time": "18:30:00",
            "description": "A comedic opera by Gioachino Rossini.",
            "location": "Lyric Opera of Chicago, Chicago, IL",
            "price": 135.0,
            "available_seats": 180,
            "id": "show_2ec864f2-36a4-4fc3-8e83-2a87cec585d9"
        },
        {
            "show_name": "La Boh\u00e8me",
            "genre": "Opera",
            "date": "2024-12-02",
            "time": "19:00:00",
            "description": "A romantic opera by Giacomo Puccini.",
            "location": "Houston Grand Opera, Houston, TX",
            "price": 150.0,
            "available_seats": 160,
            "id": "show_42c86393-4346-49bf-b0b3-f82b3fc78e55"
        },
        {
            "show_name": "Tosca",
            "genre": "Opera",
            "date": "2024-12-05",
            "time": "19:30:00",
            "description": "A dramatic opera by Giacomo Puccini.",
            "location": "Los Angeles Opera, Los Angeles, CA",
            "price": 155.0,
            "available_seats": 170,
            "id": "show_b43297c2-fec1-4028-b5d0-27b04b22fc2d"
        },
        {
            "show_name": "The Marriage of Figaro",
            "genre": "Opera",
            "date": "2024-12-08",
            "time": "19:00:00",
            "description": "A lively opera by Wolfgang Amadeus Mozart.",
            "location": "San Francisco Opera, San Francisco, CA",
            "price": 140.0,
            "available_seats": 175,
            "id": "show_21837fdd-5819-4135-8a83-977259870b78"
        },
        {
            "show_name": "Otello",
            "genre": "Opera",
            "date": "2024-12-10",
            "time": "19:30:00",
            "description": "A tragic opera by Giuseppe Verdi.",
            "location": "Metropolitan Opera House, New York, NY",
            "price": 165.0,
            "available_seats": 200,
            "id": "show_5e6515c5-f2f9-43e7-a34b-9195b063f863"
        },
        {
            "show_name": "Lucia di Lammermoor",
            "genre": "Opera",
            "date": "2024-12-12",
            "time": "19:00:00",
            "description": "A dramatic opera by Gaetano Donizetti.",
            "location": "Lyric Opera of Chicago, Chicago, IL",
            "price": 145.0,
            "available_seats": 180,
            "id": "show_248b5f97-7d1a-4ec2-abb9-3c6163074dd0"
        }
    ]

    users = [
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@gmail.com",
            "register_at": "2024-10-01 09:15:00",
            "last_login": "2024-10-12 08:30:00",
            "id": "user_be6e1836-8fe9-4938-b2d0-48f810648e72"
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@gmail.com",
            "register_at": "2024-10-02 10:00:00",
            "last_login": "2024-10-13 07:45:00",
            "id": "user_ffd7218a-31c4-4377-902e-33faf36d168c"
        },
        {
            "first_name": "Carol",
            "last_name": "Williams",
            "email": "carol.williams@gmail.com",
            "register_at": "2024-10-03 11:30:00",
            "last_login": "2024-10-14 09:00:00",
            "id": "user_7404fbd7-d043-4d4c-80e6-28c9ae81dacc"
        },
        {
            "first_name": "David",
            "last_name": "Jones",
            "email": "david.jones@gmail.com",
            "register_at": "2024-10-04 12:00:00",
            "last_login": "2024-10-15 09:30:00",
            "id": "user_42f20628-1989-4d87-81e6-4f4faca63410"
        },
        {
            "first_name": "Eve",
            "last_name": "Brown",
            "email": "eve.brown@gmail.com",
            "register_at": "2024-10-05 13:45:00",
            "last_login": "2024-10-16 10:15:00",
            "id": "user_13074ec4-3813-4bbd-afa4-339e9eee27e9"
        }
    ]

    # Insert data into the database
    for show in shows:
        columns = ', '.join(show.keys())
        placeholders = ', '.join(['?'] * len(show))
        values = tuple(show.values())
        sql = f"INSERT INTO show ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)

    for user in users:
        columns = ', '.join(user.keys())
        placeholders = ', '.join(['?'] * len(user))
        values = tuple(user.values())
        sql = f"INSERT INTO user ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, values)

    cursor.execute('''
        INSERT INTO booking (id, show_id, user_id, created_at)
        VALUES
            ('1', 'show_8406f0c6-6644-4a19-9448-670c9941b8d8', 'user_be6e1836-8fe9-4938-b2d0-48f810648e72', '2024-10-12 10:00:00')
    ''')

    # Commit changes and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder_path", required=True, type=str, help="location to save the documents")
    args = parser.parse_args()

    if not os.path.exists(args.folder_path):
        os.makedirs(args.folder_path)

    build_database(args.folder_path)