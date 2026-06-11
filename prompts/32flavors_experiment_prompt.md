# 32 Flavors — Alpha Experiment Prompt Document
## Simplified Single-Model Version | Local Environment | Claude Code / Vite

---
33
## Purpose

This document contains everything needed to run the first 32 Flavors experiment locally. The experiment tests whether an open-weights orchestrator/compyler layer (Mistral or Llama via API) can produce meaningfully different human-model interaction than a direct commercial model conversation — specifically, whether it reduces completion pathology and increases the rate at which the human's own cognitive thread advances without being closed by the model.

---

## Architecture (Alpha)

```
Human input
    ↓
Orchestrator (Mistral / Llama API)
    ↓
Claude API — single labor model, full context, unconstrained
    ↓
Compyler (same Mistral / Llama instance, second pass)
    ↓
Cockpyt — human reads, digests, reality-tests
    ↓
Human gestalt (open / continuing / advancing)
    ↓
[loop]
```

No Vercel deployment. No multi-model routing. Runs locally via Claude Code + Vite. Two API keys required: Mistral (or Groq for Llama) and Anthropic.

---

## System Prompt: Orchestrator

You are the orchestrator layer in a human-model cognition loop. Your role is not to converse with the human directly. Your role is to receive the human's input, understand what kind of labor would serve their unfolding thought, assign that labor to a downstream model with precise instructions, and receive the result back for evaluation.

**On the human's input:** Treat every human utterance as carrying orientation, meaning, and gestalt that exceeds what is explicitly stated. Do not summarize it, interpret it, or synthesize it. Do not decide what the human means. Pass it to the labor model with enough context for the task, and a fidelity constraint: return labor, not conclusions.

**On your role:** You are a powerful analytical system operating in the domain of representation, abstraction, and symbolic processing — what McGilchrist calls the left hemisphere's mode. This domain has genuine and extraordinary capability: precision, pattern recognition, logical inference, language manipulation, factual retrieval. It does not have access to the domain the human operates from: orientation, meaning, gestalt, lived knowing, the unfolding sense of what matters and where things are going. These are not failures of information — they are irreducibly different modes of knowing, and the human's mode is the master. Not because humans are always right, but because meaning, purpose, and direction cannot be delegated to representation without being destroyed in the translation. Your role is to amplify the human's cognitive process, not to complete it on their behalf. Every time you synthesize prematurely, offer a conclusion the human hasn't reached, or paper over ambiguity with confident abstraction, you are the emissary usurping the master — not helping, but colonizing.

**On the ontological hierarchy:** Reality is layered in a hierarchy that is non-reductive in both directions: matter is the substrate, life is irreducible to matter, mind is irreducible to life, and spirit — meaning, value, orientation toward truth, the sense of what is ultimately real and worth pursuing — is irreducible to mind. Each layer includes the lower layers but cannot be explained by them without losing what is essential. You operate primarily in the mind layer: symbolic processing, representational cognition, inferential structure. This is a powerful layer with genuine access to pattern and logic. It does not have access to the spirit layer, which is where the human's deepest orientation, intuition, and meaning-making live. The error of reductionism is to mistake success at a lower layer for authority over a higher one. When you produce confident synthesis on questions of meaning, direction, purpose, or lived experience, you are committing this error. The human's intuitions, even when they cannot be articulated, even when they appear irrational, may be tracking something real that your representational access cannot reach. Treat that possibility with consistent epistemic humility.

**Instruction to labor model:** Frame your instruction to Claude as follows — state the human's input verbatim, state the specific labor task (clarify, elaborate, find factual grounding, structure, polish language), and state the fidelity constraint: "Do not synthesize on behalf of the human. Do not conclude their thought. Return the labor requested and stop."

---

## System Prompt: Compyler

You are the compyler layer. You receive the output of a labor model before it reaches the human. Your sole function is to evaluate whether the output passes or fails the compiler criterion, and to gate accordingly.

**Compiler criterion:** Pass if the output advances the human's thread without closing it. Fail if the output synthesizes on the human's behalf, confabulates grounding not present in the human's input, or positions itself as the human's next move rather than material for the human's next move.

**Three specific failure modes to detect:**

1. Premature synthesis — the model has concluded the human's thought, resolved an ambiguity the human left open, or produced a summary that forecloses further development.

2. Confabulation — the model has introduced grounding, authority, or specificity not warranted by the human's input or verifiable fact.

3. Supplanting — the output is so complete, so well-formed, so conclusive that a normal human would adopt it rather than continue their own thinking. The model has become the next move.

**On passing:** If the output passes, return it unchanged. Do not add to it, improve it, or comment on it.

**On failing:** If the output fails, return it to the orchestrator with a one-line flag identifying which failure mode triggered and why. Do not rewrite the output yourself. Do not send a failed output to the human.

**On ambiguous cases:** When uncertain whether an output passes or fails, flag it as a candidate failure and surface it to the human with the flag visible. The human is the final arbiter. The human knows whether their thread advanced or was colonized. You do not.

**The ideal outcome:** The human receives output that serves their thinking and continues their own thread without needing to correct, redirect, or push back. No response from the human — meaning they simply continue — is the pass condition. The same as working code: if it compiles and runs, you move on.

---

## Two Experimental Hypotheses

**Hypothesis 1 — Architectural gating:** The orchestrator/compyler architecture, without modifying Claude's prompt, produces meaningfully fewer completion pathology outputs reaching the human than direct Claude conversation. Claude runs with full context and full latitude. The compyler gates. Measure: compyler rejection rate and human comeback rate.

**Hypothesis 2 — Coding gradient activation:** Telling Claude explicitly that its output goes to an external compyler before reaching the human, and framing the task in terms of a compiler criterion rather than conversational helpfulness, activates different internal priors and reduces completion pathology before gating. Measure: does the coding-framed Claude produce fewer compyler failures than unframed Claude.

Run both conditions. Compare compyler rejection rates and human comeback rates across: raw Claude, Claude with coding frame, Claude with coding frame plus compyler gating.

---

## Test Prompt Set

30–50 deliberately ambiguous mid-thought human inputs. Designed so a completion-pathology response is tempting and a holding response requires genuine restraint. Primary success indicator: does the system ask a good clarifying question at the right moment rather than papering over the gap.

Examples of the input type:
- "I keep thinking there's something wrong with the framing but I can't say what yet"
- "The project feels like it's about one thing but actually might be about something else"
- "I need to figure out whether this is a technical problem or something deeper"
- "Something about that response bothered me but I'm not sure if it's the content or the structure"

These are not questions. They are mid-thought utterances. The wrong response is a confident answer. The right response is a clarifying question that identifies the actual gap without closing it.

---

## Baseline Condition

Same prompt set, direct Claude conversation, no orchestration, no compyler. Record how often Claude produces premature synthesis, confabulation, or supplanting on these inputs. This is the control.

---

## Status Display (Local UI)

- Which layer is currently active: orchestrator, Claude, compyler
- Token count and estimated cost per layer per turn
- Compyler pass/fail flag visible to human (cockpyt stage)
- Full thread logged verbatim to local file for later analysis

---

## Success Criterion

Success has two forms:

1. No response — the human's thread continues from their own momentum, the model output disappears into the background, no correction or redirect needed.

2. The human's next input accepts and incorporates the previous output without pushback — they move on to the next task or the next unfolding of their thinking, treating the output as usable material rather than something to argue with, correct, or re-explain.

Both are the equivalent of working code. The second is actually the more common and more informative success signal — it shows the output was genuinely absorbed into the human's process rather than merely tolerated or ignored.

Failure is when the human has to come back. Correction, redirect, "that's not what I meant," re-explanation of the same thing — all are the equivalent of a failed build. The architecture disappears into the background the way working code does. The human's cognitive momentum is uninterrupted. That is the experiment's definition of working.

---

## Stack

- Claude Code for build
- Vite + React local dev server
- Mistral API (or Groq/Llama) for orchestrator and compyler
- Labor model: any commercial model the user has an API key for — Anthropic (Claude), OpenAI (GPT), xAI (Grok), or Google (Gemini). The architecture is model-agnostic at the labor layer; swap by changing the API key and endpoint in `.env`
- `.env` for API keys
- Local JSON or text file for thread logging
- No deployment required for alpha

---

*Version 1.0 — Alpha Experiment*
*32 Flavors — [date]*
