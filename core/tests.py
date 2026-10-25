from django.test import TestCase
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock

from core.models import (
    Company,
    QuestionnaireResponse,
    InnovationInsight,
    LLMTrace,
    ChatSession,
    ChatMessage,
)
from core.services.memory import build_assessment_history, build_score_trend
from core.services.llm_services import (
    build_innovation_prompt,
    _extract_json,
    _estimate_budget,
    _structure_valid,
    DEFAULT_MODEL,
    build_chat_system_prompt,
    chat_with_insight,
    CHAT_MODEL,
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
            innovation_score=3.5, context_bundle={}, is_selected=True
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
            innovation_score=3.5, context_bundle={}, is_selected=True
        )
        qr2 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=2, answers={}
        )
        InnovationInsight.objects.create(
            response=qr2, raw_prompt="", ai_output="",
            innovation_score=5.0, context_bundle={}, is_selected=True
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
            innovation_score=7.0, context_bundle={}, is_selected=True
        )
        qr2 = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=2, answers={}
        )
        InnovationInsight.objects.create(
            response=qr2, raw_prompt="", ai_output="",
            innovation_score=5.5, context_bundle={}, is_selected=True
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
            innovation_score=5.5, is_selected=True, context_bundle={
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
        system, user = build_innovation_prompt(self.company, self.answers)
        self.assertIn("strategic innovation advisor", system)
        self.assertIn("maturity_score", system)
        self.assertIn("Foo Inc", user)
        self.assertNotIn("REASSESSMENT DIRECTIVES", system)

    def test_reassessment_prompt_with_history(self):
        history = "PRIOR ASSESSMENT SUMMARY"
        system, user = build_innovation_prompt(self.company, self.answers,
                                               history=history)
        self.assertIn("PRIOR ASSESSMENT SUMMARY", user)
        self.assertIn("REASSESSMENT DIRECTIVES", system)
        self.assertIn("carry_forward_from", system)
        self.assertIn("score_delta", system)
        self.assertIn("comparison_to_previous", system)

    def test_first_assessment_no_carry_forward(self):
        system, user = build_innovation_prompt(self.company, self.answers)
        self.assertNotIn("carry_forward_from", system)
        self.assertNotIn("REASSESSMENT DIRECTIVES", system)

    def test_snake_case_answers_are_normalized(self):
        # The frontend sends a mix of snake_case and camelCase keys.
        answers = {
            "company_description": "A fintech startup",
            "innovation_process": "partial",
            "customer_feedback": "surveys_nps",
            "strategic_goals": "Double revenue in 2 years",
            "time_horizon": "long",
            "team_size": "12 engineers",
            "digital_maturity": "3",
            "decision_making": "owner_alone",
            "main_barrier": ["budget", "talent"],
            "past_initiatives": "Launched a mobile app",
            "additional_context": "New competitor entered",
            "budgetPercentage": 5,
            "revenueRange": "1m_to_10m",
            "regulatoryEnvironment": "high",
            "riskAppetite": "conservative",
            "strategicPriority": "growth",
            "competitivePressure": "medium",
        }
        system, user = build_innovation_prompt(self.company, answers)
        # snake_case values must surface in the clean user block (not defaults)
        self.assertIn("A fintech startup", user)
        self.assertIn("Double revenue in 2 years", user)
        self.assertIn("12 engineers", user)
        self.assertIn("Launched a mobile app", user)
        self.assertIn("New competitor entered", user)
        # budget (camelCase already) still resolved
        self.assertIn("€", user)


class JsonExtractionTests(TestCase):
    def test_extract_clean_json(self):
        result = _extract_json('{"maturity_score": 5.5, "opportunities": []}')
        self.assertEqual(result["maturity_score"], 5.5)

    def test_extract_json_with_markdown(self):
        result = _extract_json('```json\n{"a": 1}\n```')
        self.assertEqual(result, {"a": 1})

    def test_extract_json_embedded(self):
        result = _extract_json('Some text {"key": "value"} more text')
        self.assertEqual(result["key"], "value")

    def test_extract_unparseable(self):
        result = _extract_json("not json at all")
        self.assertEqual(result, {})

    def test_extract_unclosed_array(self):
        result = _extract_json('{"items": ["a", "b"')
        self.assertEqual(result, {"items": ["a", "b"]})

    def test_extract_truncated_with_trailing_comma(self):
        result = _extract_json('{"items": ["a", "b", ')
        self.assertEqual(result, {"items": ["a", "b"]})

    def test_extract_truncated_mid_object(self):
        result = _extract_json('{"a": {"b": 1,')
        self.assertEqual(result, {"a": {"b": 1}})

    def test_extract_newline_inside_string(self):
        raw = '{"type": "incremental\n", "title": "T", "n": 1}'
        result = _extract_json(raw)
        self.assertEqual(result["type"], "incremental ")
        self.assertEqual(result["title"], "T")

    def test_extract_tab_inside_string(self):
        raw = '{"action": "do\tthis", "owner": "O"}'
        result = _extract_json(raw)
        self.assertEqual(result["action"], "do this")


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


class StructureValidationTests(TestCase):
    def _opp(self, first_actions, milestones):
        return {
            "type": "incremental",
            "execution_plan": {
                "first_actions": first_actions,
                "resources_needed": ["€5,000 one-off"],
                "success_metric": "Reduce churn by 5%",
                "milestones": milestones,
            },
        }

    def test_valid_structure(self):
        ok, _ = _structure_valid({
            "opportunities": [self._opp(["A"], ["Month 1: B"])]
        })
        self.assertTrue(ok)

    def test_rejects_duplicated_milestones(self):
        ok, reason = _structure_valid({
            "opportunities": [self._opp(["A", "B"], ["A", "B"])]
        })
        self.assertFalse(ok)
        self.assertIn("duplicate", reason)


class AgentLoopTests(TestCase):
    @patch("core.services.llm_services.ollama.chat")
    def test_agent_loop_first_assessment(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": (
                '{"maturity_score": 5.5, '
                '"opportunities": [{"id": "o1", "type": "incremental", '
                '"title": "T", "rationale": "R", "impact": "medium", '
                '"difficulty": "low", "timeframe": "3 months", '
                '"execution_plan": {"first_actions": ["A"], '
                '"resources_needed": ["B"], "success_metric": "S", '
                '"milestones": ["M"]}}], '
                '"next_steps": [], "key_weaknesses": []}'
            )}
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
            "message": {"content": (
                '{"maturity_score": 6.0, "score_delta": 0.5, '
                '"score_change": "improved", '
                '"opportunities": [{"id": "opp_1", "type": "incremental", '
                '"title": "Adopt CRM", "rationale": "R", "impact": "high", '
                '"execution_plan": {"first_actions": ["A"], '
                '"resources_needed": ["B"], "success_metric": "S", '
                '"milestones": ["M"]}, '
                '"difficulty": "low", "timeframe": "3 months"}], '
                '"next_steps": [{"id": "s1", "action": "A", "owner": "O", '
                '"timeframe": "2 weeks"}], '
                '"key_weaknesses": ["No process"], '
                '"progress": {"improvements": [], "persistent_gaps": [], '
                '"achieved_milestones": []}, '
                '"comparison_to_previous": {"previous_score": 5.5}}'
            )}
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
        self.assertIn("6.0", raw)
        self.assertIn("Adopt CRM", raw)

    @patch("core.services.llm_services.ollama.chat")
    def test_reassessment_single_call(self, mock_ollama):
        good = {"message": {"content": (
            '{"maturity_score": 5.0, "score_delta": 0.1, '
            '"score_change": "improved", '
            '"opportunities": [{"id": "o1", "type": "incremental", '
            '"title": "T", "impact": "medium", "difficulty": "low", '
            '"execution_plan": {"first_actions": ["A"], '
            '"resources_needed": ["B"], "success_metric": "S", '
            '"milestones": ["M"]}, '
            '"timeframe": "3 months"}], '
            '"next_steps": [], "key_weaknesses": [], '
            '"progress": {}, "comparison_to_previous": {}}'
        )}}
        mock_ollama.return_value = good
        from core.services.llm_services import generate_innovation_insight

        raw, _ = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            history="PRIOR ASSESSMENT SUMMARY\n...",
        )
        self.assertIn("5.0", raw)
        self.assertEqual(mock_ollama.call_count, 1)

    @patch("core.services.llm_services.ollama.chat")
    def test_reassessment_returns_raw_unparseable(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": "I cannot produce valid JSON here {broken"}
        }
        from core.services.llm_services import generate_innovation_insight

        raw, _ = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            history="PRIOR ASSESSMENT SUMMARY\n...",
        )
        self.assertEqual(raw, "I cannot produce valid JSON here {broken")
        self.assertEqual(mock_ollama.call_count, 3)

    @patch("core.services.llm_services.ollama.chat")
    def test_generate_uses_correct_model(self, mock_ollama):
        mock_ollama.return_value = {
            "message": {"content": (
                '{"maturity_score": 5.0, '
                '"opportunities": [{"id": "o1", "type": "incremental", '
                '"title": "T", "rationale": "R", "impact": "medium", '
                '"difficulty": "low", "timeframe": "3 months", '
                '"execution_plan": {"first_actions": ["A"], '
                '"resources_needed": ["B"], "success_metric": "S", '
                '"milestones": ["M"]}}], '
                '"next_steps": [], "key_weaknesses": []}'
            )}
        }
        from core.services.llm_services import generate_innovation_insight

        generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
            model="caforb-v2"
        )
        mock_ollama.assert_called_once_with(
            model="caforb-v2",
            messages=[
                {"role": "system", "content": mock_ollama.call_args[1]["messages"][0]["content"]},
                {"role": "user", "content": mock_ollama.call_args[1]["messages"][1]["content"]},
            ],
            think=False,
            options={"num_predict": 16384, "temperature": 0.3, "num_ctx": 8192}
        )

    @patch("core.services.llm_services.ollama.chat")
    def test_retry_on_empty_response(self, mock_ollama):
        empty = {"message": {"content": ""}}
        good = {"message": {"content": (
            '{"maturity_score": 5.0, '
            '"opportunities": [{"id": "o1", "type": "incremental", '
            '"title": "T", "rationale": "R", "impact": "medium", '
            '"difficulty": "low", "timeframe": "3 months", '
            '"execution_plan": {"first_actions": ["A"], '
            '"resources_needed": ["B"], "success_metric": "S", '
            '"milestones": ["M"]}}], '
            '"next_steps": [], "key_weaknesses": []}'
        )}}
        mock_ollama.side_effect = [empty, good]
        from core.services.llm_services import generate_innovation_insight

        raw, _ = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
        )
        self.assertIn("5.0", raw)
        self.assertEqual(mock_ollama.call_count, 2)

    @patch("core.services.llm_services.ollama.chat")
    def test_retry_on_unparseable_then_success(self, mock_ollama):
        bad = {"message": {"content": "not valid json {broken"}}
        good = {"message": {"content": (
            '{"maturity_score": 5.0, '
            '"opportunities": [{"id": "o1", "type": "incremental", '
            '"title": "T", "rationale": "R", "impact": "medium", '
            '"difficulty": "low", "timeframe": "3 months", '
            '"execution_plan": {"first_actions": ["A"], '
            '"resources_needed": ["B"], "success_metric": "S", '
            '"milestones": ["M"]}}], '
            '"next_steps": [], "key_weaknesses": []}'
        )}}
        mock_ollama.side_effect = [bad, good]
        from core.services.llm_services import generate_innovation_insight

        raw, _ = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
        )
        self.assertIn("5.0", raw)
        self.assertEqual(mock_ollama.call_count, 2)

    @patch("core.services.llm_services.ollama.chat")
    def test_retry_exhausts_to_raw_text(self, mock_ollama):
        always_bad = {"message": {"content": "not valid json {broken"}}
        mock_ollama.return_value = always_bad
        from core.services.llm_services import generate_innovation_insight

        raw, _ = generate_innovation_insight(
            {"name": "Test", "sector": "Tech", "size": "Small"},
            {"companyDescription": "desc"},
        )
        self.assertEqual(mock_ollama.call_count, 3)
        self.assertEqual(raw, "not valid json {broken")


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

    def test_insight_to_type_tolerates_execution_plan_key_typo(self):
        from core.schema import _insight_to_type
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        qr = QuestionnaireResponse.objects.create(
            company=company, assessment_number=1, answers={}
        )
        ins = InnovationInsight.objects.create(
            response=qr, raw_prompt="", ai_output="",
            innovation_score=5.0,
            context_bundle={
                "opportunities": [{
                    "id": "opp_2", "title": "Brand Expansion",
                    "execution_4_plan": {
                        "first_actions": ["A1"],
                        "resources_needed": ["R1"],
                        "success_metric": "S1",
                        "milestones": ["M1"],
                    },
                }],
                "next_steps": [],
                "key_weaknesses": [],
            },
        )
        result = _insight_to_type(ins)
        self.assertIsNotNone(result.opportunities[0].execution_plan)
        self.assertEqual(result.opportunities[0].execution_plan.milestones, ["M1"])

    def test_insight_to_type_tolerates_execution_rf_key(self):
        from core.schema import _insight_to_type
        company = Company.objects.create(
            name="ACME", sector="Retail", size="Large", user=self.user
        )
        qr = QuestionnaireResponse.objects.create(
            company=company, assessment_number=1, answers={}
        )
        ins = InnovationInsight.objects.create(
            response=qr, raw_prompt="", ai_output="",
            innovation_score=5.0,
            context_bundle={
                "opportunities": [{
                    "id": "opp_2", "type": "radical", "title": "Expansion",
                    "execution_rf": {
                        "first_actions": ["A1"],
                        "resources_needed": ["R1"],
                        "success_metric": "S1",
                        "milestones": ["M1"],
                    },
                }],
                "next_steps": [],
                "key_weaknesses": [],
            },
        )
        result = _insight_to_type(ins)
        self.assertIsNotNone(result.opportunities[0].execution_plan)
        self.assertEqual(result.opportunities[0].execution_plan.first_actions, ["A1"])
        self.assertEqual(result.opportunities[0].type, "radical")


class ChatServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cuser", email="c@t.com", password="pass"
        )
        self.company = Company.objects.create(
            name="ChatCorp", sector="Retail", size="Small", user=self.user
        )
        qr = QuestionnaireResponse.objects.create(
            company=self.company, assessment_number=1, answers={}
        )
        self.insight = InnovationInsight.objects.create(
            response=qr, raw_prompt="", ai_output="{}",
            innovation_score=6.5, score_delta=None,
            context_bundle={
                "opportunities": [
                    {"id": "opp_1", "type": "incremental", "title": "Adopt CRM",
                     "rationale": "...", "impact": "medium", "difficulty": "low",
                     "timeframe": "3-6 months",
                     "execution_plan": {"first_actions": ["A"],
                                        "resources_needed": ["R"],
                                        "success_metric": "S",
                                        "milestones": ["M"]}}
                ],
                "next_steps": [
                    {"id": "step_1", "action": "Assign lead", "owner": "CTO",
                     "timeframe": "2 weeks"}
                ],
                "key_weaknesses": ["No process"],
            }
        )

    def test_build_chat_system_prompt_includes_context(self):
        prompt = build_chat_system_prompt(self.insight)
        self.assertIn("ChatCorp", prompt)
        self.assertIn("Adopt CRM", prompt)
        self.assertIn("6.5", prompt)
        self.assertIn("Assign lead", prompt)

    def test_build_chat_system_prompt_has_refusal_rules(self):
        prompt = build_chat_system_prompt(self.insight)
        self.assertIn("SCOPE AND REFUSAL RULES", prompt)
        self.assertIn("You are NOT a general-purpose assistant", prompt)
        self.assertIn("Do NOT answer the off-topic request", prompt)

    def test_build_chat_system_prompt_tagged_opportunity(self):
        prompt = build_chat_system_prompt(
            self.insight, tagged_opportunity_id="opp_1"
        )
        self.assertIn("selected this specific opportunity", prompt)
        self.assertIn("Adopt CRM", prompt)

    def test_build_chat_system_prompt_tagged_weakness(self):
        prompt = build_chat_system_prompt(
            self.insight, tagged_weakness="No process"
        )
        self.assertIn("selected this specific vulnerability", prompt)
        self.assertIn("No process", prompt)

    @patch("core.services.llm_services.ollama.chat")
    def test_chat_with_insight_calls_model(self, mock_chat):
        mock_chat.return_value = {"message": {"content": "Here's why..."}}
        history = [{"role": "user", "content": "hello"}]
        result = chat_with_insight(
            self.insight, history, "Tell me about opp_1",
            tagged_opportunity_id="opp_1", model="test-chat"
        )
        self.assertEqual(result, "Here's why...")
        kwargs = mock_chat.call_args[1]
        self.assertEqual(kwargs["model"], "test-chat")
        messages = kwargs["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("Adopt CRM", messages[0]["content"])
        self.assertEqual(messages[-1]["content"], "Tell me about opp_1")

    def test_chat_session_and_message_persistence(self):
        session = ChatSession.objects.create(insight=self.insight)
        msg = ChatMessage.objects.create(
            session=session, role="user", content="hi",
            tagged_opportunity_id="opp_1"
        )
        self.assertEqual(session.insight, self.insight)
        self.assertEqual(msg.tagged_opportunity_id, "opp_1")
        self.assertEqual(list(session.messages.all()), [msg])

    @patch("core.services.llm_services.ollama.chat")
    def test_ask_insight_mutation_persists_and_returns(self, mock_chat):
        from core.schema import schema
        from django.test import RequestFactory

        mock_chat.return_value = {"message": {"content": "Answer text"}}

        class FakeContext:
            def __init__(self, request):
                self.request = request

        request = RequestFactory().post("/graphql/")
        request.user = self.user

        result = schema.execute_sync(
            f'mutation {{ askInsight(insightId: {self.insight.id}, '
            f'message: "Why?", taggedOpportunityId: "opp_1") '
            '{ id role content taggedOpportunityId } }',
            context_value=FakeContext(request),
        )
        self.assertIsNone(result.errors, getattr(result, "errors", None))
        data = result.data["askInsight"]
        self.assertEqual(data["role"], "assistant")
        self.assertEqual(data["content"], "Answer text")
        self.assertEqual(data["taggedOpportunityId"], "opp_1")

        session = ChatSession.objects.get(insight=self.insight)
        msgs = list(session.messages.all())
        self.assertEqual(msgs[0].role, "user")
        self.assertEqual(msgs[1].role, "assistant")
        self.assertEqual(msgs[1].model_name, CHAT_MODEL)

    @patch("core.services.llm_services.ollama.chat")
    def test_ask_insight_mutation_tagged_weakness(self, mock_chat):
        from core.schema import schema
        from django.test import RequestFactory

        mock_chat.return_value = {"message": {"content": "Answer text"}}

        class FakeContext:
            def __init__(self, request):
                self.request = request

        request = RequestFactory().post("/graphql/")
        request.user = self.user

        result = schema.execute_sync(
            f'mutation {{ askInsight(insightId: {self.insight.id}, '
            f'message: "Why?", taggedWeakness: "No process") '
            '{ id taggedWeakness } }',
            context_value=FakeContext(request),
        )
        self.assertIsNone(result.errors, getattr(result, "errors", None))
        self.assertEqual(result.data["askInsight"]["taggedWeakness"], "No process")

        session = ChatSession.objects.get(insight=self.insight)
        msgs = list(session.messages.all())
        self.assertEqual(msgs[0].tagged_weakness, "No process")
        self.assertEqual(msgs[1].tagged_weakness, "No process")

    @patch("core.services.llm_services.ollama.chat")
    def test_ask_insight_rejects_other_users_insight(self, mock_chat):
        from core.schema import schema
        from django.test import RequestFactory

        other = User.objects.create_user(
            username="other", email="o@t.com", password="pass"
        )

        class FakeContext:
            def __init__(self, request):
                self.request = request

        request = RequestFactory().post("/graphql/")
        request.user = other

        result = schema.execute_sync(
            f'mutation {{ askInsight(insightId: {self.insight.id}, '
            f'message: "Why?") {{ id }} }}',
            context_value=FakeContext(request),
        )
        self.assertIsNotNone(result.errors)
        self.assertFalse(mock_chat.called)
