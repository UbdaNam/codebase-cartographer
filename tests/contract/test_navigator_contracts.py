from src.models.enums import AnalysisMethod
from src.models.navigator import NavigatorAnswerItem, NavigatorCitation, NavigatorRequest, NavigatorResponse


def test_navigator_response_contract_serializes_required_fields() -> None:
    response = NavigatorResponse(
        request=NavigatorRequest(query_type="explain_module", query_text="Explain app/ingestion.py"),
        summary="Module explanation.",
        results=[
            NavigatorAnswerItem(
                title="app/ingestion.py",
                answer_text="Loads orders.",
                citations=[
                    NavigatorCitation(
                        source_file="app/ingestion.py",
                        line_start=1,
                        line_end=4,
                        analysis_method=AnalysisMethod.STATIC_ANALYSIS,
                        trust_label="static_analysis",
                        artifact_reference="module_semantics.json",
                    )
                ],
                observed_facts=["Path exists."],
                inferred_notes=["Purpose statement is evidence-backed."],
            )
        ],
        partial_result_flags=[],
        trace_event_ids=["trace_event:123"],
        used_model_synthesis=False,
    )

    payload = response.model_dump(mode="json")

    assert payload["request"]["query_type"] == "explain_module"
    assert payload["results"][0]["citations"][0]["source_file"] == "app/ingestion.py"
    assert payload["results"][0]["citations"][0]["analysis_method"] == "static_analysis"
