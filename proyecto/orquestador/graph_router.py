from langgraph.graph import StateGraph, START, END
from state import UserQueryState
from experts_mock import experto_faq, experto_hipotecas
from model import router_llm
from speech_to_text import speech

g = StateGraph(UserQueryState)

g.add_node("router", router_llm)

g.add_node("faq", experto_faq)

g.add_node("hipotecas", experto_hipotecas)

def decidir_experto(state: UserQueryState):
    return state["model"]

g.add_edge(START, "router")
g.add_conditional_edges("router", decidir_experto, ["faq", "hipotecas"])
g.add_edge("faq", END)
g.add_edge("hipotecas", END)

app = g.compile()

if __name__ == "__main__":
    while(True):
        user_input = speech()
        ejemplo = {"input": user_input, "model": None, "output": None}
        res = app.invoke(ejemplo)

        print(res)
        user_input = input("\nAlguna otra pregunta? (enter para continuar, escribe 'no' para salir): ")
        if user_input == "no":
            print("\nSaliendo del programa ...\n")
            break

