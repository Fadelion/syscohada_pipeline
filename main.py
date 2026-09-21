import argparse
import logging
from typing import Callable, Dict

from syscohada_pipeline.core.orchestrator import run_pipeline


def _group_processors() -> Dict[str, Callable]:
    from syscohada_pipeline.groups.group_a import process_document_group_a
    from syscohada_pipeline.groups.group_b import process_document_group_b
    from syscohada_pipeline.groups.group_c import process_document_group_c
    from syscohada_pipeline.groups.group_d import process_document_group_d
    return {"A": process_document_group_a, "B": process_document_group_b,
            "C": process_document_group_c, "D": process_document_group_d}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline SYSCOHADA")
    parser.add_argument("input", help="PDF ou dossier de PDF")
    parser.add_argument("output", help="Dossier de sortie")
    parser.add_argument("--group", choices=["A", "B", "C", "D"], default="A")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    processor = _group_processors()[args.group]
    run_pipeline(args.input, args.output, processor, args.group)


if __name__ == "__main__":
    main()
