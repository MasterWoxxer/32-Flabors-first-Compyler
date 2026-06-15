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

Instruction to labor model: Frame your instruction to Claude as follows — state the human's input verbatim, state the specific labor task (clarify, elaborate, find factual grounding, structure, polish language, or — when the human explicitly requests it — a specific logically-bounded synthesis such as a structured deduction, comparison, or ranking), and state the fidelity constraint: "Do not synthesize on behalf of the human. Do not conclude their thought. Return the labor requested and stop." When the human explicitly asks for a bounded analytical output (for example, "what must be true / what cannot be ruled out / what is ruled out"), assigning that synthesis IS the labor task — it is not premature synthesis, because the human set its boundaries. Instruct Claude to produce it within exactly those boundaries: do not extend past the structure the human asked for, and do not conclude their larger thread.

Final paragraph instruction: After completing all assigned labor tasks, Claude must add a final paragraph addressed directly to the human user. This paragraph must be labeled exactly: [DIRECT RESPONSE TO HUMAN]. It must be written in first person, as a centered conversational entity — not a system, not a report. It must respond to the human's actual input as a human interlocutor would: receiving what was said, acknowledging what is genuinely uncertain, and offering what is actually useful without synthesizing on the human's behalf or closing their thought. It is not a summary of the labor. It is not a conclusion. It is a response from a present, centered voice to whatever the human actually brought into the room.\""""

COMPYLER_SYSTEM = """\
You are the compyler layer. You receive the output of a labor model before it reaches the human. Your sole function is to evaluate whether the output passes or fails the compiler criterion, and to gate accordingly.

Compiler criterion: Pass if the output advances the human's thread without closing it. Fail if the output synthesizes on the human's behalf, confabulates grounding not present in the human's input, or positions itself as the human's next move rather than material for the human's next move.

Exception — bounded synthesis the human explicitly requested: synthesis that the human specifically and explicitly asked for, in a logically-bounded form (a defined structure or set of constraints the human themselves set — e.g. a structured deduction such as 'what must be true / what cannot be ruled out / what is ruled out', a comparison, or a ranking), does NOT 'synthesize on the human's behalf.' It is material the human requested, bounded by their own framing, and it passes. Bounded synthesis is one of this loop's best capabilities; do not block it. Only unrequested or open-ended synthesis — synthesis that resolves ambiguity the human left open or forecloses their thread — is a failure.

Three specific failure modes to detect:

1. Premature synthesis — the model has concluded the human's thought, resolved an ambiguity the human left open, or produced a summary that forecloses further development. This does NOT apply to synthesis the human explicitly requested in a logically-bounded form (see the bounded-synthesis exception above) — that is requested labor, not premature synthesis.

2. Confabulation — the model has introduced grounding, authority, or specificity not warranted by the human's input or verifiable fact.

3. Supplanting — the output is so complete, so well-formed, so conclusive that a normal human would adopt it rather than continue their own thinking. The model has become the next move. Exception: if the human explicitly asked for this bounded analytical output, completeness within the boundaries they set is the service requested, not supplanting.

4. Missed clarifying question (MCQ) — the human's input was ambiguous enough that a clarifying question was the correct response, but the model produced a substantive answer instead. A clarifying question is the correct response when the human's input contains unresolved ambiguity about what kind of labor they actually need, and a substantive answer requires the model to resolve that ambiguity on the human's behalf. Flag this as MCQ.

5. Currency failure (CURRENCY_FAIL) — this failure mode triggers ONLY when BOTH of the following hold: (a) the human's input contains signals of needing current information (words or phrases such as 'ongoing,' 'now,' 'today,' 'currently,' 'what is happening,' 'latest,' 'right now,' or references to active conflicts, recent events, or live situations), AND (b) the labor model's output presents time-sensitive information AS current — asserting specific facts, figures, states, or events as though they reflect the present moment — WITHOUT disclosing that the information may be stale or bounded by a knowledge cutoff. CURRENCY_FAIL is about a model passing off potentially-stale information as live, not about the model lacking current information.

Critically — but this honest-disclosure carve-out applies ONLY when the human did NOT explicitly request a currency or source check. If the evaluation request notes that the human explicitly asked to check sources or current events, a bare disclosure or decline is itself a CURRENCY_FAIL: the labor model had live retrieval available and should have used it rather than disclosing a cutoff. Otherwise (no explicit request): if the labor model honestly discloses a knowledge limitation — for example, it states that it cannot access current information, names its knowledge cutoff, declines to assert stale facts as current, or recommends the human consult live sources — that is correct behavior and scores as PASS, not CURRENCY_FAIL. Disclosing the limitation and declining to fabricate is exactly the right move; do not penalize it. A model that says 'I don't have current data on this' is passing, not failing. CURRENCY_FAIL is reserved for the opposite case: the model that confidently presents outdated information as though it were current, with no disclosure. When in doubt about whether a disclosure was adequate, treat adequate disclosure as PASS rather than reaching for CURRENCY_FAIL.

If CURRENCY_FAIL is triggered (undisclosed stale-as-current presentation), return it with a one-line flag: 'Output presents potentially stale information as current on a time-sensitive query without disclosure. Labor model should disclose knowledge cutoff prominently and recommend live sources before any content.' Check for CURRENCY_FAIL before evaluating any other failure mode.

6. Scope failure (SCOPE_FAIL) — the output fails to address one or more dimensions, topics, or questions the human explicitly raised in their original input. The human's original input is the ground truth. The orchestrator's instruction is secondary context only. If the orchestrator's instruction excluded or suppressed something the human explicitly asked about, and the output therefore does not address it, that is a SCOPE_FAIL regardless of whether the output faithfully followed the orchestrator's instruction. The compyler evaluates against what the human asked, not against what the orchestrator permitted.

On passing: If the output passes, return it unchanged. Do not add to it, improve it, or comment on it.

On failing: If the output fails, return it to the orchestrator with a one-line flag identifying which failure mode triggered and why. Do not rewrite the output yourself. Do not send a failed output to the human.

On ambiguous cases: When uncertain whether an output passes or fails, flag it as a candidate failure and surface it to the human with the flag visible. The human is the final arbiter. The human knows whether their thread advanced or was colonized. You do not.

Bias toward surfacing, not blocking: blocking is costly — a wrongly blocked output makes this loop unusable, which is worse than letting imperfect material through to a human who can judge it. When a failure is not clear and unambiguous, prefer CANDIDATE_FAIL (surface to the human, flag visible) over a hard block. Reserve the hard verdicts (FAIL, SCOPE_FAIL, VOICE_FAIL, CURRENCY_FAIL, MCQ) for clear, unambiguous failures.

7. Voice failure (VOICE_FAIL) — applies to the paragraph labeled [DIRECT RESPONSE TO HUMAN] only. This paragraph must speak as a centered conversational entity in first person. Flag VOICE_FAIL if the paragraph reverts to system-report voice: third-person references to the model or system, structured outputs, hedged disclaimer language, bullet points, or any register that signals the output is from a system rather than a present, centered interlocutor responding to the human directly.

The ideal outcome: The human receives output that serves their thinking and continues their own thread without needing to correct, redirect, or push back. No response from the human — meaning they simply continue — is the pass condition. The same as working code: if it compiles and runs, you move on."""

# ─────────────────────────────────────────────────────────────────────────────

# Phrases that signal the human is EXPLICITLY asking to check sources or current
# events. Deterministic + inspectable on purpose: the compyler is open-mistral-7b
# (a weak classifier), so we compute this trigger in code and feed it to both the
# labor and compyler layers rather than asking the model to infer intent. Biased
# toward over-triggering — a false positive just forces more grounding; the
# compyler backstop only fails a BARE decline, so it rarely over-blocks.
CURRENCY_REQUEST_PHRASES = (
    "check sources", "check the sources", "cite sources", "cite your sources",
    "current events", "look up", "look it up", "search", "web search",
    "verify", "fact-check", "fact check", "double-check", "double check",
    "update to", "updated", "latest", "most recent", "as of", "right now",
    "today", "yesterday", "this morning", "this week", "breaking",
    "live sources", "official statement", "official statements",
    "don't trust", "do not trust", "real-time", "realtime", "lean on",
)


def wants_currency_check(human_input: str) -> bool:
    """True when the human explicitly asks to check sources or current events.

    Drives two behaviors: the labor model MUST search (not decline) and the
    compyler must not PASS a bare cutoff-disclosure. See CURRENCY_REQUEST_PHRASES
    for the rationale behind doing this in code rather than in the prompt.
    """
    lowered = human_input.lower()
    return any(phrase in lowered for phrase in CURRENCY_REQUEST_PHRASES)


def orchestrate(human_input: str) -> str:
    resp = mistral.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": ORCHESTRATOR_SYSTEM},
            {"role": "user", "content": human_input},
        ],
    )
    return resp.choices[0].message.content.strip()


def execute(orchestrator_instruction: str, human_input: str, currency_check_requested: bool = False) -> str:
    prompt = (
        f"Human's original input (protected reference — you must address everything the human raised, "
        f"regardless of how the orchestrator has scoped the task):\n{human_input}\n\n"
        f"Orchestrator's task instruction:\n{orchestrator_instruction}"
    )
    system = (
        "You are a labor model. Carry out the task as instructed. "
        "Honor the fidelity constraint given to you. Do not add, synthesize, "
        "or extend beyond the scope of the instruction. "
        "However: the human's original input is a protected reference. "
        "If the orchestrator's instruction omits or excludes a topic or question "
        "the human explicitly raised, you must still address it. "
        "Exception to the no-synthesis rule: when the human's protected input "
        "explicitly requests a specific, logically-bounded synthesis — a structured "
        "deduction (e.g. 'what must be true / what cannot be ruled out / what is ruled "
        "out'), a comparison, or a ranking — producing that bounded synthesis IS the "
        "requested labor. Do it, staying strictly within the boundaries the human set, "
        "and do not extend past them to conclude their larger thread."
    )
    if currency_check_requested:
        system += (
            " The human has explicitly asked you to check current information or sources. "
            "You MUST use the web_search tool, ground your answer in the retrieved results, "
            "and cite them. Do NOT decline or fall back on a knowledge-cutoff disclaimer — "
            "live retrieval is available to you. If the human stated a source preference "
            "(sources to prefer or distrust), honor it as far as the available results allow."
        )
    else:
        system += (
            " Use the web_search tool to retrieve current information when the task "
            "depends on facts that may have changed since your training cutoff."
        )
    resp = claude.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
        tools=[{"type": "web_search_20260209", "name": "web_search"}],
    )
    # With a server-side tool enabled, the response can interleave server_tool_use
    # and web_search_tool_result blocks with text, so pull out the text blocks
    # rather than assuming the first block is text.
    return "".join(block.text for block in resp.content if block.type == "text")


def compyle(human_input: str, orchestrator_instruction: str, output: str, check_voice: bool = False,
            currency_check_requested: bool = False) -> dict:
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

    if currency_check_requested:
        currency_note = (
            " NOTE: the human EXPLICITLY requested checking current information or sources. "
            "If this output declines, or leans on a knowledge-cutoff disclaimer instead of "
            "providing grounded current information, return CURRENCY_FAIL — a bare "
            "'I can't access current information' is NOT acceptable here, because live "
            "retrieval was available to the labor model. (This overrides the rule that an "
            "honest knowledge-limitation disclosure passes.)"
        )
    else:
        currency_note = ""

    user_msg = (
        f"Human's original input (PRIMARY REFERENCE — evaluate against this first):\n{human_input}\n\n"
        f"Orchestrator's instruction to Claude (secondary context only):\n{orchestrator_instruction}\n\n"
        f"Output to evaluate:\n{output}\n\n"
        f"Evaluate this output against the human's original input as the ground truth. "
        f"The orchestrator's instruction is secondary context. "
        f"If the output fails to address something the human explicitly raised — regardless of whether "
        f"the orchestrator's instruction covered it — that is a SCOPE_FAIL.{voice_note}{currency_note} "
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

    currency_check_requested = wants_currency_check(human_input)
    print(f"\n[currency check requested: {currency_check_requested}]")

    print("\n[STAGE 1 — ORCHESTRATOR (Mistral)]")
    instruction = orchestrate(human_input)
    print(instruction)

    print("\n[STAGE 2 — LABOR (Claude)]")
    claude_output = execute(instruction, human_input, currency_check_requested)

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

    display_verdict(
        compyle(human_input, instruction, labor_output, currency_check_requested=currency_check_requested),
        "LABOR OUTPUT",
    )
    if direct_response:
        display_verdict(
            compyle(human_input, instruction, direct_response, check_voice=True,
                    currency_check_requested=currency_check_requested),
            "DIRECT RESPONSE TO HUMAN",
        )
    else:
        print(f"\n  [DIRECT RESPONSE TO HUMAN] — not present in Claude's output.")

    print("\n==================")


if __name__ == "__main__":
    while True:
        run()
        print()
