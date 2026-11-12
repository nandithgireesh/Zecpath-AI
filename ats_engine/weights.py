# ats_engine/weights.py


ROLE_WEIGHTS = {
    "machine learning engineer": {
        "skill": 0.40,
        "experience": 0.25,
        "education": 0.15,
        "semantic": 0.20,
    },
    "ai/ml engineer": {
        "skill": 0.40,
        "experience": 0.25,
        "education": 0.15,
        "semantic": 0.20,
    },
    "ai engineer": {
        "skill": 0.40,
        "experience": 0.25,
        "education": 0.15,
        "semantic": 0.20,
    },
    "business analyst": {
        "skill": 0.35,
        "experience": 0.25,
        "education": 0.20,
        "semantic": 0.20,
    },
    "staff nurse": {
        "skill": 0.35,
        "experience": 0.30,
        "education": 0.25,
        "semantic": 0.10,
    },
    "default": {
        "skill": 0.40,
        "experience": 0.25,
        "education": 0.15,
        "semantic": 0.20,
    },
}


def get_weights(role):

    if not role:
        return ROLE_WEIGHTS["default"]

    role = role.lower().strip()

    return ROLE_WEIGHTS.get(
        role,
        ROLE_WEIGHTS["default"],
    )
