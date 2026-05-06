from fastapi import FastAPI
from pydantic import BaseModel
from main import genetic_algorithm

app = FastAPI()

class Params(BaseModel):
    item: str
    stat: str
    level: int
    pop_size: int
    generations: int
    duration_min: int

@app.post("/run")
def run_algo(params: Params):
    best_solution = genetic_algorithm(
        item=params.item,
        focused_stat=params.stat,
        level_max=params.level,
        pop_size=params.pop_size,
        generations=params.generations,
        duration_min=params.duration_min
    )

    best = best_solution[0]

    return {
        "fitness": best_solution[1],
        "duration": best.duration,
        "recipe": [[ing["name"] for ing in row] for row in best.recipe]
    }