import sys

# Add the custom path to sys.path
sys.path.append(r'C:\Users\Ankurv\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\Local-packages\Python311\site-packages')

# Now you can import your package
import langgraph # Replace this with the actual package name
from langgraph.graph import StateGraph

# Define initial state
state = {"message": "Hello, LangGraph!"}

# Node function (acts like a node)
def greet(state):
    print(state["message"])
    return state

# Create stateful graph
builder = StateGraph(state)
builder.add_node("greet", greet)
builder.set_entry_point("greet")

# Compile and run
graph = builder.compile()
graph.invoke(state)
