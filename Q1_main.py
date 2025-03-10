import argparse
import subprocess
import sys

def run_script(option):
    """ This is the main code that runs the Q1 scripts based on the option provided """
    script_map = {
        'a': 'Q1a.py',
        'b': 'Q1b.py',
        'c': 'Q1c.py',
        'd': 'Q1d.py'
    }

    script = script_map.get(option)
    if script:
        subprocess.run([sys.executable, script], check=True)
    else:
        print("Invalid option. Please choose from 'a', 'b', 'c', or 'd'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Q1 scripts")
    parser.add_argument('--option', choices=['a', 'b', 'c', 'd'], required=True, help="Option to run the corresponding Q1 script")
    args = parser.parse_args()

    run_script(args.option)