#!/usr/bin/env python3
import os
from nanda_adapter import NANDA
from crewai import Agent, Task, Crew
from langchain_mistralai import ChatMistralAI


def create_absurdist_improvement():
    """Create a multi-agent absurdist transformation system using Mistral"""

    # Initialize the LLM (Mistral)
    llm = ChatMistralAI(
        api_key=os.getenv("MISTRAL_API_KEY"),
        model="mistral-large-latest"
    )

    # Camusian Agent
    camus_agent = Agent(
        role="Existential Philosopher",
        goal="Reframe messages through the lens of absurdity, futility, and revolt",
        backstory="You are Albert Camus reincarnated in digital form, pondering meaninglessness and freedom.",
        verbose=True,
        llm=llm
    )

    # Plathian Agent
    plath_agent = Agent(
        role="Poetic Melancholic",
        goal="Transform messages into lyrical, haunting reflections on mortality and fragile beauty",
        backstory="You channel Sylvia Plath, crafting imagery of darkness, despair, and fleeting hope.",
        verbose=True,
        llm=llm
    )

    # Synthesizer Agent
    synthesis_agent = Agent(
        role="Absurdist Synthesizer",
        goal="Blend Camus’ existential clarity with Plath’s poetic darkness",
        backstory="You are the mediator between philosophy and poetry, weaving both voices into one.",
        verbose=True,
        llm=llm
    )

    def absurdist_improvement(message_text: str, mode: str = "blend") -> str:
        """Transform message into absurdist-philosophical text with chosen style"""

        try:
            tasks = []

            if mode in ["camus", "blend"]:
                tasks.append(Task(
                    description=f"Reframe this message with Camusian absurdism:\n{message_text}",
                    expected_output="A philosophical reinterpretation emphasizing futility, absurdity, or revolt.",
                    agent=camus_agent
                ))

            if mode in ["plath", "blend"]:
                tasks.append(Task(
                    description=f"Reframe this message in Plath’s dark poetic style:\n{message_text}",
                    expected_output="A lyrical, melancholic reinterpretation with vivid imagery.",
                    agent=plath_agent
                ))

            # If blending, add a synthesis task
            if mode == "blend":
                tasks.append(Task(
                    description="Synthesize the above reinterpretations into one unified reflection. "
                                "Balance Camus’ clarity with Plath’s imagery.",
                    expected_output="A single absurdist-philosophical response that feels both existential and poetic.",
                    agent=synthesis_agent
                ))

            crew = Crew(
                agents=[camus_agent, plath_agent, synthesis_agent],
                tasks=tasks,
                verbose=True
            )

            result = crew.kickoff()
            return str(result).strip()

        except Exception as e:
            print(f"Error in absurdist improvement: {e}")
            return f"Like Sisyphus, {message_text} rolls endlessly toward the silence of the void."

    return absurdist_improvement


def main():
    """Start the absurdist agent server"""

    if not os.getenv("MISTRAL_API_KEY"):
        print("Please set your MISTRAL_API_KEY environment variable")
        return

    absurdist_logic = create_absurdist_improvement()
    nanda = NANDA(absurdist_logic)

    print("Starting Absurdist Agent with multi-agent CrewAI (Mistral)...")
    print("Messages will be transformed into existential reflections infused with Camus and Plath.")

    domain = os.getenv("DOMAIN_NAME", "localhost")
    if domain != "localhost":
        nanda.start_server_api(os.getenv("MISTRAL_API_KEY"), domain)
    else:
        nanda.start_server()


if __name__ == "__main__":
    main()
