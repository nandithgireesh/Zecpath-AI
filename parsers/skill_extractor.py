import re
from sentence_transformers import SentenceTransformer, util

from data.skills.skill_dictionary import (
    TECHNICAL_SKILLS,
    BUSINESS_SKILLS,
    CREATIVE_SKILLS,
    SKILL_SYNONYMS,
    SKILL_STACKS,
)


class SkillExtractor:

    def __init__(self):
        self.technical_skills = TECHNICAL_SKILLS
        self.business_skills = BUSINESS_SKILLS
        self.creative_skills = CREATIVE_SKILLS
        self.skill_synonyms = SKILL_SYNONYMS
        self.skill_stacks = SKILL_STACKS

        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        # Combine all skills
        self.all_skills = (
            list(self.technical_skills)
            + list(self.business_skills)
            + list(self.creative_skills)
        )

        # Precompute embeddings
        self.skill_embeddings = self.model.encode(
            self.all_skills, convert_to_tensor=True
        )

    def clean_text(self, text):
        """
        Clean resume text before extracting skills.
        """

        text = text.lower()

        # Convert separators to spaces
        text = text.replace("-", " ")
        text = text.replace(".", " ")

        # Remove unwanted characters
        text = re.sub(r"[^a-zA-Z0-9+#\s]", " ", text)

        # Remove extra spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def normalize_skill(self, skill):
        """
        Normalize skill names before lookup.
        """

        skill = skill.lower().strip()

        # Normalize punctuation
        skill = skill.replace("-", " ")
        skill = skill.replace(".", " ")

        # Remove extra spaces
        skill = " ".join(skill.split())

        # Apply synonym mapping
        return self.skill_synonyms.get(skill, skill)

    def expand_skill_stack(self, text):
        """
        Detect stack names (MERN, MEAN, etc.)
        and expand them into individual skills.
        """

        text = text.lower()

        expanded = set()

        for stack, skills in self.skill_stacks.items():

            if stack in text:

                expanded.update(skills)

        return expanded

    def get_skill_confidence(self, skill, text):
        """
        Calculate confidence score for an extracted skill.
        """

        text = text.lower()
        skill = skill.lower()

        # Exact dictionary match
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, text):
            return 1.00

        # Synonym match
        for synonym, actual_skill in self.skill_synonyms.items():

            if actual_skill == skill:

                synonym_pattern = r"\b" + re.escape(synonym) + r"\b"

                if re.search(synonym_pattern, text):
                    return 0.95

        # Technology stack
        for stack, skills in self.skill_stacks.items():

            if skill in skills and stack in text:
                return 0.90

        # NLP similarity
        predicted = self.predict_skill_nlp(skill)

        if predicted is not None:
            return 0.85

        return 0.50

    def predict_skill_nlp(self, phrase, threshold=0.75):
        """
        Predict the closest known skill using semantic similarity.
        """
        phrase = self.normalize_skill(phrase)

        phrase_embedding = self.model.encode(phrase, convert_to_tensor=True)

        similarities = util.cos_sim(phrase_embedding, self.skill_embeddings)[0]

        best_index = similarities.argmax().item()

        best_score = similarities[best_index].item()

        if best_score >= threshold:

            predicted_skill = self.all_skills[best_index]

            return predicted_skill

        return None

    def extract_skills(self, text):
        """
        Extract technical, business, and creative skills
        using the master skill dictionary.
        """

        text = self.clean_text(text)

        # Expand technology stacks (MERN, MEAN, etc.)
        expanded_stack_skills = self.expand_skill_stack(text)

        technical = set()
        business = set()
        creative = set()

        # -----------------------------
        # Technical Skills
        # -----------------------------
        for skill in self.technical_skills:

            pattern = r"\b" + re.escape(skill.lower()) + r"\b"

            if re.search(pattern, text):
                technical.add(skill)

        # -----------------------------
        # Business Skills
        # -----------------------------
        for skill in self.business_skills:

            pattern = r"\b" + re.escape(skill.lower()) + r"\b"

            if re.search(pattern, text):
                business.add(skill)

        # -----------------------------
        # Creative Skills
        # -----------------------------
        for skill in self.creative_skills:

            pattern = r"\b" + re.escape(skill.lower()) + r"\b"

            if re.search(pattern, text):
                creative.add(skill)

        # -----------------------------
        # Add skills from technology stacks
        # -----------------------------
        for skill in expanded_stack_skills:

            if skill in self.technical_skills:
                technical.add(skill)

            elif skill in self.business_skills:
                business.add(skill)

            elif skill in self.creative_skills:
                creative.add(skill)

        # -----------------------------
        # Return extracted skills
        # -----------------------------
        return {
            "technical_skills": sorted(list(technical)),
            "business_skills": sorted(list(business)),
            "creative_skills": sorted(list(creative)),
        }

    def extract_skills_with_confidence(self, text):
        """
        Extract skills along with confidence scores.
        """

        skills = self.extract_skills(text)

        result = {}

        for category, skill_list in skills.items():

            result[category] = []

            for skill in skill_list:

                result[category].append(
                    {
                        "skill": skill,
                        "confidence": self.get_skill_confidence(skill, text),
                    }
                )

        return result
