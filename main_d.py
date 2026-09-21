import sys
import logging
from syscohada_pipeline.core.orchestrator import run_pipeline
from syscohada_pipeline.groups.group_d import process_document_group_d

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 main_d.py <chemin_vers_pdf_ou_dossier> [dossier_sortie]")
        sys.exit(1)
    run_pipeline(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "./output", process_document_group_d, "D")
