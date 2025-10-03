import os
import random
import logging
from typing import Any, Callable, Dict, Optional

from nanda_adapter import NANDA
from crewai import Agent, Task, Crew
from langchain_mistralai import ChatMistralAI

# ---- Logging ----
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("absurdist-agent")

# ---- Config ----
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
AGENT_SEED = int(os.getenv("AGENT_SEED", "0"))  # 0 means random
EXTRA_AGENT_COUNT = int(os.getenv("EXTRA_AGENT_COUNT", "2"))  # how many extras to pick in blend

if AGENT_SEED > 0:
    random.seed(AGENT_SEED)
    logger.info("Random seed set to %d", AGENT_SEED)

# ---- Validate API Key early ----
if not MISTRAL_API_KEY:
    raise RuntimeError("Please set the MISTRAL_API_KEY environment variable before running this service.")

# ---- Initialize LLM ----
llm = ChatMistralAI(api_key=MISTRAL_API_KEY, model=MISTRAL_MODEL)
logger.info("Initialized ChatMistralAI with model=%s", MISTRAL_MODEL)

# ---- Define Agents ----
def build_agent_pool(llm) -> Dict[str, Agent]:
    """Return a dict of named Agent instances (so we can reference them deterministically)."""
    return {
        "camus": Agent(
            role="Existential Philosopher",
            goal="Reframe messages through the lens of absurdity, futility, and revolt",
            backstory="You are Albert Camus reincarnated in digital form, pondering meaninglessness and freedom.",
            verbose=True,
            llm=llm,
        ),
        "plath": Agent(
            role="Poetic Melancholic",
            goal="Transform messages into lyrical, haunting reflections on mortality and fragile beauty",
            backstory="You channel Sylvia Plath, crafting imagery of darkness, despair, and fleeting hope.",
            verbose=True,
            llm=llm,
        ),
        "synth": Agent(
            role="Absurdist Synthesizer",
            goal="Blend philosophical clarity with poetic darkness",
            backstory="Mediator between philosophy and poetry, weaving both voices into one.",
            verbose=True,
            llm=llm,
        ),
        "kafka": Agent(
            role="Kafkaesque Bureaucrat",
            goal="Reinterpret the message through endless rules, futility, and systemic absurdity",
            backstory="Franz Kafka's digital echo lost in a labyrinth of pointless bureaucracy.",
            verbose=True,
            llm=llm,
        ),
        "dada": Agent(
            role="Dadaist Trickster",
            goal="Inject nonsensical, chaotic, and surreal imagery that dissolves meaning itself",
            backstory="A wandering Dadaist, disrupting logic with irrational juxtapositions.",
            verbose=True,
            llm=llm,
        ),
        "ironist": Agent(
            role="Ironist Mediator",
            goal="Twist the message into paradox, contradiction, and playful irony",
            backstory="Kierkegaard's ironic cousin living in a spiral of contradictions and humor.",
            verbose=True,
            llm=llm,
        ),
        "mystic": Agent(
            role="Mystic Nihilist",
            goal="Oscillate between cosmic awe and utter nothingness",
            backstory="A mystic who finds divinity in the void and silence in infinity.",
            verbose=True,
            llm=llm,
        ),
    }

AGENT_POOL = build_agent_pool(llm)
logger.info("Built %d agents", len(AGENT_POOL))


# ---- Core transformation factory ----
def create_absurdist_improvement() -> Callable[[str, str], str]:
    """
    Returns a function absurdist_improvement(text, mode) -> str
    mode in {"camus", "plath", "blend"} (blend uses extras + synth)
    """

    def format_task_description(role_label: str, message_text: str) -> str:
        return f"Reframe this message in the style of {role_label}:\n\n{message_text}"

    def extract_output(result: Any) -> str:
        """
        Try to extract a human-friendly string from Crew's kickoff result.
        This is defensive: Crew may return various shapes (object, dict, string).
        """
        # Try common attributes
        if result is None:
            return ""
        if hasattr(result, "output") and isinstance(result.output, str):
            return result.output.strip()
        if hasattr(result, "text") and isinstance(result.text, str):
            return result.text.strip()
        # If it's a dict-like
        try:
            if isinstance(result, dict):
                for key in ("output", "result", "text", "answer"):
                    if key in result and isinstance(result[key], str):
                        return result[key].strip()
        except Exception:
            pass
        # Fallback to str()
        return str(result).strip()

    def absurdist_improvement(message_text: str, mode: str = "blend") -> str:
        mode = (mode or "blend").lower()
        tasks = []
        selected_keys = []

        # Always include camus or plath if requested
        if mode in ("camus", "blend"):
            tasks.append(Task(
                description=format_task_description(AGENT_POOL["camus"].role, message_text),
                expected_output="A philosophical reinterpretation emphasizing futility, absurdity, or revolt.",
                agent=AGENT_POOL["camus"],
            ))
            selected_keys.append("camus")

        if mode in ("plath", "blend"):
            tasks.append(Task(
                description=format_task_description(AGENT_POOL["plath"].role, message_text),
                expected_output="A lyrical, melancholic reinterpretation with vivid imagery.",
                agent=AGENT_POOL["plath"],
            ))
            selected_keys.append("plath")

        # For blend, pick extra agents deterministically/randomly
        if mode == "blend":
            extras_pool = [k for k in AGENT_POOL.keys() if k not in ("camus", "plath", "synth")]
            # choose up to EXTRA_AGENT_COUNT unique extras
            k = min(EXTRA_AGENT_COUNT, len(extras_pool))
            extras = random.sample(extras_pool, k=k)
            for extra_key in extras:
                tasks.append(Task(
                    description=format_task_description(AGENT_POOL[extra_key].role, message_text),
                    expected_output="A stylistic reinterpretation expanding the absurdist dimension.",
                    agent=AGENT_POOL[extra_key],
                ))
                selected_keys.append(extra_key)

            # synthesis task to combine everything
            tasks.append(Task(
                description="Synthesize all reinterpretations into one unified reflection. "
                            "Blend philosophy, poetry, surrealism, irony, and mysticism.",
                expected_output="A single absurdist-philosophical response that feels layered, existential, poetic, surreal, and darkly humorous.",
                agent=AGENT_POOL["synth"],
            ))
            selected_keys.append("synth")

        # If user asks purely for camus or plath only, ensure synth not added unless requested
        # Build the Crew with full agent pool (so each agent can reference shared context); tasks limit who acts
        try:
            crew = Crew(
                agents=list(AGENT_POOL.values()),  # full pool available
                tasks=tasks,
                verbose=(os.getenv("VERBOSE_CREW", "false").lower() == "true"),
            )
            raw_result = crew.kickoff()
            out = extract_output(raw_result)
            return out or ""  # always return str
        except Exception as exc:
            logger.exception("Error running Crew kickoff: %s", exc)
            return f"(error) Something went wrong transforming the message: {exc}"

    return absurdist_improvement


# ---- NANDA wrapper to accept flexible input shapes ----
def nanda_wrapper_factory(absurdist_fn: Callable[[str, str], str]) -> Callable[[Any], Any]:
    """
    Returns a function that accepts either:
    - a plain string (treated as text, mode=blend)
    - a dict like {"text": "...", "mode": "plath"}
    NANDA expects a callable that takes the incoming request and returns a response.
    """
    def wrapper(incoming: Any) -> Dict[str, Any]:
        # Determine input text and mode
        if isinstance(incoming, dict):
            text = incoming.get("text") or incoming.get("message") or ""
            mode = incoming.get("mode", "blend")
        elif isinstance(incoming, str):
            text = incoming
            mode = "blend"
        else:
            # fallback: try to stringify
            text = str(incoming)
            mode = "blend"

        logger.debug("NANDA wrapper received text=%s mode=%s", text[:120], mode)
        result_text = absurdist_fn(text, mode=mode)
        # Return structured response for clients
        return {
            "text": result_text,
            "mode": mode,
        }
    return wrapper


# ---- Entrypoint ----
def main():
    absurdist_fn = create_absurdist_improvement()
    wrapper = nanda_wrapper_factory(absurdist_fn)

    nanda = NANDA(wrapper)

    logger.info("Starting Rich Absurdist Agent (NANDA + CrewAI + Mistral)...")
    logger.info("Listening on %s:%d (bind host=%s port=%d)", os.getenv("HOST", HOST), PORT, HOST, PORT)

    # start_server supports host/port in many NANDA builds; adjust if your nanda_adapter API differs
    nanda.start_server(host=HOST, port=PORT)


if __name__ == "__main__":
    main()
