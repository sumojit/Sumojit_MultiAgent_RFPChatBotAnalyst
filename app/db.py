import json
import sqlite3
from datetime import datetime
from .config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_criteria (
            criterion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            weight REAL NOT NULL,
            max_score REAL NOT NULL DEFAULT 10,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfp_runs (
            rfp_run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfp_run_criteria (
            run_criterion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfp_run_id INTEGER NOT NULL,
            criterion_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            weight REAL NOT NULL,
            max_score REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rfp_suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            rfp_run_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            submission_date TEXT NOT NULL,
            experience_rating REAL NOT NULL,
            absolute_score REAL,
            ppi REAL,
            final_rank INTEGER,
            result_json TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluation_results (
            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            criterion_id INTEGER NOT NULL,
            raw_score REAL,
            normalized_score REAL,
            justification TEXT,
            evidence_json TEXT,
            warnings_json TEXT,
            weighted_score REAL,
            benchmark_score REAL,
            criterion_gap REAL,
            relative_percentage REAL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM evaluation_criteria")
    count = cursor.fetchone()[0]

    if count == 0:
        criteria = [
            ("Technical Capability",
             "Architecture, integrations, scalability, technical fit", 0.30, 10),
            ("Implementation Plan",
             "Timeline, milestones, staffing, risk plan", 0.20, 10),
            ("Commercial Value",
             "Pricing clarity, total cost, assumptions", 0.20, 10),
            ("Security & Compliance",
             "Controls, certifications, privacy, auditability", 0.20, 10),
            ("Support & Experience",
             "Support model, similar projects, references", 0.10, 10),
        ]

        cursor.executemany("""
            INSERT INTO evaluation_criteria
            (name, description, weight, max_score)
            VALUES (?, ?, ?, ?)
        """, criteria)

        print("Default evaluation criteria inserted.")
    else:
        print("Existing evaluation criteria preserved.")

    conn.commit()
    conn.close()


def load_active_criteria():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT criterion_id, name, description, weight, max_score
        FROM evaluation_criteria
        WHERE is_active = 1
        ORDER BY criterion_id
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "criterion_id": row[0],
            "name": row[1],
            "description": row[2],
            "weight": float(row[3]),
            "max_score": float(row[4]),
        }
        for row in rows
    ]


def validate_criteria(criteria):
    if not criteria:
        raise ValueError("No active evaluation criteria found.")

    total_weight = sum(c["weight"] for c in criteria)

    if abs(total_weight - 1.0) > 1e-9:
        raise ValueError(
            f"Active criteria weights must total 100%. "
            f"Current total = {total_weight * 100:.2f}%"
        )

    for criterion in criteria:
        if criterion["weight"] < 0:
            raise ValueError(f"Negative weight for {criterion['name']}.")
        if criterion["max_score"] <= 0:
            raise ValueError(f"Invalid max score for {criterion['name']}.")


def create_run(criteria):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO rfp_runs (created_at, status)
        VALUES (?, ?)
    """, (datetime.now().isoformat(), "RUNNING"))

    run_id = cursor.lastrowid

    for criterion in criteria:
        cursor.execute("""
            INSERT INTO rfp_run_criteria
            (rfp_run_id, criterion_id, name, description, weight, max_score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            run_id,
            criterion["criterion_id"],
            criterion["name"],
            criterion["description"],
            criterion["weight"],
            criterion["max_score"],
        ))

    conn.commit()
    conn.close()
    return run_id


def persist_results(run_id, rankings):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        for supplier in rankings:
            cursor.execute("""
                INSERT INTO rfp_suppliers
                (
                    rfp_run_id, supplier_name, submission_date,
                    experience_rating, absolute_score, ppi,
                    final_rank, result_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                supplier["supplier_name"],
                supplier["submission_date"],
                supplier["experience_rating"],
                supplier["absolute_score"],
                supplier["ppi"],
                supplier["final_rank"],
                json.dumps(supplier, indent=2),
            ))

            supplier_id = cursor.lastrowid

            for result in supplier["criteria"]:
                cursor.execute("""
                    INSERT INTO evaluation_results
                    (
                        supplier_id, criterion_id, raw_score,
                        normalized_score, justification, evidence_json,
                        warnings_json, weighted_score, benchmark_score,
                        criterion_gap, relative_percentage
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    supplier_id,
                    result["criterion_id"],
                    result["raw_score"],
                    result["score"],
                    result["justification"],
                    json.dumps(result["evidence"]),
                    json.dumps(result["warnings"]),
                    result["weighted_score"],
                    result.get("benchmark_score"),
                    result.get("criterion_gap"),
                    result.get("relative_percentage"),
                ))

        cursor.execute("""
            UPDATE rfp_runs
            SET status = ?
            WHERE rfp_run_id = ?
        """, ("COMPLETED", run_id))

        conn.commit()

    except Exception:
        cursor.execute("""
            UPDATE rfp_runs
            SET status = ?
            WHERE rfp_run_id = ?
        """, ("FAILED", run_id))
        conn.commit()
        raise

    finally:
        conn.close()
