from flask import Flask, render_template, jsonify
from main import genetic_algorithm

FIRST_INGREDIENT_QUALITY = 2 #1, 2 ou 3 étoiles
SECOND_INGREDIENT_QUALITY = 2 #1, 2 ou 3 étoiles

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run")
def run_algo():
    best_solution = genetic_algorithm()

    result = {
        "score": best_solution[1],
        "recipe": best_solution[0].display_recipe(),
        "boost": best_solution[0].give_boost_array(),
        "stats": best_solution[0].show_stats(),
        "link": "https://wynnbuilder-beta.github.io/crafter/#"
                + best_solution[0].encode_wynn_craft_hash(
                    [FIRST_INGREDIENT_QUALITY, SECOND_INGREDIENT_QUALITY]
                )
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)