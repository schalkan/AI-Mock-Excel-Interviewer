import sys
import os

# Ensure project root is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now imports will work regardless of how script is run
from frontend.components.welcome import WelcomeComponent


def main():
    print("Starting app...")
    welcome = WelcomeComponent()
    welcome.render()


if __name__ == "__main__":
    main()