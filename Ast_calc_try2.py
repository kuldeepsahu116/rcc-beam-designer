from itertools import product
import math

def min_ast_bars_required(AST_required,diameters,max_bars):

    areas = [math.pi * (d**2) / 4 for d in diameters]

    def is_valid(combo):
        # condition 1: enforce descending rule with 0 allowed
        for i in range(len(combo)):
            for j in range(i+1, len(combo)):
                # if smaller dia has bars but larger dia has less bars => invalid
                if combo[i] > 0 and combo[i] < combo[j]:
                    return False
        # Condition 2: Largest diameter actually used must have ≥2 bars
        for i in range(len(combo)):
            if combo[i] > 0:              # first non-zero = largest dia used
                if combo[i] < 2:          # must be >= 2
                    return False
                break
        return True

    best_combo = None
    best_ast = float('inf')

    for combo in product(range(max_bars+1), repeat=len(diameters)):

        if not is_valid(combo):
            continue

        ast = sum(combo[i] * areas[i] for i in range(len(combo)))

        if ast >= AST_required and ast < best_ast:
            best_ast = ast
            best_combo = combo

    return best_combo, best_ast


# --------------------------
# Example input (same as your sheet)
required_ast = 900
diameters = [30, 25, 20, 16, 12, 10]
max_bars = 8


# max_bars = up to 6 per diameter (you may change)
combo, ast = min_ast_bars_required(required_ast,diameters,max_bars)

print("Best combination (number of bars for each diameter):")
for d, n in zip(diameters, combo):
    print(f"Dia {d} mm → {n} bars")

print("\nAst provided =", ast)
print("Excess steel =", ast - required_ast)