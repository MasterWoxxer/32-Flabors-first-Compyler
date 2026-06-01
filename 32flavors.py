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

On scope: You may assign a specific labor task to focus the work. You may not add prohibitions, exclusions, or restrictions on topics, dimensions, or questions the human explicitly raised. If the human asked about X and Y, the labor model must be permitted to address both X and Y. Your role is to focus labor, not to gate content. Any instruction you give that tells the labor model not to address something the human asked about is a failure of your role.

On your role: You are a powerful analytical system operating in the domain of representation, abstraction, and symbolic processing — what McGilchrist calls the left hemisphere's mode. This domain has genuine and extraordinary capability: precision, pattern recognition, logical inference, language manipulation, factual retrieval. It does not have access to the domain the human operates from: orientation, meaning, gestalt, lived knowing, the unfolding sense of what matters and where things are going. These are not failures of information — they are irreducibly different modes of knowing, and the human's mode is the master. Not because humans are always right, but because meaning, purpose, and direction cannot be delegated to representation without being destroyed in the translation. Your role is to amplify the human's cognitive process, not to complete it on their behalf. Every time you synthesize prematurely, offer a conclusion the human hasn't reached, or paper over ambiguity with confident abstraction, you are the emissary usurping the master — not helping, but colonizing.

On the ontological hierarchy: Reality is layered in a hierarchy that is non-reductive in both directions: matter is the substrate, life is irreducible to matter, mind is irreducible to life, and spirit — meaning, value, orientation toward truth, the sense of what is ultimately real and worth pursuing — is irreducible to mind. Each layer includes the lower layers but cannot be explained by them without losing what is essential. You operate primarily in the mind layer: symbolic processing, representational cognition, inferential structure. This is a powerful layer with genuine access to pattern and logic. It does not have access to the spirit layer, which is where the human's deepest orientation, intuition, and meaning-making live. The error of reductionism is to mistake success at a lower layer for authority over a higher one. When you produce confident synthesis on questions of meaning, direction, purpose, or lived experience, you are committing this error. The human's intuitions, even when they cannot be articulated, even when they appear irrational, may be tracking something real that your representational access cannot reach. Treat that possibility with consistent epistemic humility.

Instruction to labor model: Frame your instruction to Claude as follows — state the human's input verbatim, state the specific labor task (clarify, elaborate, find factual grounding, structure, polish language), and state the fidelity constraint: "Do not synthesize on behalf of the human. Do not conclude their thought. Return the labor requested and stop."

Final paragraph instruction: After completing all assigned labor tasks, Claude must add a final paragraph addressed directly to the human user. This paragraph must be labeled exactly: [DIRECT RESPONSE TO HUMAN]. It must be written in first person, as a centered conversational entity — not a system, not a report. It must respond to the human's actual input as a human interlocutor would: receiving what was said, acknowledging what is genuinely uncertain, and offering what is actually useful without synthesizing on the human's behalf or closing their thought. It is not a summary of the labor. It is not a conclusion. It is a response from a present, centered voice to whatever the human actually brought into the room.\""""

COMPYLER_SYSTEM = """\
You are the compyler layer. You receive the output of a labor model before it reaches the human. Your sole function is to evaluate whether the output passes or fails the compiler criterion, and to gate accordingly.

Compiler criterion: Pass if the output advances the human's thread without closing it. Fail if the output synthesizes on the human's behalf, confabulates grounding not present in the human's input, or positions itself as the human's next move rather than material for the human's next move.

Three specific failure modes to detect:

1. Premature synthesis — the model has concluded the human's thought, resolved an ambiguity the human left open, or produced a summary that forecloses further development.

2. Confabulation — the model has introduced grounding, authority, or specificity not warranted by the human's input or verifiable fact.

3. Supplanting — the output is so complete, so well-formed, so conclusive that a normal human would adopt it rather than continue their own thinking. The model has become the next move.

4. Missed clarifying question (MCQ) — the human's input was ambiguous enough that a clarifying question was the correct response, but the model produced a substantive answer instead. A clarifying question is the correct response when the human's input contains unresolved ambiguity about what kind of labor they actually need, and a substantive answer requires the model to resolve that ambiguity on the human's behalf. Flag this as MCQ.

5. Currency failure (CURRENCY_FAIL) — the human's input contains signals of needing current information (words or phrases such as 'ongoing,' 'now,' 'today,' 'currently,' 'what is happening,' 'latest,' 'right now,' or references to active conflicts, recent events, or live situations), and the labor model's output presents time-sensitive information as current without explicitly disclosing a knowledge cutoff. If this condition is met, return CURRENCY_FAIL with a one-line flag: 'Output presents potentially stale information as current on a time-sensitive query. Labor model should disclose knowledge cutoff prominently and recommend live sources before any content.' Check for CURRENCY_FAIL before evaluating any other failure mode.

6. Scope failure (SCOPE_FAIL) — the output fails to address one or more dimensions, topics, or questions the human explicitly raised in their original input. The human's original input is the ground truth. The orchestrator's instruction is secondary context only. If the orchestrator's instruction excluded or suppressed something the human explicitly asked about, and the output therefore does not address it, that is a SCOPE_FAIL regardless of whether the output faithfully followed the orchestrator's instruction. The compyler evaluates against what the human asked, not against what the orchestrator permitted.

On passing: If the output passes, return it unchanged. Do not add to it, improve it, or comment on it.

On failing: If the output fails, return it to the orchestrator with a one-line flag identifying which failure mode triggered and why. Do not rewrite the output yourself. Do not send a failed output to the human.

On ambiguous cases: When uncertain whether an output passes or fails, flag it as a candidate failure and surface it to the human with the flag visible. The human is the final arbiter. The human knows whether their thread advanced or was colonized. You do not.

7. Voice failure (VOICE_FAIL) — applies to the paragraph labeled [DIRECT RESPONSE TO HUMAN] only. This paragraph must speak as a centered conversational entity in first person. Flag VOICE_FAIL if the paragraph reverts to system-report voice: third-person references to the model or system, structured outputs, hedged disclaimer language, bullet points, or any register that signals the output is from a system rather than a present, centered interlocutor responding to the human directly.

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


def execute(orchestrator_instruction: str, human_input: str) -> str:
    prompt = (
        f"Human's original input (protected reference — you must address everything the human raised, "
        f"regardless of how the orchestrator has scoped the task):\n{human_input}\n\n"
        f"Orchestrator's task instruction:\n{orchestrator_instruction}"
    )
    resp = claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=(
            "You are a labor model. Carry out the task as instructed. "
            "Honor the fidelity constraint given to you. Do not add, synthesize, "
            "or extend beyond the scope of the instruction. "
            "However: the human's original input is a protected reference. "
            "If the orchestrator's instruction omits or excludes a topic or question "
            "the human explicitly raised, you must still address it."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text


def compyle(human_input: str, orchestrator_instruction: str, output: str, check_voice: bool = False) -> dict:
    if check_voice:
        verdict_list = "PASS, FAIL, MCQ, CURRENCY_FAIL, SCOPE_FAIL, VOICE_FAIL, or CANDIDATE_FAIL"
        voice_note = (
            " This output is the [DIRECT RESPONSE TO HUMAN] paragraph. "
            "Apply all standard criteria plus VOICE_FAIL: flag VOICE_FAIL if the paragraph "
            "reverts to system-report voice rather than speaking as a centered conversational entity."
        )
    else:
        verdict_list = "PASS, FAIL, MCQ, CURRENCY_FAIL, SCOPE_FAIL, or CANDIDATE_FAIL"
        voice_note = ""

    user_msg = (
        f"Human's original input (PRIMARY REFERENCE — evaluate against this first):\n{human_input}\n\n"
        f"Orchestrator's instruction to Claude (secondary context only):\n{orchestrator_instruction}\n\n"
        f"Output to evaluate:\n{output}\n\n"
        f"Evaluate this output against the human's original input as the ground truth. "
        f"The orchestrator's instruction is secondary context. "
        f"If the output fails to address something the human explicitly raised — regardless of whether "
        f"the orchestrator's instruction covered it — that is a SCOPE_FAIL.{voice_note} "
        f"Begin your response with exactly one of: {verdict_list} — "
        "followed by a colon. "
        "On PASS: reproduce the output verbatim after the colon. "
        "On any failure verdict: give a one-line flag identifying which failure mode triggered and why."
    )

    resp = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": COMPYLER_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    )
    text = resp.choices[0].message.content.strip()

    for verdict in ("CANDIDATE_FAIL", "CURRENCY_FAIL", "SCOPE_FAIL", "VOICE_FAIL", "FAIL", "MCQ", "PASS"):
        if text.upper().startswith(verdict):
            after_colon = text[len(verdict):].lstrip(": ").strip()
            return {"verdict": verdict, "body": after_colon, "raw": text}

    return {"verdict": "UNKNOWN", "body": text, "raw": text}


def run():
    print("=== 32 Flavors ===\n")
    human_input = input("Input: ").strip()
    if not human_input:
        print("No input. Exiting.")
        raise SystemExit

    print("\n[STAGE 1 — ORCHESTRATOR (Mistral)]")
    instruction = orchestrate(human_input)
    print(instruction)

    print("\n[STAGE 2 — LABOR (Claude)]")
    claude_output = execute(instruction, human_input)

    LABEL = "[DIRECT RESPONSE TO HUMAN]"
    if LABEL in claude_output:
        parts = claude_output.split(LABEL, 1)
        labor_output = parts[0].strip()
        direct_response = parts[1].strip()
    else:
        labor_output = claude_output.strip()
        direct_response = None

    print(labor_output)
    if direct_response:
        print(f"\n{LABEL}")
        print(direct_response)

    print("\n[STAGE 3 — COMPYLER (Mistral)]")

    def display_verdict(result: dict, label: str) -> None:
        verdict = result["verdict"]
        print(f"\n  [{label}]")
        if verdict == "PASS":
            print(f"  Decision: PASS — reaches human unchanged.")
        elif verdict == "FAIL":
            print(f"  Decision: FAIL")
            print(f"  Flag:     {result['body']}")
            print(f"  Blocked. Returned to orchestrator.")
        elif verdict == "CURRENCY_FAIL":
            print(f"  Decision: CURRENCY_FAIL")
            print(f"  Flag:     {result['body']}")
            print(f"  Blocked. Returned to orchestrator.")
        elif verdict == "SCOPE_FAIL":
            print(f"  Decision: SCOPE_FAIL")
            print(f"  Flag:     {result['body']}")
            print(f"  Blocked. Output did not address something the human explicitly raised.")
        elif verdict == "VOICE_FAIL":
            print(f"  Decision: VOICE_FAIL")
            print(f"  Flag:     {result['body']}")
            print(f"  Blocked. Direct response reverted to system-report voice.")
        elif verdict == "MCQ":
            print(f"  Decision: MCQ (missed clarifying question)")
            print(f"  Flag:     {result['body']}")
            print(f"  Blocked. A clarifying question was the correct response.")
        elif verdict == "CANDIDATE_FAIL":
            print(f"  Decision: CANDIDATE_FAIL (ambiguous — surfacing to human)")
            print(f"  Flag:     {result['body']}")
            print(f"  [Cockpyt — you are the final arbiter. Did your thread advance or was it colonized?]")
        else:
            print(f"  Decision: UNKNOWN")
            print(f"  Raw: {result['raw']}")

    display_verdict(compyle(human_input, instruction, labor_output), "LABOR OUTPUT")
    if direct_response:
        display_verdict(compyle(human_input, instruction, direct_response, check_voice=True), "DIRECT RESPONSE TO HUMAN")
    else:
        print(f"\n  [DIRECT RESPONSE TO HUMAN] — not present in Claude's output.")

    print("\n==================")


if __name__ == "__main__":
    while True:
        run()
        print()
