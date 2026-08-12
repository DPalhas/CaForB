from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from core.models import Company, QuestionnaireResponse, InnovationInsight, LLMTrace
from core.services.memory import build_assessment_history, build_score_trend
from core.services.llm_services import (
    build_innovation_prompt, _extract_json, _estimate_budget, DEFAULT_MODEL
)


class MemoryServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass"
        )
        self.company = Company.objects.create(
            name="TestCorp", sector="Technology & IT",
            size="Medium", user=self.user
        )

    def test_build_score_trend_empty(self):
        trend = build_score_trend(self.company)
        self.assertEqual(trend["trend"], "stable")
        self.assertEqual(trend["assessment_count"], 0)
        self.assertEqual(trend["latest_score"], None)

    def test_build_score_trend_single(self):
        qr = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=1, answers={}
        )
        InnovationInsight.objects.create(
            response=qr, raw_prompt="", ai_output="",
            innovation_score=3.5, context_bundle={}
        )
        trend = build_score_trend(self.company)
        self.assertEqual(trend["assessment_count"], 1)
        self.assertEqual(trend["latest_score"], 3.5)
        self.assertEqual(trend["trend"], "stable")
        self.assertEqual(trend["delta"], 0)

    def test_build_score_trend_improving(self):
        qr1 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=1, answers={}
        )
        InnovationInsight.objects.create(
            response=qr1, raw_prompt="", ai_output="",
            innovation_score=3.5, context_bundle={}
        )
        qr2 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=2, answers={}
        )
        InnovationInsight.objects.create(
            response=qr2, raw_prompt="", ai_output="",
            innovation_score=5.0, context_bundle={}
        )
        trend = build_score_trend(self.company)
        self.assertEqual(trend["assessment_count"], 2)
        self.assertEqual(trend["trend"], "improving")
        self.assertAlmostEqual(trend["delta"], 1.5)

    def test_build_score_trend_declining(self):
        qr1 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=1, answers={}
        )
        InnovationInsight.objects.create(
            response=qr1, raw_prompt="", ai_output="",
            innovation_score=7.0, context_bundle={}
        )
        qr2 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=2, answers={}
        )
        InnovationInsight.objects.create(
            response=qr2, raw_prompt="", ai_output="",
            innovation_score=5.5, context_bundle={}
        )
        trend = build_score_trend(self.company)
        self.assertEqual(trend["trend"], "declining")
        self.assertAlmostEqual(trend["delta"], -1.5)

    def test_build_assessment_history_empty(self):
        result = build_assessment_history(self.company)
        self.assertEqual(result, "")

    def test_build_assessment_history_with_prior(self):
        qr = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=1,
            answers={"companyDescription": "A tech company"},
            period_label="Q1 2026", changes_since_last="Nada mudou",
            recommendation_status={"opp_1": "completed"}
        )
        insight = InnovationInsight.objects.create(
            response=qr, raw_prompt="test", ai_output="{}",
            innovation_score=5.5, context_bundle={
                "opportunities": [
                    {"id": "opp_1", "type": "incremental",
                     "title": "Adopt CRM", "rationale": "...",
                     "impact": "medium", "difficulty": "low",
                     "timeframe": "3-6 months",
                     "execution_plan": {"first_actions": ["..."],
                                        "resources_needed": ["..."],
                                        "success_metric": "Reduce time 40%",
                                        "milestones": ["Week 2: pilot"]}}
                ],
                "next_steps": [
                    {"id": "step_1", "action": "Assign CRM lead",
                     "owner": "CTO", "timeframe": "2 weeks"}
                ],
                "key_weaknesses": ["No formal innovation process"]
            }
        )
        result = build_assessment_history(self.company)
        self.assertIn("PRIOR ASSESSMENT SUMMARY", result)
        self.assertIn("Adopt CRM", result)
        self.assertIn("COMPLETED", result)
        self.assertIn("Key Weaknesses", result)


class PromptBuilderTests(TestCase):
    def setUp(self):
        self.company = {"name": "Foo Inc", "sector": "Fintech", "size": "Small"}
        self.answers = {
            "companyDescription": "A fintech startup",
            "regulatoryEnvironment": "high",
            "competitivePressure": "medium",
            "riskAppetite": "conservative",
            "strategicPriority": "growth",
            "decisionMaking": "owner_alone",
            "customerFeedback": "surveys_nps",
            "budgetPercentage": 5,
            "revenueRange": "1m_to_10m",
        }

    def test_first_assessment_prompt_no_history(self):
        prompt = build_innovation_prompt(self.company, self.answers)
        self.assertIn("strategic innovation advisor", prompt)
        self.assertIn("maturity_score", prompt)
        self.assertIn("Foo Inc", prompt)
        self.assertIn("REASSESSMENT", prompt)  # the JSON schema always mentions "reassessment" as it's in the opportunities type field hints

    def test_reassessment_prompt_with_history(self):
        history = "PRIOR ASSESSMENT SUMMARY"
        prompt = build_innovation_prompt(self.company, self.answers,
                                         history=history)
        self.assertIn("PRIOR ASSESSMENT SUMMARY", prompt)
        self.assertIn("REASSESSMENT DIRECTIVES", prompt)
        self.assertIn("carry_forward_from", prompt)
        self.assertIn("score_delta", prompt)
        self.assertIn("comparison_to_previous", prompt)

    def test_first_assessment_no_carry_forward(self):
        prompt = build_innovation_prompt(self.company, self.answers)
        self.assertNotIn("carry_forward_from", prompt)
        self.assertNotIn("REASSESSMENT DIRECTIVES", prompt)


class JsonExtractionTests(TestCase):
    def test_extract_clean_json(self):
        result = _extract_json('{"maturity_score": 5.5, "opportunities": []}')
        self.assertEqual(result["maturity_score"], 5.5)

    def test_extract_json_with_markdown(self):
        result = _extract_json('```json\n{"a": 1}\n```')
        self.assertEqual(result, {})

    def test_extract_json_embedded(self):
        result = _extract_json('Some text {"key": "value"} more text')
        self.assertEqual(result["key"], "value")

    def test_extract_unparseable(self):
        result = _extract_json("not json at all")
        self.assertEqual(result, {})

    def test_extract_unclosed_array(self):
        result = _extract_json('{"items": ["a", "b"')
        self.assertEqual(result, {"items": ["a", "b"]})


class BudgetEstimationTests(TestCase):
    def test_valid_budget(self):
        result = _estimate_budget({
            "budgetPercentage": 10, "revenueRange": "1m_to_10m"
        })
        self.assertIn("550,000", result)

    def test_missing_percentage(self):
        result = _estimate_budget({"budgetPercentage": None, "revenueRange": "1m_to_10m"})
        self.assertEqual(result, "unknown")

    def test_missing_range(self):
        result = _estimate_budget({"budgetPercentage": 10})
        self.assertEqual(result, "unknown")

    def test_unknown_range(self):
        result = _estimate_budget({
            "budgetPercentage": 10, "revenueRange": "unknown_key"
        })
        self.assertEqual(result, "10% of revenue")


class AgentLoopTests(TestCase):
    @patch("core.services.llm_services.ollama.chat")
    def test_agent_loop_first_assessment(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": '{"maturity_score": 5.5, "opportunities": [], "next_steps": [], "key_weaknesses": []}'}
        }
        from core.services.llm_services import generate_innovation_insight

        traces = []
        def cb(step, inp, out, dur):
            traces.append((step, dur))

        raw, dur = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            trace_cb=cb
        )
        self.assertIn("5.5", raw)
        steps = [t[0] for t in traces]
        self.assertIn("resolve_context", steps)
        self.assertIn("build_prompt", steps)
        self.assertIn("llm_inference", steps)

    @patch("core.services.llm_services.ollama.chat")
    def test_agent_loop_reassessment(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": '{"maturity_score": 6.0, "score_delta": 0.5, "opportunities": [], "next_steps": [], "key_weaknesses": []}'}
        }
        from core.services.llm_services import generate_innovation_insight

        traces = []
        def cb(step, inp, out, dur):
            traces.append(step)

        history = "PRIOR ASSESSMENT SUMMARY\n..."
        raw, dur = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            history=history,
            trace_cb=cb
        )
        steps = traces
        self.assertIn("resolve_context", steps)
        self.assertIn("build_prompt", steps)
        self.assertIn("llm_inference", steps)

    @patch("core.services.llm_services.ollama.chat")
    def test_generate_uses_correct_model(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": '{"maturity_score": 5.0, "opportunities": [], "next_steps": [], "key_weaknesses": []}'}
        }
        from core.services.llm_services import generate_innovation_insight

        generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            model="caforb-v2"
        )
        mock_ollama.assert_called_once_with(
            model="caforb-v2",
            messages=[{"role": "user", "content": mock_ollama.call_args[1]["messages"][0]["content"]}]
        )


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="muser", email="m@t.com", password="pass"
        )

    def test_company_created_with_user(self):
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        self.assertEqual(company.user, self.user)
        self.assertIsNotNone(company.created_at)

    def test_questionnaire_response_assessment_number(self):
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        qr = QuestionnaireResponse.objects.create(
            company=company, assessment_number=2, answers={}
        )
        self.assertEqual(qr.assessment_number, 2)
        self.assertEqual(qr.period_label, "")
        self.assertEqual(qr.changes_since_last, "")
        self.assertEqual(qr.recommendation_status, {})

    def test_innovation_insight_previous_chain(self):
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        qr1 = QuestionnaireResponse.objects.create(
            company=company, assessment_number=1, answers={}
        )
        ins1 = InnovationInsight.objects.create(
            response=qr1, raw_prompt="", ai_output="",
            innovation_score=4.0, context_bundle={}, model_name="gemma4"
        )
        qr2 = QuestionnaireResponse.objects.create(
            company=company, assessment_number=2, answers={},
            changes_since_last="Hired 5 engineers",
            recommendation_status={"opp_1": "completed"}
        )
        ins2 = InnovationInsight.objects.create(
            response=qr2, previous_insight=ins1,
            raw_prompt="", ai_output="",
            innovation_score=5.0, score_delta=1.0,
            context_bundle={}, model_name="caforb-v2"
        )
        self.assertEqual(ins2.previous_insight, ins1)
        self.assertEqual(ins2.score_delta, 1.0)
        self.assertEqual(ins2.model_name, "caforb-v2")

    def test_llm_trace_model_name(self):
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        qr = QuestionnaireResponse.objects.create(
            company=company, assessment_number=1, answers={}
        )
        ins = InnovationInsight.objects.create(
            response=qr, raw_prompt="", ai_output="",
            innovation_score=4.0, context_bundle={}
        )
        trace = LLMTrace.objects.create(
            insight=ins, step_name="synthesize", model_name="gemma4",
            input_payload={"a": 1}, output_payload={"b": 2}, duration_ms=1500
        )
        self.assertEqual(trace.step_name, "synthesize")
        self.assertEqual(trace.model_name, "gemma4")
        self.assertEqual(trace.duration_ms, 1500)
