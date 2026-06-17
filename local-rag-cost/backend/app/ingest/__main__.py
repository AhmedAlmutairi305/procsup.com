import argparse
from .pipeline import ingest_folder


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()
    result = ingest_folder(args.folder, args.workspace)
    print(f"Indexed: {result['indexed']}, skipped (dedup): {result['skipped']}")


if __name__ == "__main__":
    main()
