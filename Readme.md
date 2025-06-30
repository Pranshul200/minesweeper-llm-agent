# Minesweeper LLM Agent

This project implements a classic Minesweeper environment in Python, along with a local LLM agent that plays the game autonomously. It supports evaluation across difficulty levels and comparison with a mock baseline agent.

## Features

* Fully custom Minesweeper engine (seed-based, first-move safe)
* `MinesweeperAPI` class interface for board control and agent interaction
* Local LLM agent powered by Mistral via [Ollama](https://ollama.com)
* Evaluation harness over Easy, Medium, Hard settings
* Clean prompt generation with board state, history, and game rules

---

## Setup Instructions

### 1. Clone & Create Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start Ollama (if not running)

```bash
ollama run mistral
```

### 3. Run a Game (Debug)

```bash
python3 tests/test_agent.py
```

### 4. Evaluate Agents

```bash
python3 evaluation/eval_runner.py
```

---

## Folder Structure

```
mine_sweeper/
├── agents/             # Mock + Ollama LLM agents
├── api/                # Interface layer between engine and agent
├── minesweeper/        # Core game logic (engine, board)
├── evaluation/         # Multi-game evaluation runner
├── tests/              # Unit and integration tests
├── prompt.py           # Generates few-shot prompt with history
├── requirements.txt    # Python dependencies
├── results_*.json      # Saved evaluation results
└── README.md
```

---

## Agents

### MockLLMAgent

A baseline agent that randomly selects from unrevealed safe tiles.

### OllamaLLMAgent

Uses a local Mistral model via Ollama.

* Passes current board and move history as text
* Receives next move in the format: `reveal 2 3` or `flag 1 1`

---

## Prompting Strategy

Prompts include:

* Text description of rules
* Board state (5x5, etc)
* Explicit instruction to respond in one line



---

## Evaluation

Run `eval_runner.py` to test both agents over:

* Easy: 5x5, 3 mines
* Medium: 6x6, 6 mines
* Hard: 8x8, 10 mines

Each result is saved as:

* `results_mock_easy.json`
* `results_llm_hard.json`

Sample Output:

```json
{
  "agent": "llm",
  "rows": 5,
  "cols": 5,
  "mines": 3,
  "total_games": 100,
  "wins": 30,
  "win_rate": 0.3,
  "avg_revealed": 12.1,
  "avg_steps": 13.2,
  "avg_runtime_sec": 0.002
}
```

---

## Known Limitations


* The LLM (Mistral 7B) performs reasonably on easy boards but struggles significantly as board complexity increases.

* It lacks chain-of-thought reasoning, spatial deduction, and working memory, making it prone to guessing.

* It sometimes produces invalid or repeated moves, despite strict prompt format and postprocessing.

* It fails to resolve ambiguities logically, and lacks the capacity to backtrack or simulate alternative outcomes.

* Response formatting occasionally breaks (explanations instead of clean JSON).

---


