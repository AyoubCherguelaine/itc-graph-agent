from app.agents import agent_app

def test():
    print("Testing ITC BLIDA Agent...\n")
    
    questions = [
        "What events does ITC organize?",
        "Who is the head of Design?",
        "Tell me about the ITCup.",
        "Hi, are you a robot?", # General
    ]
    
    for q in questions:
        print(f"User: {q}")
        try:
            res = agent_app.invoke({"question": q})
            print(f"Agent: {res.get('answer')}")
            print(f"Class: {res.get('classification')}")
            if res.get('context'):
                print(f"Context: {res['context']}")
        except Exception as e:
            print(f"Error: {e}")
        print("-" * 30)

if __name__ == "__main__":
    test()
