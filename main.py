from app.db import initialize_database
from app.graph import build_graph
from app.display import display_results


SUPPLIERS = [
    {
        "supplier_name": "Apex Systems",
        "submission_date": "2026-08-25",
        "experience_rating": 8.5,
        "pdf_path": "data/sample_pdfs/apex_systems.pdf",
    },
    {
        "supplier_name": "BrightPath Tech",
        "submission_date": "2026-08-24",
        "experience_rating": 6.5,
        "pdf_path": "data/sample_pdfs/brightpath_tech.pdf",
    },
    {
        "supplier_name": "NexaWorks",
        "submission_date": "2026-08-26",
        "experience_rating": 9.0,
        "pdf_path": "data/sample_pdfs/nexaworks.pdf",
    },
    {
        "supplier_name": "Orbit Digital",
        "submission_date": "2026-08-23",
        "experience_rating": 9.5,
        "pdf_path": "data/sample_pdfs/orbit_digital.pdf",
    },
]


def run_rfp_evaluation(suppliers):
    initialize_database()

    app = build_graph()

    initial_state = {
        "suppliers": suppliers
    }

    final_state = app.invoke(initial_state)
    display_results(final_state)

    return final_state


if __name__ == "__main__":
    run_rfp_evaluation(SUPPLIERS)
