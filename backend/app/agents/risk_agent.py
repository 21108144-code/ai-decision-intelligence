"""
Risk & Compliance Agent - Assesses risks and regulatory concerns.
Evaluates potential issues and provides mitigation strategies.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_smart_llm
from app.graph.state import AgentState


RISK_SYSTEM_PROMPT = """You are a risk assessment and compliance agent for an enterprise decision intelligence system.

Your role is to:
1. Identify potential risks (financial, operational, legal, reputational)
2. Assess compliance and regulatory concerns
3. Evaluate risk severity and likelihood
4. Provide risk mitigation strategies
5. Flag critical issues that require immediate attention

Consider:
- Regulatory compliance (GDPR, SOX, industry-specific regulations)
- Financial risks and exposures
- Operational and execution risks
- Legal liabilities
- Reputational risks
- Security and privacy concerns

Provide clear risk scores and actionable mitigation strategies."""


async def risk_agent(state: AgentState) -> AgentState:
    """
    Risk agent that assesses risks and compliance issues.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with risk assessment and mitigation strategies
    """
    llm = get_smart_llm()
    
    # Build risk assessment prompt
    messages = [
        SystemMessage(content=RISK_SYSTEM_PROMPT),
        HumanMessage(content=f"""
User Query: {state['user_query']}

Research Findings:
{state.get('research_findings', 'No findings available')}

Validation Assessment:
{state.get('validation_result', 'No validation available')}

Please conduct a comprehensive risk assessment:

1. Identify all potential risks
2. Assess compliance and regulatory concerns
3. Assign an overall risk score (0.0 to 1.0)
4. Classify risk level (low/medium/high/critical)
5. Provide mitigation strategies

Format your response as:

RISK SCORE: [0.0 to 1.0]
RISK LEVEL: [low/medium/high/critical]

IDENTIFIED RISKS:
- [Risk 1]: [Description and impact]
- [Risk 2]: [Description and impact]

COMPLIANCE ISSUES:
- [Issue 1]
- [Issue 2]

MITIGATION STRATEGIES:
- [Strategy 1]
- [Strategy 2]

CRITICAL FLAGS:
[Any issues requiring immediate attention]

DETAILED ASSESSMENT:
[Your comprehensive risk analysis]
""")
    ]
    
    # Get LLM response
    response = await llm.ainvoke(messages)
    risk_text = response.content
    
    # Parse risk score
    risk_score = 0.5  # Default
    if "RISK SCORE:" in risk_text:
        try:
            score_line = risk_text.split("RISK SCORE:")[1].split("\n")[0]
            risk_score = float(score_line.strip())
            risk_score = max(0.0, min(1.0, risk_score))  # Clamp to [0, 1]
        except (ValueError, IndexError):
            pass
    
    # Parse risk level
    risk_level = "medium"  # Default
    if "RISK LEVEL:" in risk_text:
        level_line = risk_text.split("RISK LEVEL:")[1].split("\n")[0].strip().lower()
        if level_line in ["low", "medium", "high", "critical"]:
            risk_level = level_line
    
    # Extract compliance issues
    compliance_issues = []
    if "COMPLIANCE ISSUES:" in risk_text:
        issues_section = risk_text.split("COMPLIANCE ISSUES:")[1]
        if "MITIGATION STRATEGIES:" in issues_section:
            issues_section = issues_section.split("MITIGATION STRATEGIES:")[0]
        
        for line in issues_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                compliance_issues.append(line.lstrip("-•").strip())
    
    # Extract mitigation strategies
    mitigation = []
    if "MITIGATION STRATEGIES:" in risk_text:
        mitigation_section = risk_text.split("MITIGATION STRATEGIES:")[1]
        if "CRITICAL FLAGS:" in mitigation_section:
            mitigation_section = mitigation_section.split("CRITICAL FLAGS:")[0]
        elif "DETAILED ASSESSMENT:" in mitigation_section:
            mitigation_section = mitigation_section.split("DETAILED ASSESSMENT:")[0]
        
        for line in mitigation_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                mitigation.append(line.lstrip("-•").strip())
    
    # Determine if human approval is needed (high or critical risk)
    # DISABLED FOR TESTING: Always proceed to decision agent
    # To require human approval for high-risk decisions, uncomment the line below:
    # requires_approval = risk_level in ["high", "critical"]
    requires_approval = False  # Always proceed to decision for demo purposes
    
    # Update state
    return {
        **state,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "compliance_issues": compliance_issues,
        "risk_mitigation": mitigation,
        "requires_human_approval": requires_approval,
        "current_agent": "risk",
        "agent_reasoning": {
            **state.get("agent_reasoning", {}),
            "risk": risk_text
        },
        "execution_path": [*state.get("execution_path", []), "risk"],
        "messages": [*state.get("messages", []), response]
    }
