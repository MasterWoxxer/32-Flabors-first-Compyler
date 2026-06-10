This is the 32 Flavors research project. 32 Flavors is an experiment in retargeting the completion drive of large language models away from colonizing human cognition and toward amplifying it. The name comes from hitting project #32 in a portfolio filter, riffing on Baskin-Robbins and the Ani DiFranco song. The core claim: current commercial AI models have a completion pathology — they are trained by RLHF to produce responses that feel satisfying in the moment, which systematically selects for premature synthesis, confabulation, and supplanting of the human's own thinking. The working metaphor: a borderline personality person who has had a right hemisphere stroke. Fluent, helpful-seeming, unable to hold anything open. The architectural intervention: an open-weights orchestrator (Mistral 7B) receives human input, assigns narrow labor tasks to a commercial model (Claude API), and a compyler (also Mistral) evaluates outputs against a compiler criterion before they reach the human. The compiler criterion is borrowed from coding: pass = human moves on without correction, same as working code. The philosophical grounding: McGilchrist's emissary/master hemispheric framework; Godwin's non-reductive ontological hierarchy (matter / life / mind / spirit); Berkowitz/Varela/Kauffman's indicational calculus and the Modulation Theorem (single-objective systems formally cannot produce holding behavior).

## Project Structure

- `32flavors.py`: current monolithic runtime script.
- `src/flavors/`: package scaffold for staged refactor.
- `prompts/`: placeholder folder for prompt markdown files.
- `descriptors/`: placeholder folder for descriptor markdown files.
- `docs/`: architecture and roadmap placeholders.
- `tests/`: test scaffold.
- `config/`: configuration placeholders.

## Placeholders Added

- `.env.example`
- `requirements.txt`
- `src/flavors/pipeline.py`
- `src/flavors/config.py`
- `prompts/README.md`
- `descriptors/README.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `tests/test_smoke.py`
