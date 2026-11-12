import os
import sys
import json
from typing import Dict, List, Optional, Any, Union

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screening_ai.question_models import (
    ScreeningQuestion,
    QuestionCategory,
    AnswerType,
    ImportanceLevel,
    ScreeningCallScript,
    ScreeningCallScriptItem,
)
from utils.logger import logger


class ScreeningQuestionBank:
    """
    Day 22 - HR Screening Question Bank & Dataset Manager.
    
    Manages structured, AI-ready question repositories for automated voice screening calls.
    Supports multi-role filtering, answer-type tagging, dynamic template rendering,
    and multilingual localization.
    """

    def __init__(
        self,
        dataset_path: Optional[str] = None,
        category_mapping_path: Optional[str] = None,
        conversation_flow_path: Optional[str] = None,
    ):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dataset_path = dataset_path or os.path.join(
            base_dir, "data", "screening_questions", "hr_screening_questions.json"
        )
        self.category_mapping_path = category_mapping_path or os.path.join(
            base_dir, "data", "screening_questions", "question_category_mapping.json"
        )
        self.conversation_flow_path = conversation_flow_path or os.path.join(
            base_dir, "data", "screening_questions", "ai_conversation_flows.json"
        )

        self.questions: Dict[str, ScreeningQuestion] = {}
        self.category_taxonomy: Dict[str, Any] = {}
        self.conversation_flows: Dict[str, Any] = {}

        self.load_dataset()
        self.load_category_mapping()
        self.load_conversation_flows()
        logger.info(f"ScreeningQuestionBank initialized with {len(self.questions)} questions.")

    def load_dataset(self) -> None:
        """Load question definitions from JSON file."""
        if not os.path.exists(self.dataset_path):
            logger.warning(f"Dataset path {self.dataset_path} does not exist.")
            return

        with open(self.dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_questions = data.get("questions", [])
        for item in raw_questions:
            try:
                q = ScreeningQuestion(**item)
                self.questions[q.id] = q
            except Exception as e:
                logger.error(f"Error parsing question {item.get('id')}: {e}")

    def load_category_mapping(self) -> None:
        """Load category taxonomy metadata."""
        if os.path.exists(self.category_mapping_path):
            with open(self.category_mapping_path, "r", encoding="utf-8") as f:
                self.category_taxonomy = json.load(f).get("categories", {})

    def load_conversation_flows(self) -> None:
        """Load conversation flow templates."""
        if os.path.exists(self.conversation_flow_path):
            with open(self.conversation_flow_path, "r", encoding="utf-8") as f:
                self.conversation_flows = json.load(f)

    def get_question_by_id(self, question_id: str) -> Optional[ScreeningQuestion]:
        """Retrieve question object by ID."""
        return self.questions.get(question_id)

    def filter_questions(
        self,
        role: Optional[str] = None,
        category: Optional[Union[str, QuestionCategory]] = None,
        mandatory_only: bool = False,
        min_importance: Optional[Union[str, ImportanceLevel]] = None,
        include_general: bool = True,
    ) -> List[ScreeningQuestion]:
        """
        Filter question bank by role, category, mandatory status, and importance level.
        """
        results = []
        target_cat = category.value if isinstance(category, QuestionCategory) else category
        target_imp = min_importance.value if isinstance(min_importance, ImportanceLevel) else min_importance

        importance_order = {
            "CRITICAL": 4,
            "HIGH": 3,
            "MEDIUM": 2,
            "LOW": 1,
        }
        min_imp_rank = importance_order.get(str(target_imp).upper(), 0) if target_imp else 0

        for q in self.questions.values():
            # Role matching
            if role:
                norm_role = role.lower()
                q_role = q.role.lower()
                if q_role == "general":
                    if not include_general:
                        continue
                elif q_role not in norm_role and norm_role not in q_role:
                    continue

            # Category matching
            if target_cat and q.category.value.lower() != str(target_cat).lower():
                continue

            # Mandatory filter
            if mandatory_only and not q.is_mandatory:
                continue

            # Importance filter
            if min_imp_rank > 0:
                q_rank = importance_order.get(q.scoring_importance.value, 1)
                if q_rank < min_imp_rank:
                    continue

            results.append(q)

        return results

    def get_questions_for_role(self, role: str) -> Dict[str, List[ScreeningQuestion]]:
        """
        Retrieve all categorized questions relevant for a given job role.
        """
        categorized: Dict[str, List[ScreeningQuestion]] = {
            cat.value: [] for cat in QuestionCategory
        }

        all_role_q = self.filter_questions(role=role)
        for q in all_role_q:
            categorized[q.category.value].append(q)

        return categorized

    def render_question(
        self,
        question_id: str,
        context: Dict[str, Any],
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Render dynamic question template with context variables and language localization.
        """
        q = self.get_question_by_id(question_id)
        if not q:
            raise ValueError(f"Question with ID '{question_id}' not found.")

        rendered_text = q.render(context, lang=language)
        follow_up = q.follow_up_prompt
        if follow_up:
            for key, val in context.items():
                follow_up = follow_up.replace(f"{{{key}}}", str(val))

        return {
            "question_id": q.id,
            "category": q.category.value,
            "role": q.role,
            "language": language,
            "rendered_prompt": rendered_text,
            "expected_answer_type": q.expected_answer_type.value,
            "is_mandatory": q.is_mandatory,
            "scoring_importance": q.scoring_importance.value,
            "follow_up_prompt": follow_up,
            "validation_rules": (
                q.validation_rules.model_dump() if q.validation_rules else None
            ),
        }

    def generate_call_script(
        self,
        candidate_data: Dict[str, Any],
        role_name: str = "Software Engineer",
        job_location: str = "Bangalore",
        language: str = "en",
        bot_name: str = "Zecpath AI Recruiter",
    ) -> ScreeningCallScript:
        """
        Generate an end-to-end conversational call script for an automated AI screening session.
        """
        candidate_name = (
            candidate_data.get("name")
            or candidate_data.get("candidate_name")
            or candidate_data.get("candidate_id")
            or "Candidate"
        )

        context = {
            "candidate_name": candidate_name,
            "role_name": role_name,
            "job_location": job_location,
            "bot_name": bot_name,
            "min_experience": candidate_data.get("min_experience", 2),
        }

        script_items: List[ScreeningCallScriptItem] = []
        stages = self.conversation_flows.get("stages", [])

        for stage in stages:
            stage_id = stage.get("stage_id", "")
            cat_name = stage.get("category", "General")
            q_id = stage.get("question_id")

            if q_id and q_id in self.questions:
                q = self.questions[q_id]
                prompt = q.render(context, lang=language)
                follow_up = q.follow_up_prompt
                if follow_up:
                    for k, v in context.items():
                        follow_up = follow_up.replace(f"{{{k}}}", str(v))

                script_items.append(
                    ScreeningCallScriptItem(
                        stage_id=stage_id,
                        category=q.category.value,
                        question_id=q.id,
                        rendered_prompt=prompt,
                        expected_answer_type=q.expected_answer_type.value,
                        is_mandatory=q.is_mandatory,
                        scoring_importance=q.scoring_importance.value,
                        intent=q.intent,
                        follow_up_prompt=follow_up,
                    )
                )
            elif stage.get("question_selection_strategy") == "role_dynamic":
                # Find best matching technical skill questions for role
                skill_questions = self.filter_questions(
                    role=role_name, category=QuestionCategory.SKILLS
                )
                if not skill_questions:
                    skill_questions = self.filter_questions(
                        role="General", category=QuestionCategory.SKILLS
                    )

                for sq in skill_questions[:2]:
                    prompt = sq.render(context, lang=language)
                    script_items.append(
                        ScreeningCallScriptItem(
                            stage_id=f"{stage_id}_{sq.id}",
                            category=sq.category.value,
                            question_id=sq.id,
                            rendered_prompt=prompt,
                            expected_answer_type=sq.expected_answer_type.value,
                            is_mandatory=sq.is_mandatory,
                            scoring_importance=sq.scoring_importance.value,
                            intent=sq.intent,
                            follow_up_prompt=sq.follow_up_prompt,
                        )
                    )
            else:
                # Custom greeting or closing stage
                raw_prompt = stage.get("bot_prompt", "")
                for k, v in context.items():
                    raw_prompt = raw_prompt.replace(f"{{{k}}}", str(v))

                script_items.append(
                    ScreeningCallScriptItem(
                        stage_id=stage_id,
                        category=cat_name,
                        question_id=None,
                        rendered_prompt=raw_prompt,
                        expected_answer_type="text",
                        is_mandatory=True,
                        scoring_importance="HIGH",
                        intent=stage.get("expected_intent"),
                    )
                )

        closing_statement = (
            f"Thank you so much for your time today, {candidate_name}. "
            "Our recruitment team will review your responses and reach out with next steps. Have a great day!"
        )

        return ScreeningCallScript(
            candidate_name=candidate_name,
            role_name=role_name,
            language=language,
            total_stages=len(script_items),
            estimated_call_duration_minutes=round(len(script_items) * 0.75, 1),
            script_items=script_items,
            closing_statement=closing_statement,
        )

    def get_dataset_summary(self) -> Dict[str, Any]:
        """Return dataset breakdown and metrics."""
        category_counts = {cat.value: 0 for cat in QuestionCategory}
        role_counts: Dict[str, int] = {}
        answer_type_counts: Dict[str, int] = {}
        mandatory_count = 0

        for q in self.questions.values():
            category_counts[q.category.value] = category_counts.get(q.category.value, 0) + 1
            role_counts[q.role] = role_counts.get(q.role, 0) + 1
            answer_type_counts[q.expected_answer_type.value] = (
                answer_type_counts.get(q.expected_answer_type.value, 0) + 1
            )
            if q.is_mandatory:
                mandatory_count += 1

        return {
            "total_questions": len(self.questions),
            "categories_covered": list(category_counts.keys()),
            "category_distribution": category_counts,
            "role_distribution": role_counts,
            "answer_type_distribution": answer_type_counts,
            "mandatory_questions_count": mandatory_count,
            "optional_questions_count": len(self.questions) - mandatory_count,
            "supported_languages": ["en", "hi", "ml", "ta"],
        }
