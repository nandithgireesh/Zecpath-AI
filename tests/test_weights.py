import os
import sys

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ats_engine.weights import get_weights


def main():

    roles = [
        "Machine Learning Engineer",
        "Business Analyst",
        "Staff Nurse",
        "Unknown Role",
    ]

    for role in roles:

        weights = get_weights(role)

        print("=" * 60)
        print("Role:", role)
        print("Weights:", weights)
        print("Total:", sum(weights.values()))


if __name__ == "__main__":
    main()
