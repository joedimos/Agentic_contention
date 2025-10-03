import os
import random
import threading
from nanda_adapter import NANDA
from crewai import Agent, Task, Crew
from litellm import completion  # LiteLLM core


# Minimal LiteLLM wrapper so CrewAI agents can use it
class LiteLLMWrapper:
    def __init__(self, model, api_key, provider="mistral-inference"):
        self.model = model
        self.api_key = api_key
        self.provider = provider

    def __call__(self, prompt: str) -> str:
        return completion(
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            prompt=prompt,
            max_tokens=512
        ).text


def create_absurdist_improvement():
    """Create a multi-agent absurdist transformation system"""

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("Please set your MISTRAL_API_KEY environment variable")

    mistral_model = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
    llm = LiteLLMWrapper(model=mistral_model, api_key=api_key, provider="mistral-inference")

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
        goal="Blend Camus’ existential clarity with Plath’s poetic darkness",
        backstory="You are the mediator between philosophy and poetry, weaving both voices into one.",
        verbose=True,
        llm=llm
    )

    # Extended Agents
    kafka_agent = Agent(
        role="Kafkaesque Bureaucrat",
        goal="Reinterpret the message through endless rules, futility, and systemic absurdity",
        backstory="You are Franz Kafka’s digital echo, lost in a labyrinth of pointless bureaucracy.",
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
        backstory="You are Kierkegaard’s ironic cousin, living in a spiral of contradictions and humor.",
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
        """Transform message into absurdist-philosophical text with chosen style"""
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
                    description=f"Reframe this message in Plath’s dark poetic style:\n{message_text}",
                    expected_output="A lyrical, melancholic reinterpretation with vivid imagery.",
                    agent=plath_agent
                ))
                selected_agents.append(plath_agent)

            # Random additional absurdists for blend mode
            if mode == "blend":
                extras = random.sample([kafka_agent, dada_agent, ironist_agent, mystic_agent], k=2)
                for agent in extras:
                    tasks.append(Task(
                        description=f"Reframe this message in the style of {agent.role}:",
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
            return f"Like Sisyphus, {message_text} rolls endlessly toward the silence of the void."

    return absurdist_improvement


def repl(absurdist_logic):
    """Simple terminal chat loop"""
    print("Starting Absurdist Agent REPL...")
    print("Type your messages and press Enter. Type 'exit' or 'quit' to stop.\n")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("Goodbye. The void awaits...")
            break
        response = absurdist_logic(user_input)
        print(f"Absurdist Agent: {response}\n")


def main():
    """Start the absurdist agent server (NANDA API + REPL)"""
    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set your MISTRAL_API_KEY environment variable")
        return

    absurdist_logic = create_absurdist_improvement()
    nanda = NANDA(absurdist_logic)

    # Run NANDA server in background
    print("Starting NANDA server in background on http://localhost:8000 ...")
    threading.Thread(target=nanda.start_server, daemon=True).start()

    # Run REPL in foreground
    repl(absurdist_logic)


if __name__ == "__main__":
    main()
