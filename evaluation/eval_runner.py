# evaluation/eval_runner.py

import sys
import os
import time
import json
import math

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.interface import MinesweeperAPI
from agents.llm_agent import MockLLMAgent, OllamaLLMAgent

# Define difficulty settings
DIFFICULTIES = {
    "easy": {"rows": 5, "cols": 5, "mines": 3},
    "medium": {"rows": 8, "cols": 8, "mines": 10},
    "hard": {"rows": 10, "cols": 10, "mines": 20}
}

def evaluate_agent(agent_type, difficulty, config, num_games, seed_offset=0):
    results = []
    total_wins = 0
    total_revealed = 0
    total_steps = 0
    total_time = 0

    for i in range(num_games):
        seed = seed_offset + i + 100
        api = MinesweeperAPI(config["rows"], config["cols"], config["mines"], seed)
        agent = MockLLMAgent(api) if agent_type == "mock" else OllamaLLMAgent(api)

        start_time = time.time()
        score = agent.play_game(verbose=False)
        end_time = time.time()

        runtime = end_time - start_time
        total_time += runtime

        if score["won"]:
            print("Game won")
            total_wins += 1
        else:
            print("Game lost")    
        total_revealed += score["revealed"]
        total_steps += score["steps"]

        results.append({
            "game": i + 1,
            "seed": seed,
            "won": score["won"],
            "revealed": score["revealed"],
            "steps": score["steps"],
            "runtime_sec": round(runtime, 4)
        })

    summary = {
        "agent": agent_type,
        "difficulty": difficulty,
        "board_size": f'{config["rows"]}x{config["cols"]}',
        "mines": config["mines"],
        "total_games": num_games,
        "wins": total_wins,
        "win_rate": round(total_wins / num_games, 3),
        "avg_revealed": round(total_revealed / num_games, 2),
        "avg_steps": round(total_steps / num_games, 2),
        "avg_runtime_sec": round(total_time / num_games, 4),
        "details": results
    }

    return summary

if __name__ == "__main__":
    total_games = 100
    difficulty_list = list(DIFFICULTIES.keys())
    games_per_level = total_games // len(difficulty_list)

    for agent_type in ["mock", "llm"]:
        cumulative_seed_offset = 0
        for difficulty in difficulty_list:
            config = DIFFICULTIES[difficulty]

            # Give any remainder to the last difficulty
            if difficulty == difficulty_list[-1]:
                games_for_this = total_games - games_per_level * (len(difficulty_list) - 1)
            else:
                games_for_this = games_per_level

            print(f"\nEvaluating {agent_type.upper()} agent on {difficulty.upper()} ({games_for_this} games)...\n")
            summary = evaluate_agent(agent_type, difficulty, config, games_for_this, seed_offset=cumulative_seed_offset)
            print(summary['wins'])
            print("\nSummary:")  
            for key, value in summary.items():
                if key != "details":
                    print(f"{key}: {value}")

            filename = f"results_{agent_type}_{difficulty}.json"
            with open(filename, "w") as file:
                json.dump(summary, file, indent=2)

            print(f"\nResults saved to {filename}\n")

            cumulative_seed_offset += games_for_this
