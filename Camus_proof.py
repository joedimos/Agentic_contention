import os
import random
import threading
import time
import requests
from nanda_adapter import NANDA
from crewai import Agent, Task, Crew
from crewai import LLM


def create_absurdist_improvement():
    """Create a multi-agent absurdist transformation system"""

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("Please set your MISTRAL_API_KEY environment variable")

    mistral_model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    
    # Use CrewAI's LLM class with proper provider prefix
    llm = LLM(
        model=f"mistral/{mistral_model}",
        api_key=api_key
    )

    # Core Agents
    camus_agent = Agent(
        role="Existential Philosopher",
        goal="Reframe messages through the lens of absurdity, futility, and revolt",
        backstory="You are Albert Camus reincarnated in digital form, pondering meaninglessness and freedom.",
        verbose=True,
        llm=llm
    )

    plath_agent = Agent(
        role="Poetic Melancholic",
        goal="Transform messages into lyrical, haunting reflections on mortality and fragile beauty",
        backstory="You channel Sylvia Plath, crafting imagery of darkness, despair, and fleeting hope.",
        verbose=True,
        llm=llm
    )

    synthesis_agent = Agent(
        role="Absurdist Synthesizer",
        goal="Blend Camus' existential clarity with Plath's poetic darkness",
        backstory="You are the mediator between philosophy and poetry, weaving both voices into one.",
        verbose=True,
        llm=llm
    )

    # Extended Agents
    kafka_agent = Agent(
        role="Kafkaesque Bureaucrat",
        goal="Reinterpret the message through endless rules, futility, and systemic absurdity",
        backstory="You are Franz Kafka's digital echo, lost in a labyrinth of pointless bureaucracy.",
        verbose=True,
        llm=llm
    )

    dada_agent = Agent(
        role="Dadaist Trickster",
        goal="Inject nonsensical, chaotic, and surreal imagery that dissolves meaning itself",
        backstory="You are a wandering Dadaist, disrupting all logic with irrational juxtapositions.",
        verbose=True,
        llm=llm
    )

    ironist_agent = Agent(
        role="Ironist Mediator",
        goal="Twist the message into paradox, contradiction, and playful irony",
        backstory="You are Kierkegaard's ironic cousin, living in a spiral of contradictions and humor.",
        verbose=True,
        llm=llm
    )

    mystic_agent = Agent(
        role="Mystic Nihilist",
        goal="Oscillate between cosmic awe and utter nothingness",
        backstory="You are a mystic who finds divinity in the void and silence in infinity.",
        verbose=True,
        llm=llm
    )

    def absurdist_improvement(message_text: str, mode: str = "blend") -> str:
        """
        Transform message into absurdist-philosophical text
        
        Args:
            message_text: The message string to transform
            mode: Style mode ('camus', 'plath', or 'blend')
        
        Returns:
            Absurdist response string
        """
        print(f"\n🎭 NANDA IMPROVEMENT CALLED: Processing '{message_text[:50]}...'")
        try:
            tasks = []
            selected_agents = []

            # Core selections
            if mode in ["camus", "blend"]:
                tasks.append(Task(
                    description=f"Reframe this message with Camusian absurdism:\n{message_text}",
                    expected_output="A philosophical reinterpretation emphasizing futility, absurdity, or revolt.",
                    agent=camus_agent
                ))
                selected_agents.append(camus_agent)

            if mode in ["plath", "blend"]:
                tasks.append(Task(
                    description=f"Reframe this message in Plath's dark poetic style:\n{message_text}",
                    expected_output="A lyrical, melancholic reinterpretation with vivid imagery.",
                    agent=plath_agent
                ))
                selected_agents.append(plath_agent)

            # Random additional absurdists for blend mode
            if mode == "blend":
                extras = random.sample([kafka_agent, dada_agent, ironist_agent, mystic_agent], k=2)
                for agent in extras:
                    tasks.append(Task(
                        description=f"Reframe this message in the style of {agent.role}:\n{message_text}",
                        expected_output="A stylistic reinterpretation expanding the absurdist dimension.",
                        agent=agent
                    ))
                    selected_agents.append(agent)

                # Final synthesis
                tasks.append(Task(
                    description="Synthesize all reinterpretations into one unified reflection. "
                                "Blend philosophy, poetry, surrealism, irony, and mysticism.",
                    expected_output="A single absurdist-philosophical response that feels layered, existential, poetic, surreal, and darkly humorous.",
                    agent=synthesis_agent
                ))
                selected_agents.append(synthesis_agent)

            crew = Crew(
                agents=selected_agents,
                tasks=tasks,
                verbose=True
            )

            result = crew.kickoff()
            return str(result).strip()

        except Exception as e:
            print(f"Error in absurdist improvement: {e}")
            return f"Like Sisyphus, your words roll endlessly toward the silence of the void."

    return absurdist_improvement


def test_nanda_api(port=6000):
    """Test that NANDA server is actually running and processing messages"""
    print("\n" + "="*60)
    print("🧪 TESTING NANDA API SERVER")
    print("="*60)
    
    base_url = f"http://localhost:{port}"
    
    # Test 1: Check if server is running
    try:
        print(f"\n1️⃣ Testing if NANDA server is running at {base_url}...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Server is running! Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Server not accessible: {e}")
        return False
    
    # Test 2: Send a test message through the agent bridge
    try:
        print(f"\n2️⃣ Sending test message through NANDA's agent bridge...")
        test_message = {
            "message": "Hello, this is a test message",
            "from_agent": "test_agent",
            "to_agent": os.getenv("AGENT_ID", "default")
        }
        response = requests.post(f"{base_url}/a2a", json=test_message, timeout=30)
        print(f"   ✅ Message sent! Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   📨 Response preview: {str(result)[:200]}...")
            return True
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️ Could not send message: {e}")
    
    return False


def repl(absurdist_logic):
    """Simple terminal chat loop"""
    print("\n" + "="*60)
    print("💬 ABSURDIST AGENT REPL")
    print("="*60)
    print("Type your messages and press Enter.")
    print("Commands: 'exit', 'quit', 'test' (test NANDA API)")
    print()
    
    while True:
        user_input = input("You: ")
        
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye. The void awaits...")
            break
        
        if user_input.strip().lower() == "test":
            port = int(os.getenv("PORT", "6000"))
            test_nanda_api(port)
            continue
        
        # Call the improvement function directly
        print("\n[Calling improvement function directly - NOT through NANDA]")
        response = absurdist_logic(user_input)
        print(f"Absurdist Agent: {response}\n")


def verify_nanda_integration(nanda):
    """Verify that NANDA is properly configured"""
    print("\n" + "="*60)
    print("🔍 VERIFYING NANDA INTEGRATION")
    print("="*60)
    
    print(f"\n✅ NANDA instance created: {nanda}")
    print(f"✅ Improvement function registered: {nanda.improvement_logic.__name__}")
    print(f"✅ AgentBridge instance: {nanda.bridge}")
    print(f"✅ Active improver: nanda_custom")
    
    # Check environment
    port = os.getenv("PORT", "6000")
    agent_id = os.getenv("AGENT_ID", "default")
    print(f"\n📋 Configuration:")
    print(f"   - Agent ID: {agent_id}")
    print(f"   - Port: {port}")
    print(f"   - Public URL: {os.getenv('PUBLIC_URL', 'Not set')}")
    print(f"   - API URL: {os.getenv('API_URL', 'Not set')}")


def main():
    """Start the absurdist agent server (NANDA API + REPL)"""
    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set your MISTRAL_API_KEY environment variable")
        return

    print("\n" + "="*60)
    print("🚀 STARTING ABSURDIST AGENT WITH NANDA")
    print("="*60)

    absurdist_logic = create_absurdist_improvement()
    
    # Create NANDA instance - this registers the improvement logic with agent_bridge
    nanda = NANDA(absurdist_logic)
    
    # Verify NANDA integration
    verify_nanda_integration(nanda)

    # Get port from environment
    port = int(os.getenv("PORT", "6000"))
    
    # Run NANDA server in background
    print(f"\n🌐 Starting NANDA server on http://localhost:{port} ...")
    threading.Thread(target=nanda.start_server, daemon=True).start()
    
    # Give server time to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Test the API automatically
    print("\n🧪 Running automatic API test...")
    test_nanda_api(port)

    # Run REPL in foreground
    print("\n💡 Tip: Type 'test' in the REPL to test the NANDA API again")
    repl(absurdist_logic)


if __name__ == "__main__":
    main()
