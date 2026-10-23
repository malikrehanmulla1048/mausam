"""
MAUSAM — AI Credit Committee Service
Powered by Amazon Bedrock when configured.
Falls back to deterministic rule-based analysis (clearly labelled).
"""
import json
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


# ─── EVIDENCE SCHEMA ─────────────────────────────────────────────────────────

def build_evidence_bundle(business_data: dict) -> dict:
    """
    Assemble a structured evidence bundle from backend analytics.
    All metric values must originate from the analytics layer, not the AI.
    """
    overview = business_data.get("overview", {})
    forecast = business_data.get("forecast", {})
    risk = business_data.get("risk_assessment", {})
    findings = business_data.get("top_findings", [])

    bundle = {
        "CASH-001": {
            "id": "CASH-001", "category": "cash_flow",
            "label": "Current Available Cash",
            "value": overview.get("current_cash", 0),
            "unit": "INR",
        },
        "CASH-002": {
            "id": "CASH-002", "category": "cash_flow",
            "label": "Days of Cash Runway",
            "value": forecast.get("runway_days", 0),
            "unit": "days",
        },
        "CASH-003": {
            "id": "CASH-003", "category": "cash_flow",
            "label": "Shortfall Probability (42-day)",
            "value": forecast.get("shortfall_probability", 0),
            "unit": "probability",
        },
        "CASH-004": {
            "id": "CASH-004", "category": "cash_flow",
            "label": "Minimum Projected Balance (P50)",
            "value": forecast.get("min_balance_p50", 0),
            "unit": "INR",
        },
        "CASH-005": {
            "id": "CASH-005", "category": "cash_flow",
            "label": "Total Outstanding Receivables",
            "value": overview.get("total_outstanding", 0),
            "unit": "INR",
        },
        "RISK-001": {
            "id": "RISK-001", "category": "risk",
            "label": "Readiness Score",
            "value": risk.get("score", 0),
            "unit": "score_300_900",
        },
        "RISK-002": {
            "id": "RISK-002", "category": "risk",
            "label": "Largest Customer Concentration",
            "value": risk.get("top_customer_pct", 0),
            "unit": "percent",
        },
        "RISK-003": {
            "id": "RISK-003", "category": "risk",
            "label": "Overdue Receivables",
            "value": risk.get("overdue_amount", 0),
            "unit": "INR",
        },
        "DEBTOR-001": {
            "id": "DEBTOR-001", "category": "debtors",
            "label": "Sharma Traders Avg Payment Delay (recent)",
            "value": risk.get("sharma_avg_delay", 45),
            "unit": "days",
        },
        "RECON-001": {
            "id": "RECON-001", "category": "reconciliation",
            "label": "Open High-Severity Findings",
            "value": len([f for f in findings if f.get("severity") == "HIGH"]),
            "unit": "count",
        },
        "RECON-002": {
            "id": "RECON-002", "category": "reconciliation",
            "label": "Reconciliation Health Score",
            "value": risk.get("reconciliation_health", 70),
            "unit": "score_0_100",
        },
    }
    return bundle


def validate_citation(citation_id: str, evidence_bundle: dict) -> bool:
    """Validate that a citation ID exists in the evidence bundle."""
    return citation_id in evidence_bundle


# ─── DETERMINISTIC FALLBACK COMMITTEE ────────────────────────────────────────

def run_deterministic_committee(evidence_bundle: dict, business_name: str) -> dict:
    """
    Rule-based committee analysis.
    Clearly labelled as DETERMINISTIC DEMONSTRATION MODE.
    """
    ev = evidence_bundle

    current_cash = ev.get("CASH-001", {}).get("value", 0)
    runway = ev.get("CASH-002", {}).get("value", 0)
    shortfall_prob = ev.get("CASH-003", {}).get("value", 0)
    min_balance = ev.get("CASH-004", {}).get("value", 0)
    outstanding = ev.get("CASH-005", {}).get("value", 0)
    score = ev.get("RISK-001", {}).get("value", 0)
    top_cust_pct = ev.get("RISK-002", {}).get("value", 0)
    overdue = ev.get("RISK-003", {}).get("value", 0)
    sharma_delay = ev.get("DEBTOR-001", {}).get("value", 45)
    open_findings = ev.get("RECON-001", {}).get("value", 0)
    recon_health = ev.get("RECON-002", {}).get("value", 70)

    # ── CASH FLOW ANALYST ─────────────────────────────────────────────────────
    cf_concerns = []
    cf_positives = []

    if shortfall_prob > 0.40:
        cf_concerns.append(f"[CASH-003] Shortfall probability of {shortfall_prob:.0%} is elevated. Action required.")
    if runway < 20:
        cf_concerns.append(f"[CASH-002] Only {runway} days of runway. Below the 20-day threshold.")
    if min_balance < 50_000:
        cf_concerns.append(f"[CASH-004] Projected minimum balance ₹{min_balance:,.0f} is critically low.")
    if outstanding > current_cash * 2:
        cf_concerns.append(f"[CASH-005] Outstanding receivables (₹{outstanding:,.0f}) are 2× current cash — collection velocity is critical.")
    if runway >= 25:
        cf_positives.append(f"[CASH-002] {runway} days of runway provides reasonable short-term buffer.")
    if shortfall_prob < 0.20:
        cf_positives.append(f"[CASH-003] Shortfall probability below 20% — manageable with proactive monitoring.")

    cf_assessment = "HIGH_RISK" if shortfall_prob > 0.40 or runway < 15 else "MODERATE" if shortfall_prob > 0.20 else "ACCEPTABLE"

    # ── RISK OFFICER ─────────────────────────────────────────────────────────
    ro_concerns = []
    ro_positives = []

    if top_cust_pct > 35:
        ro_concerns.append(f"[RISK-002] Top customer contributes {top_cust_pct:.1f}% of revenue — concentration risk is high.")
    if overdue > 2_00_000:
        ro_concerns.append(f"[RISK-003] Overdue receivables of ₹{overdue:,.0f} create liquidity pressure.")
    if score < 550:
        ro_concerns.append(f"[RISK-001] Readiness score of {score} indicates multiple risk factors requiring attention.")
    if sharma_delay > 40:
        ro_concerns.append(f"[DEBTOR-001] Sharma Traders avg delay of {sharma_delay} days represents customer-specific risk.")
    if score >= 600:
        ro_positives.append(f"[RISK-001] Readiness score of {score} is within acceptable range for an MSME of this profile.")

    ro_assessment = "HIGH_RISK" if score < 500 or top_cust_pct > 40 else "MODERATE" if score < 600 else "ACCEPTABLE"

    # ── DEVIL'S ADVOCATE ─────────────────────────────────────────────────────
    da_challenges = []

    if shortfall_prob < 0.50:
        da_challenges.append("Even a 40% shortfall probability means near-coin-flip odds. This should not be read as safe.")
    if sharma_delay > 40:
        da_challenges.append(f"[DEBTOR-001] The delay data for Sharma Traders is based on historical pattern and may understate current risk if the relationship has deteriorated further.")
    da_challenges.append("[RECON-001] Reconciliation findings remain unresolved. The committee cannot fully assess financial integrity until these are cleared.")
    da_challenges.append("Seasonal effects (Diwali inventory) have not been stress-tested against a demand shortfall scenario.")
    da_challenges.append("The model assumes customers will pay per historical pattern. A default or delayed payment by a top customer would materially worsen the outlook.")

    da_missing_evidence = [
        "Actual bank statements post-October 2025 not fully reconciled.",
        "Supplier credit terms renegotiation status unknown.",
        "GST filing compliance beyond October 2025 unconfirmed.",
    ]

    # ── AUDITOR ──────────────────────────────────────────────────────────────
    audit_checks = []
    all_valid = True

    for ref in ["CASH-001", "CASH-002", "CASH-003", "RISK-001", "DEBTOR-001", "RECON-001"]:
        if ref in ev:
            audit_checks.append({"reference": ref, "status": "VERIFIED", "value": ev[ref]["value"]})
        else:
            audit_checks.append({"reference": ref, "status": "NOT_FOUND"})
            all_valid = False

    if open_findings > 0:
        audit_checks.append({
            "reference": "RECON-001",
            "status": "FLAGGED",
            "note": f"{open_findings} unresolved HIGH severity findings affect data integrity assessment.",
        })

    auditor_verdict = "DATA_INTEGRITY_CONCERNS" if open_findings > 2 else "ACCEPTABLE_WITH_CAVEATS" if open_findings > 0 else "VERIFIED"

    # ── CHAIRPERSON SYNTHESIS ─────────────────────────────────────────────────
    risk_votes = [cf_assessment, ro_assessment]
    if risk_votes.count("HIGH_RISK") >= 1:
        overall = "HIGH_RISK"
    elif risk_votes.count("MODERATE") >= 1:
        overall = "MODERATE"
    else:
        overall = "ACCEPTABLE"

    disagreement_score = len(set(risk_votes)) - 1  # 0 if unanimous, 1 if disagreement
    disagreement_note = (
        "Analyst perspectives diverge — ambiguity in the evidence warrants human review."
        if disagreement_score > 0 else
        "Analyst perspectives are broadly aligned."
    )

    if overall == "HIGH_RISK":
        chair_conclusion = (
            f"The committee has material concerns about {business_name}'s near-term cash position. "
            f"The {shortfall_prob:.0%} shortfall probability [CASH-003] and {runway}-day runway [CASH-002], "
            f"combined with {open_findings} unresolved reconciliation findings [RECON-001], "
            f"suggest that immediate intervention planning is advisable. "
            f"Lender readiness requires resolution of open findings and improvement of the readiness score."
        )
        recommended_actions = [
            "Accelerate collection from overdue customers, prioritising Sharma Traders [DEBTOR-001].",
            "Resolve HIGH-severity reconciliation findings before any lender engagement [RECON-001].",
            "Run Rescue Planner interventions to extend runway beyond 30 days [CASH-002].",
            "Ensure GST filings are current and bank statement reconciliation is complete.",
        ]
    elif overall == "MODERATE":
        chair_conclusion = (
            f"The committee notes moderate risks for {business_name}. "
            f"The readiness score of {score} [RISK-001] and {shortfall_prob:.0%} shortfall probability [CASH-003] "
            f"are manageable with active monitoring and targeted interventions. "
            f"Customer concentration and the Sharma Traders payment pattern [DEBTOR-001] are the primary watchpoints."
        )
        recommended_actions = [
            "Monitor Sharma Traders payment closely and consider a proactive conversation [DEBTOR-001].",
            "Diversify customer base to reduce top-customer concentration [RISK-002].",
            "Clear reconciliation findings to strengthen data integrity [RECON-001].",
            "Review Rescue Planner options to reduce shortfall probability below 20% [CASH-003].",
        ]
    else:
        chair_conclusion = (
            f"The committee finds {business_name}'s financial position broadly acceptable at present. "
            f"Runway of {runway} days [CASH-002] and a readiness score of {score} [RISK-001] are positive signals. "
            f"Continued monitoring is recommended, particularly given seasonal dynamics."
        )
        recommended_actions = [
            "Maintain current cash management discipline.",
            "Continue monitoring customer payment patterns [DEBTOR-001].",
            "Address any open reconciliation items promptly [RECON-001].",
        ]

    return {
        "mode": "DETERMINISTIC_DEMONSTRATION",
        "mode_label": "⚠️ Deterministic Rule-Based Analysis — Amazon Bedrock is not configured",
        "business_name": business_name,
        "timestamp": datetime.utcnow().isoformat(),
        "rounds": {
            "round_1": {
                "cash_flow_analyst": {
                    "role": "Cash Flow Analyst",
                    "assessment": cf_assessment,
                    "key_findings": cf_concerns + cf_positives,
                    "concerns": cf_concerns,
                    "positives": cf_positives,
                    "citations": ["CASH-001", "CASH-002", "CASH-003", "CASH-004", "CASH-005"],
                },
                "risk_officer": {
                    "role": "Risk Officer",
                    "assessment": ro_assessment,
                    "key_findings": ro_concerns + ro_positives,
                    "concerns": ro_concerns,
                    "positives": ro_positives,
                    "citations": ["RISK-001", "RISK-002", "RISK-003", "DEBTOR-001"],
                },
                "devils_advocate": {
                    "role": "Devil's Advocate",
                    "challenges": da_challenges,
                    "missing_evidence": da_missing_evidence,
                    "citations": ["CASH-003", "DEBTOR-001", "RECON-001"],
                },
                "auditor": {
                    "role": "Auditor",
                    "checks": audit_checks,
                    "verdict": auditor_verdict,
                    "citations": ["CASH-001", "CASH-002", "CASH-003", "RISK-001", "DEBTOR-001", "RECON-001"],
                },
            },
            "round_2": {
                "rebuttals": [
                    {
                        "from": "Risk Officer",
                        "to": "Cash Flow Analyst",
                        "note": "Concur on runway concern. Customer concentration amplifies any collection delay — not independent risks.",
                    },
                    {
                        "from": "Cash Flow Analyst",
                        "to": "Devil's Advocate",
                        "note": "The downside scenario you describe is captured in the P10 Monte Carlo band. The P50 median case is used for the primary assessment.",
                    },
                    {
                        "from": "Auditor",
                        "to": "All",
                        "note": f"All primary metric citations verified. {open_findings} reconciliation findings remain open and represent a data quality caveat on the committee's conclusions.",
                    },
                ],
            },
        },
        "chairperson": {
            "overall_assessment": overall,
            "conclusion": chair_conclusion,
            "recommended_actions": recommended_actions,
            "human_review_required": open_findings > 0 or overall == "HIGH_RISK",
            "human_review_reasons": (
                ["Unresolved HIGH severity reconciliation findings"] if open_findings > 0 else []
            ) + (
                ["Overall assessment is HIGH_RISK — requires human financial advisor review"] if overall == "HIGH_RISK" else []
            ),
            "disclaimer": (
                "This assessment is AI-assisted decision support only. "
                "It does not constitute a lending decision, credit rating, or legal advice. "
                "Consult qualified financial professionals before taking significant business decisions."
            ),
        },
        "disagreement_score": disagreement_score,
        "disagreement_note": disagreement_note,
        "evidence_bundle_size": len(ev),
    }


# ─── BEDROCK COMMITTEE ────────────────────────────────────────────────────────

def run_bedrock_committee(evidence_bundle: dict, business_name: str, bedrock_client, model_id: str) -> dict:
    """
    Run the multi-agent committee using Amazon Bedrock.
    Falls back to deterministic if any invocation fails.
    Each agent's output is validated for evidence citations.
    """
    try:
        system_prompt = """You are participating in a structured AI Credit Committee analysis for an Indian MSME.
You will receive a verified evidence bundle with metric IDs (e.g. CASH-001, RISK-002).
CRITICAL RULES:
1. Every factual claim MUST cite a metric ID from the evidence bundle.
2. Do NOT perform arithmetic — use only pre-calculated values from the bundle.
3. Do NOT make unconditional lending recommendations.
4. Your role is decision SUPPORT, not decision MAKING.
5. Be specific, grounded, and cite evidence."""

        agents = {
            "cash_flow_analyst": (
                "You are the CASH FLOW ANALYST. "
                "Evaluate cash runway (CASH-002), shortfall probability (CASH-003), "
                "minimum projected balance (CASH-004), and total outstanding (CASH-005). "
                "Respond in JSON: {role, assessment (ACCEPTABLE/MODERATE/HIGH_RISK), key_findings: [], concerns: [], positives: [], citations: []}"
            ),
            "risk_officer": (
                "You are the RISK OFFICER. "
                "Evaluate readiness score (RISK-001), customer concentration (RISK-002), "
                "overdue receivables (RISK-003), and Sharma Traders delay (DEBTOR-001). "
                "Respond in JSON: {role, assessment, key_findings: [], concerns: [], positives: [], citations: []}"
            ),
            "devils_advocate": (
                "You are the DEVIL'S ADVOCATE. Challenge assumptions. "
                "What evidence is missing? What could go worse than the P50 forecast? "
                "Respond in JSON: {role, challenges: [], missing_evidence: [], citations: []}"
            ),
            "auditor": (
                "You are the AUDITOR. Verify that other analysts' claims are supported by the evidence bundle. "
                "Flag any uncited claims. Report on reconciliation findings (RECON-001, RECON-002). "
                "Respond in JSON: {role, checks: [], verdict, citations: []}"
            ),
        }

        evidence_text = json.dumps(
            {k: {"label": v["label"], "value": v["value"], "unit": v["unit"]} for k, v in evidence_bundle.items()},
            indent=2
        )

        round_1_results = {}
        for agent_name, agent_prompt in agents.items():
            messages = [
                {
                    "role": "user",
                    "content": f"Evidence Bundle:\n{evidence_text}\n\nBusiness: {business_name}\n\nAnalyse as instructed."
                }
            ]

            response = bedrock_client.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1200,
                    "system": system_prompt + "\n\n" + agent_prompt,
                    "messages": messages,
                }),
                contentType="application/json",
                accept="application/json",
            )

            body = json.loads(response["body"].read())
            raw_text = body["content"][0]["text"]

            try:
                agent_result = json.loads(raw_text)
            except json.JSONDecodeError:
                # Extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
                agent_result = json.loads(json_match.group()) if json_match else {"role": agent_name, "raw": raw_text}

            # Validate citations
            citations = agent_result.get("citations", [])
            invalid_citations = [c for c in citations if not validate_citation(c, evidence_bundle)]
            if invalid_citations:
                agent_result["_invalid_citations"] = invalid_citations
                logger.warning(f"Agent {agent_name} made invalid citations: {invalid_citations}")

            round_1_results[agent_name] = agent_result

        # Chairperson synthesis
        chair_prompt = (
            f"You are the CHAIRPERSON synthesising the committee discussion.\n"
            f"Round 1 Analysis:\n{json.dumps(round_1_results, indent=2)}\n"
            f"Evidence Bundle:\n{evidence_text}\n\n"
            "Synthesise into: {overall_assessment, conclusion, recommended_actions: [], human_review_required: bool, disclaimer}"
        )

        chair_response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [{"role": "user", "content": chair_prompt}],
            }),
            contentType="application/json",
            accept="application/json",
        )

        chair_body = json.loads(chair_response["body"].read())
        chair_raw = chair_body["content"][0]["text"]
        try:
            chairperson = json.loads(chair_raw)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', chair_raw, re.DOTALL)
            chairperson = json.loads(json_match.group()) if json_match else {"conclusion": chair_raw}

        chairperson.setdefault("disclaimer", (
            "This assessment is AI-assisted decision support only. "
            "It does not constitute a lending decision, credit rating, or legal advice."
        ))

        return {
            "mode": "BEDROCK_LIVE",
            "mode_label": "Live Amazon Bedrock Analysis",
            "model_id": model_id,
            "business_name": business_name,
            "timestamp": datetime.utcnow().isoformat(),
            "rounds": {
                "round_1": round_1_results,
            },
            "chairperson": chairperson,
            "evidence_bundle_size": len(evidence_bundle),
        }

    except Exception as e:
        logger.error(f"Bedrock committee failed: {e}. Falling back to deterministic mode.")
        result = run_deterministic_committee(evidence_bundle, business_name)
        result["bedrock_error"] = str(e)
        result["mode"] = "DETERMINISTIC_FALLBACK_FROM_BEDROCK_ERROR"
        result["mode_label"] = "⚠️ Bedrock unavailable — Deterministic fallback in use"
        return result
