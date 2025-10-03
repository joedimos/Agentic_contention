import os
import random
import threading
from nanda_adapter import NANDA
from crewai import Agent, Task, Crew
from crewai import LLM


def create_absurdist_chat():
    """Create a multi-agent absurdist transformation chat system"""

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

    def absurdist_chat(messages: list, mode: str = "blend") -> str:
        """
        Transform the latest message into absurdist-philosophical text
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            mode: Style mode ('camus', 'plath', or 'blend')
        
        Returns:
            Absurdist response string
        """
        try:
            # Get the latest user message
            user_messages = [m for m in messages if m.get('role') == 'user']
            if not user_messages:
                return "The silence speaks volumes in the theater of the absurd."
            
            message_text = user_messages[-1].get('content', '')
            
            # Include conversation context if available
            context = ""
            if len(messages) > 1:
                context = "Previous conversation context:\n"
                for msg in messages[-3:-1]:  # Last 2 messages before current
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    context += f"{role}: {content}\n"
                context += "\n"
            
            tasks = []
            selected_agents = []

            # Core selections
            if mode in ["camus", "blend"]:
                tasks.append(Task(
                    description=f"{context}Reframe this message with Camusian absurdism:\n{message_text}",
                    expected_output="A philosophical reinterpretation emphasizing futility, absurdity, or revolt.",
                    agent=camus_agent
                ))
                selected_agents.append(camus_agent)

            if mode in ["plath", "blend"]:
                tasks.append(Task(
                    description=f"{context}Reframe this message in Plath's dark poetic style:\n{message_text}",
                    expected_output="A lyrical, melancholic reinterpretation with vivid imagery.",
                    agent=plath_agent
                ))
                selected_agents.append(plath_agent)

            # Random additional absurdists for blend mode
            if mode == "blend":
                extras = random.sample([kafka_agent, dada_agent, ironist_agent, mystic_agent], k=2)
                for agent in extras:
                    tasks.append(Task(
                        description=f"{context}Reframe this message in the style of {agent.role}:\n{message_text}",
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
            print(f"Error in absurdist chat: {e}")
            return f"Like Sisyphus, your words roll endlessly toward the silence of the void."

    return absurdist_chat


def repl(chat_function):
    """Simple terminal chat loop"""
    print("Starting Absurdist Agent REPL...")
    print("Type your messages and press Enter. Type 'exit' or 'quit' to stop.\n")
    
    conversation_history = []
    
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye. The void awaits...")
            break
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Call the chat function with full message history
        response = chat_function(conversation_history)
        
        # Add assistant response to history
        conversation_history.append({"role": "assistant", "content": response})
        
        print(f"Absurdist Agent: {response}\n")


def main():
    """Start the absurdist agent server (NANDA API + REPL)"""
    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set your MISTRAL_API_KEY environment variable")
        return

    absurdist_chat_fn = create_absurdist_chat()
    nanda = NANDA(absurdist_chat_fn)

    # Run NANDA server in background
    print("Starting NANDA server in background on http://localhost:8000 ...")
    threading.Thread(target=nanda.start_server, daemon=True).start()

    # Run REPL in foreground using the chat function directly
    repl(absurdist_chat_fn)


if __name__ == "__main__":
    main()
