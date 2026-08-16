"""
Terminal CLI test script to test the LangChain + Gemini Chatbot.
"""
from dotenv import load_dotenv
from llm_service import get_llm_service

load_dotenv()

def main():
    print("=" * 50)
    print(" CogAdvisor - Financial Planning AI (Gemini)")
    print(" Type 'exit' or 'quit' to end the chat.")
    print("=" * 50)
    
    try:
        service = get_llm_service()
    except Exception as e:
        print(f"\n[Error] Failed to initialize LLM: {e}")
        return

    history = []
    
    # Sample contextual profile
    sample_profile = {"age": 28, "monthly_income": "$5,000", "monthly_savings": "$1,000"}
    sample_goals = [{"goal": "Emergency Fund", "target": "$10,000"}, {"goal": "Home Down Payment", "target": "$50,000"}]
    risk_tolerance = "Moderate"

    print(f"\n[Context Loaded] Profile: {sample_profile}, Risk: {risk_tolerance}\n")

    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chat. Goodbye!")
                break

            reply, sources = service.generate_reply(
                question=user_input,
                user_profile=sample_profile,
                goals=sample_goals,
                risk_tolerance=risk_tolerance,
                chat_history=history
            )

            print(f"\nBot:\n{reply}\n")
            if sources:
                print("-" * 30)
                print(f"[RAG Sources Retrieved: {len(sources)}]")
                for s in sources:
                    print(f" • {s.get('source')} ({s.get('category')}) - score: {s.get('relevance_score')}")
                print("-" * 30)
            
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": reply})

        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except Exception as err:
            print(f"\nError: {err}")

if __name__ == "__main__":
    main()
