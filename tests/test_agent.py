import shutil
import os

# Clean all __pycache__ folders recursively from project root
for root, dirs, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))):
    for d in dirs:
        if d == '__pycache__':
            shutil.rmtree(os.path.join(root, d))
open("debug_prompt.txt", "w").close()
# ...existing code...
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.interface import MinesweeperAPI
from agents.llm_agent import OllamaLLMAgent

if __name__ == "__main__":
    print("Initializing MinesweeperAPI...")
    
    api = MinesweeperAPI(rows=5, cols=5, num_mines=3, seed=123)

    print("\nCreating Ollama LLM Agent...")
    agent = OllamaLLMAgent(api)

    print("\nStarting Game Play...\n")
    result = agent.play_game(verbose=True)

    print("\nGame Finished")
    print("Agent Result:", result)