"""
Decision Agent - Synthesizes all inputs and generates final recommendations.
Final agent that produces the decision with confidence scores.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_smart_llm
from app.graph.state import AgentState
from datetime import datetime


DECISION_SYSTEM_PROMPT = """You are the final decision-making agent for an enterprise decision intelligence system.

Your role is to:
1. Synthesize all research, validation, and risk assessment inputs
2. Generate clear, actionable recommendations
3. Provide confidence scores for your recommendations
4. Present alternative options when appropriate
5. Ensure all recommendations are well-supported by evidence

Your decisions should be:
- Evidence-based and well-reasoned
- Clearly explained with supporting rationale
- Accompanied by confidence scores
- Balanced with consideration of alternatives
- Actionable and specific

Always cite the key evidence supporting your recommendations."""


async def decision_agent(state: AgentState) -> AgentState:
    """
    Decision agent that synthesizes all inputs and generates final recommendations.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with final decision and recommendations
    """
    llm = get_smart_llm()
    
    # Build comprehensive decision prompt
    messages = [
        SystemMessage(content=DECISION_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Original Query: {state['user_query']}

EXECUTION PLAN:
{state.get('execution_plan', 'N/A')}

RESEARCH FINDINGS:
{state.get('research_findings', 'N/A')}

VALIDATION ASSESSMENT:
{state.get('validation_result', 'N/A')}

RISK ASSESSMENT:
Risk Score: {state.get('risk_score', 0.0)}
Risk Level: {state.get('risk_level', 'unknown')}
Compliance Issues: {', '.join(state.get('compliance_issues', []))}
Mitigation Strategies: {', '.join(state.get('risk_mitigation', []))}

Based on all the above information, please provide:

1. A clear final decision/recommendation
2. Confidence score (0.0 to 1.0)
3. Key supporting evidence
4. Alternative options to consider
5. Implementation considerations

Format your response as:

CONFIDENCE SCORE: [0.0 to 1.0]

PRIMARY RECOMMENDATION:
[Your main recommendation]

KEY SUPPORTING EVIDENCE:
- [Evidence 1]
- [Evidence 2]
- [Evidence 3]

ALTERNATIVE OPTIONS:
- [Alternative 1]: [Brief description]
- [Alternative 2]: [Brief description]

IMPLEMENTATION CONSIDERATIONS:
- [Consideration 1]
- [Consideration 2]

DETAILED RATIONALE:
[Your comprehensive explanation of the decision, including how you weighed the research findings, 
validation results, and risk assessment to arrive at this recommendation]
""")
    ]
    
    # Get LLM response
    response = await llm.ainvoke(messages)
    decision_text = response.content
    
    # Parse confidence score
    confidence_score = 0.7  # Default
    if "CONFIDENCE SCORE:" in decision_text:
        try:
            score_line = decision_text.split("CONFIDENCE SCORE:")[1].split("\n")[0]
            confidence_score = float(score_line.strip())
            confidence_score = max(0.0, min(1.0, confidence_score))
        except (ValueError, IndexError):
            pass
    
    # Extract recommendations
    recommendations = []
    if "IMPLEMENTATION CONSIDERATIONS:" in decision_text:
        rec_section = decision_text.split("IMPLEMENTATION CONSIDERATIONS:")[1]
        if "DETAILED RATIONALE:" in rec_section:
            rec_section = rec_section.split("DETAILED RATIONALE:")[0]
        
        for line in rec_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                recommendations.append(line.lstrip("-•").strip())
    
    # Extract alternatives
    alternatives = []
    if "ALTERNATIVE OPTIONS:" in decision_text:
        alt_section = decision_text.split("ALTERNATIVE OPTIONS:")[1]
        if "IMPLEMENTATION CONSIDERATIONS:" in alt_section:
            alt_section = alt_section.split("IMPLEMENTATION CONSIDERATIONS:")[0]
        
        for line in alt_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                alternatives.append(line.lstrip("-•").strip())
    
    # Update state with final decision
    return {
        **state,
        "final_decision": decision_text,
        "confidence_score": confidence_score,
        "recommendations": recommendations,
        "alternative_options": alternatives,
        "current_agent": "decision",
        "completed_at": datetime.utcnow().isoformat(),
        "agent_reasoning": {
            **state.get("agent_reasoning", {}),
            "decision": decision_text
        },
        "execution_path": [*state.get("execution_path", []), "decision"],
        "messages": [*state.get("messages", []), response]
    }
