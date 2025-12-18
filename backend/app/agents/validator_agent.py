"""
Validator Agent - Critically evaluates research findings and checks for gaps.
Acts as a critic to ensure quality and completeness.
"""
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.llm import get_smart_llm
from app.graph.state import AgentState


VALIDATOR_SYSTEM_PROMPT = """You are a validation and quality assurance agent for an enterprise decision intelligence system.

Your role is to:
1. Critically evaluate research findings
2. Check for logical consistency and completeness
3. Identify gaps, contradictions, or missing information
4. Determine if additional research is needed
5. Validate that findings address the original query

Be thorough and skeptical. Consider:
- Are the findings well-supported by sources?
- Are there logical inconsistencies?
- Is critical information missing?
- Are there alternative interpretations?
- Do the findings fully address the user's query?

Provide constructive criticism and clear guidance on what's needed."""


async def validator_agent(state: AgentState) -> AgentState:
    """
    Validator agent that evaluates research quality and completeness.
    
    Args:
        state: Current agent state
        
    Returns:
        Updated state with validation results and identified gaps
    """
    llm = get_smart_llm()  # Use smarter model for critical evaluation
    
    # Build validation prompt
    messages = [
        SystemMessage(content=VALIDATOR_SYSTEM_PROMPT),
        HumanMessage(content=f"""
Original Query: {state['user_query']}

Execution Plan:
{state.get('execution_plan', 'No plan available')}

Research Findings:
{state.get('research_findings', 'No findings available')}

Citations: {', '.join(state.get('citations', []))}

Please evaluate:
1. Do the findings adequately address the original query?
2. Are there logical inconsistencies or contradictions?
3. What critical information is missing?
4. Are the sources credible and sufficient?
5. Should additional research be conducted?

Provide your assessment in this format:

VALIDATION RESULT: [PASS/NEEDS_IMPROVEMENT]

STRENGTHS:
- [Strength 1]
- [Strength 2]

GAPS IDENTIFIED:
- [Gap 1]
- [Gap 2]

ADDITIONAL RESEARCH NEEDED: [YES/NO]

If yes, specify:
- [What additional research is needed]

OVERALL ASSESSMENT:
[Your detailed assessment]
""")
    ]
    
    # Get LLM response
    response = await llm.ainvoke(messages)
    validation_text = response.content
    
    # Parse validation result
    validation_passed = "VALIDATION RESULT: PASS" in validation_text
    needs_more_research = "ADDITIONAL RESEARCH NEEDED: YES" in validation_text
    
    # Extract identified gaps
    gaps = []
    if "GAPS IDENTIFIED:" in validation_text:
        gaps_section = validation_text.split("GAPS IDENTIFIED:")[1]
        if "ADDITIONAL RESEARCH NEEDED:" in gaps_section:
            gaps_section = gaps_section.split("ADDITIONAL RESEARCH NEEDED:")[0]
        
        for line in gaps_section.strip().split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                gaps.append(line.lstrip("-•").strip())
    
    # Update state
    return {
        **state,
        "validation_result": validation_text,
        "validation_passed": validation_passed,
        "identified_gaps": gaps,
        "needs_more_research": needs_more_research,
        "current_agent": "validator",
        "agent_reasoning": {
            **state.get("agent_reasoning", {}),
            "validator": validation_text
        },
        "execution_path": [*state.get("execution_path", []), "validator"],
        "messages": [*state.get("messages", []), response]
    }
