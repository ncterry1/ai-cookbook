# Need these 3 below to move back one directory to import associated modules
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from gui.aiGuiUbuntu import run_app

if __name__ == "__main__":
    run_app()