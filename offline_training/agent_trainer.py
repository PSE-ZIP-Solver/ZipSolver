import pickle
import random
from pathlib import Path

from offline_training.board_generator import BoardGenerator

BOARD_SIZE = 8
NR_EVALUATION_BOARDS = 10_000
OUTPUT_DIR = Path("offline_training/evaluation_boards/8x8(final_sets)")


def generate_and_save_set(name, min_walls, max_walls, min_waypoints, max_waypoints, filename):
    output_path = OUTPUT_DIR / filename

    if output_path.exists():
        print(f"\n{name}: already exists -> {output_path}")
        return

    print(
        f"\nGenerating {name}: {NR_EVALUATION_BOARDS} boards, "
        f"walls {min_walls}-{max_walls}, "
        f"waypoints {min_waypoints}-{max_waypoints}"
    )

    boards = []

    for index in range(NR_EVALUATION_BOARDS):
        nr_of_walls = random.randint(min_walls, max_walls)
        nr_of_waypoints = random.randint(min_waypoints, max_waypoints)

        boards.append(
            BoardGenerator.generate(
                BOARD_SIZE,
                nr_of_waypoints,
                nr_of_walls,
                1,
            )[0]
        )

        if (index + 1) % 500 == 0 or index + 1 == NR_EVALUATION_BOARDS:
            print(f"Generated {index + 1}/{NR_EVALUATION_BOARDS}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as file:
        pickle.dump(boards, file)

    print(f"Saved -> {output_path}")


if __name__ == "__main__":
    generate_and_save_set(
        "8x8 Final Set 2 / Sparse",
        0,
        16,
        0,
        20,
        "8x8-final-eval-set2-sparse-0to16walls-0to20wp-10000boards.pkl",
    )

    generate_and_save_set(
        "8x8 Final Set 3 / Dense",
        33,
        49,
        42,
        62,
        "8x8-final-eval-set3-dense-33to49walls-42to62wp-10000boards.pkl",
    )

    print("\nDone. Both final 8x8 evaluation sets were generated/saved.")
