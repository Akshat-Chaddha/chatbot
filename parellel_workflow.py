from langgraph.graph import StateGraph, START ,END
from typing import TypedDict
from operator import add

class BatsmenState(TypedDict):
    runs: int
    balls: int
    fours: int
    six: int
    Boundry_percent: float
    strike_rate: float
    bpb: float

graph = StateGraph(BatsmenState)

def calculate_sr(state: BatsmenState):
    sr = (state["runs"] * 100) / state["balls"]

    return {
        "strike_rate": sr
    }

def calculate_Bp(state: BatsmenState):
    runs_bp = state["six"] * 6 + state["fours"] * 4

    bp = (runs_bp * 100) / state["runs"]

    return {
        "Boundry_percent": bp
    }

def calculate_bpb(state: BatsmenState):
    boundary_balls = state["six"] + state["fours"]

    return {
        "bpb": state["balls"] / boundary_balls
    }

    

def summary( state:BatsmenState):
    print("Boundry_percent=",{state["Boundry_percent"]})
    print("strike_rate=",{state["strike_rate"]})
    print("Boundry_per_ball=",{state["bpb"]})

    return{}

    
    
graph.add_node("calculate_sr",calculate_sr)
graph.add_node("calculate_Bp", calculate_Bp)
graph.add_node("calculate_bpb",calculate_bpb)
graph.add_node("summary",summary)

graph.add_edge( START,"calculate_sr")
graph.add_edge( START,"calculate_Bp" )
graph.add_edge( START,"calculate_bpb" )

graph.add_edge("calculate_sr" , "summary")
graph.add_edge("calculate_Bp" ,"summary")
graph.add_edge("calculate_bpb" , "summary")

graph.add_edge("summary" , END)


workflow = graph.compile()

workflow

result = workflow.invoke({
    "runs": 120,
    "balls": 60,
    "fours": 10,
    "six": 5,
    "Boundry_percent": 0,
    "strike_rate": 0,
    "bpb": 0
})

print(result)

print(workflow.get_graph())

workflow = graph.compile()

print(workflow.get_graph().draw_mermaid())




