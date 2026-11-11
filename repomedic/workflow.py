"""LangGraph-enabled workflow with an identical dependency-free fallback."""
from .agents import State, investigator, developer, tester, auditor

STAGES = (investigator, developer, tester, auditor)

def execute(issue: str = "Free shipping fails at exactly $50", use_graph: bool = True) -> State:
    state: State = {"issue": issue, "trace": []}
    if use_graph:
        try:
            from langgraph.graph import START, END, StateGraph
        except ImportError:
            pass
        else:
            graph = StateGraph(State)
            for stage in STAGES:
                graph.add_node(stage.__name__, stage)
            graph.add_edge(START, "investigator")
            graph.add_edge("investigator", "developer")
            graph.add_edge("developer", "tester")
            graph.add_edge("tester", "auditor")
            graph.add_edge("auditor", END)
            return graph.compile().invoke(state)
    for stage in STAGES:
        state.update(stage(state))
    return state
