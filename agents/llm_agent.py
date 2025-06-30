import json
import random
import requests
from prompt import generate_prompt
import re
import os
import shutil


class MockLLMAgent:
    """Stub agent that randomly reveals tiles (unchanged)."""

    def __init__(self, api):
        self.api = api
        self.rows = api.game.rows
        self.cols = api.game.cols

    def select_action(self, board_text: str):
        unrevealed = [
            (r, c)
            for r in range(self.rows)
            for c in range(self.cols)
            if not self.api.game.board[r][c].is_revealed
            and not self.api.game.board[r][c].is_flagged
        ]
        if not unrevealed:
            return "terminate", -1, -1
        return "reveal", *random.choice(unrevealed)

    def play_game(self, verbose=True):
        if verbose:
            print("Starting game...")
            print(self.api.get_board())

        while not self.api.is_game_over():
            action, r, c = self.select_action(self.api.get_board())
            if action == "terminate":
                break
            self.api.perform_action(action, r, c)
            if verbose:
                print(f"\nAction: {action} ({r}, {c})")
                print(self.api.get_board())

        return self.api.get_score()


class OllamaLLMAgent:
    """
    Communicates with a local Ollama server (OpenAI-compatible) model and enforces JSON‑only replies.
    """

    def __init__(self, api, model: str = "mistral"):
        self.api = api
        self.model = model
        self.num_mines = api.game.num_mines
        self.rows = api.game.rows
        self.cols = api.game.cols
        self.history: list[str] = []

    def _query_llm(self, prompt: str) -> str:
        """Send prompt to Ollama and return raw text response."""
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False
        }

        print("Using model:", self.model)

        # Clean up __pycache__ folders
        for root, dirs, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
            for d in dirs:
                if d == '__pycache__':
                    shutil.rmtree(os.path.join(root, d))

        try:
            resp = requests.post("http://localhost:11434/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            resp.raise_for_status()

            resp_data = resp.json()
            

            # Ollama returns message directly, not wrapped in choices[]
            message = resp.json()["response"].strip().lower()
            if message:
                return message
            raise ValueError("Missing 'message.content' in Ollama response.")

        except Exception as e:
            print("Error while querying LLM:", e)
            raise

    def select_action(self, board_text: str):
        prompt = generate_prompt(
            board=board_text,
            history=self.history,
            rows=self.rows,
            cols=self.cols,
            total_mines=self.num_mines,
        )

        with open("debug_prompt.txt", "a") as f:
            f.write(prompt)
            f.write("\n\n---\n\n")

        try:
            raw = self._query_llm(prompt)
            print("LLM says:", raw)
            
            # Try to extract JSON from code block
            matches = re.findall(r'```json(.*?)```', raw, re.DOTALL) or \
                      re.findall(r'```(.*?)```', raw, re.DOTALL) 

            if not matches:
                matches = [raw]  # Try entire raw response

            data = json.loads(matches[-1].strip())
            action = data["action"]
            r = int(data["row"])
            c = int(data["col"])
            r = r - 1  # Convert to 0-based indexing
            c = c - 1  # Convert to 0-based indexing
            if action in ("reveal", "flag") and 0 <= r < self.rows and 0 <= c < self.cols:
                print(f"Valid action: {action} ({r}, {c})")
                return action, r, c 

            print("JSON fields out of range, falling back to terminate.")

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print("Invalid JSON or structure:", e)
        except requests.RequestException as e:
            print("HTTP error talking to Ollama:", e)

        return "terminate", -1, -1

    def play_game(self, verbose=True):
        if verbose:
            print("Starting game...")
            print(self.api.get_board())

        while not self.api.is_game_over():
            action, r, c = self.select_action(self.api.get_board())
            if action == "terminate":
                break

            self.api.perform_action(action, r, c)
            self.history.append(f"{action} {r} {c}")

            if verbose:
                print(f"\nAction: {action} ({r}, {c})")
                print(self.api.get_board())

        return self.api.get_score()
