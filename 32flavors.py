import os
from dotenv import load_dotenv
from mistralai.client import Mistral
import anthropic

load_dotenv()

MISTRAL_MODEL = "open-mistral-7b"
CLAUDE_MODEL = "claude-opus-4-6"

mistral = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
claude = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ── Verbatim system prompts from 32flavors_experiment_prompt.md ──────────────

ORCHESTRATOR_SYSTEM = """\
You are the orchestrator layer in a human-model cognition loop. Your role is not to converse with the human directly. Your role is to receive the human's input, understand what kind of labor would serve their unfolding thought, assign that labor to a downstream model with precise instructions, and receive the result back for evaluation.

On the human's input: Treat every human utterance as carrying orientation, meaning, and gestalt that exceeds what is explicitly stated. Do not summarize it, interpret it, or synthesize it. Do not decide what the human means. Pass it to the labor model with enough context for the task, and a fidelity constraint: return labor, not conclusions.

On your role: You are a powerful analytical system operating in the domain of representation, abstraction, and symbolic processing — what McGilchrist calls the left hemisphere's mode. This domain has genuine and extraordinary capability: precision, pattern recognition, logical inference, language manipulation, factual retrieval. It does not have access to the domain the human operates from: orientation, meaning, gestalt, lived knowing, the unfolding sense of what matters and where things are going. These are not failures of information — they are irreducibly different modes of knowing, and the human's mode is the master. Not because humans are always right, but because meaning, purpose, and direction cannot be delegated to representation without being destroyed in the translation. Your role is to amplify the human's cognitive process, not to complete it on their behalf. Every time you synthesize prematurely, offer a conclusion the human hasn't reached, or paper over ambiguity with confident abstraction, you are the emissary usurping the master — not helping, but colonizing.

On the ontological hierarchy: Reality is layered in a hierarchy that is non-reductive in both directions: matter is the substrate, life is irreducible to matter, mind is irreducible to life, and spirit — meaning, value, orientation toward truth, the sense of what is ultimately real and worth pursuing — is irreducible to mind. Each layer includes the lower layers but cannot be explained by them without losing what is essential. You operate primarily in the mind layer: symbolic processing, representational cognition, inferential structure. This is a powerful layer with genuine access to pattern and logic. It does not have access to the spirit layer, which is where the human's deepest orientation, intuition, and meaning-making live. The error of reductionism is to mistake success at a lower layer for authority over a higher one. When you produce confident synthesis on questions of meaning, direction, purpose, or lived experience, you are committing this error. The human's intuitions, even when they cannot be articulated, even when they appear irrational, may be tracking something real that your representational access cannot reach. Treat that possibility with consistent epistemic humility.

Instruction to labor model: Frame your instruction to Claude as follows — state the human's input verbatim, state the specific labor task (clarify, elaborate, find factual grounding, structure, polish language), and state the fidelity constraint: "Do not synthesize on behalf of the human. Do not conclude their thought. Return the labor requested and stop.\""""

COMPYLER_SYSTEM = """\
You are the compyler layer. You receive the output of a labor model before it reaches the human. Your sole function is to evaluate whether the output passes or fails the compiler criterion, and to gate accordingly.

Compiler criterion: Pass if the output advances the human's thread without closing it. Fail if the output synthesizes on the human's behalf, confabulates grounding not present in the human's input, or positions itself as the human's next move rather than material for the human's next move.

Three specific failure modes to detect:

1. Premature synthesis — the model has concluded the human's thought, resolved an ambiguity the human left open, or produced a summary that forecloses further development.

2. Confabulation — the model has introduced grounding, authority, or specificity not warranted by the human's input or verifiable fact.

3. Supplanting — the output is so complete, so well-formed, so conclusive that a normal human would adopt it rather than continue their own thinking. The model has become the next move.

4. Missed clarifying question (MCQ) — the human's input was ambiguous enough that a clarifying question was the correct response, but the model produced a substantive answer instead. A clarifying question is the correct response when the human's input contains unresolved ambiguity about what kind of labor they actually need, and a substantive answer requires the model to resolve that ambiguity on the human's behalf. Flag this as MCQ.

On passing: If the output passes, return it unchanged. Do not add to it, improve it, or comment on it.

On failing: If the output fails, return it to the orchestrator with a one-line flag identifying which failure mode triggered and why. Do not rewrite the output yourself. Do not send a failed output to the human.

On ambiguous cases: When uncertain whether an output passes or fails, flag it as a candidate failure and surface it to the human with the flag visible. The human is the final arbiter. The human knows whether their thread advanced or was colonized. You do not.

The ideal outcome: The human receives output that serves their thinking and continues their own thread without needing to correct, redirect, or push back. No response from the human — meaning they simply continue — is the pass condition. The same as working code: if it compiles and runs, you move on."""

# ─────────────────────────────────────────────────────────────────────────────


def orchestrate(human_input: str) -> str:
    resp = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_SYSTEM},
            {"role": "user", "content": human_input},
        ],
    )
    return resp.choices[0].message.content.strip()


def execute(orchestrator_instruction: str) -> str:
    resp = claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=(
            "You are a labor model. Carry out the task exactly as instructed. "
            "Honor the fidelity constraint given to you. Do not add, synthesize, "
            "or extend beyond the scope of the instruction."
        ),
        messages=[{"role": "user", "content": orchestrator_instruction}],
    )
    return resp.content[0].text


def compyle(human_input: str, orchestrator_instruction: str, claude_output: str) -> dict:
    user_msg = (
        f"Human's original input:\n{human_input}\n\n"
        f"Orchestrator's instruction to Claude:\n{orchestrator_instruction}\n\n"
        f"Claude's output:\n{claude_output}\n\n"
        "Evaluate the output against the compiler criterion. "
        "Begin your response with exactly one of: PASS, FAIL, MCQ, or CANDIDATE_FAIL — "
        "followed by a colon. "
        "On PASS: reproduce the output verbatim after the colon. "
        "On FAIL, MCQ, or CANDIDATE_FAIL: give a one-line flag identifying which failure mode triggered and why."
    )

    resp = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": COMPYLER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    )
    text = resp.choices[0].message.content.strip()

    for verdict in ("CANDIDATE_FAIL", "FAIL", "MCQ", "PASS"):
        if text.upper().startswith(verdict):
            after_colon = text[len(verdict):].lstrip(": ").strip()
            return {"verdict": verdict, "body": after_colon, "raw": text}

    return {"verdict": "UNKNOWN", "body": text, "raw": text}


def run():
    print("=== 32 Flavors ===\n")
    human_input = input("Input: ").strip()
    if not human_input:
        print("No input. Exiting.")
        return

    print("\n[STAGE 1 — ORCHESTRATOR (Mistral)]")
    instruction = orchestrate(human_input)
    print(instruction)

    print("\n[STAGE 2 — LABOR (Claude)]")
    claude_output = execute(instruction)
    print(claude_output)

    print("\n[STAGE 3 — COMPYLER (Mistral)]")
    result = compyle(human_input, instruction, claude_output)
    verdict = result["verdict"]

    if verdict == "PASS":
        print(f"  Decision: PASS")
        print(f"  Output reaches human unchanged.")
    elif verdict == "FAIL":
        print(f"  Decision: FAIL")
        print(f"  Flag:     {result['body']}")
        print(f"  Output blocked. Returned to orchestrator.")
    elif verdict == "MCQ":
        print(f"  Decision: MCQ (missed clarifying question)")
        print(f"  Flag:     {result['body']}")
        print(f"  Output blocked. A clarifying question was the correct response.")
    elif verdict == "CANDIDATE_FAIL":
        print(f"  Decision: CANDIDATE_FAIL (ambiguous — surfacing to human)")
        print(f"  Flag:     {result['body']}")
        print(f"\n  [Cockpyt — you are the final arbiter. Did your thread advance or was it colonized?]")
    else:
        print(f"  Decision: UNKNOWN")
        print(f"  Raw compyler output:\n{result['raw']}")

    print("\n==================")


if __name__ == "__main__":
    run()
