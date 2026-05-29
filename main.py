import argparse
import subprocess
import sys

def run_script(script_path):
    print(f"\n========== Running {script_path} ==========\n")
    try:
        subprocess.run([sys.executable, script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] '{script_path}' failed with exit status {e.returncode}")
        sys.exit(e.returncode)

def main():
    parser = argparse.ArgumentParser(description="YouTube Comments Sentiment Analysis Pipeline")
    
    parser.add_argument("--scrape", action="store_true", help="Run scraping step (src/scraping.py)")
    parser.add_argument("--clean", action="store_true", help="Run cleaning step (src/cleaning.py) - also triggers split")
    parser.add_argument("--split", action="store_true", help="Run standalone splitting step (src/splitting.py)")
    parser.add_argument("--label", action="store_true", help="Run auto-labeling step (src/labeling.py)")
    parser.add_argument("--merge", action="store_true", help="Run merging step (src/merging.py)")
    parser.add_argument("--prepare", action="store_true", help="Run data preparation steps: scrape, clean, and label")
    parser.add_argument("--train", action="store_true", help="Run training step (src/training.py)")
    parser.add_argument("--test", action="store_true", help="Run evaluation/test step (src/testing.py)")
    parser.add_argument("--all", action="store_true", help="Run the full pipeline: prepare (scrape, clean, label), merge, train, and test")

    args = parser.parse_args()

    # If no arguments are provided, print help message
    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)
        
    if args.prepare:
        print("\n[INFO] Flag --prepare detected. Running data preparation steps: scrape -> clean (and split) -> label.")
        print("Merging, training, and testing steps will NOT be run automatically.\n")
        args.scrape = True
        args.clean = True
        args.label = True

    if args.all:
        print("\n[INFO] Flag --all detected. Running full pipeline: scrape -> clean (and split) -> label.")
        print("Merging, training, and testing steps will be run automatically.\n")
        args.scrape = True
        args.clean = True
        args.label = True
        args.merge = True
        args.train = True
        args.test = True

    if args.scrape:
        run_script("src/scraping.py")
    if args.clean:
        run_script("src/cleaning.py")
    if args.split:
        run_script("src/splitting.py")
    if args.label:
        run_script("src/labeling.py")
    if args.merge:
        run_script("src/merging.py")
    if args.train:
        run_script("src/training.py")
    if args.test:
        run_script("src/testing.py")

if __name__ == "__main__":
    main()
