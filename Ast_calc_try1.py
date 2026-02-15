import math
from itertools import product

def area(d):
    return math.pi * (d**2) / 4

def best_bar_combination(required_ast, diameters, max_bars):
    # Pre-calc area for each diameter
    areas = [area(d) for d in diameters]

    best = None
    best_ast = float('inf')

    # Loop in all combinations of number of bars 0..max_bars for each diameter
    for combo in product(range(max_bars+1), repeat=len(diameters)):
        ast = sum(a * n for a, n in zip(areas, combo))

        if ast >= required_ast:  # must be higher side
            # Choose the one with minimum Ast above requirement
            if ast < best_ast:
                best_ast = ast
                best = combo

    return best, best_ast


# --------------------------
# Example input (same as your sheet)
required_ast = 844
diameters = [10, 12, 14, 16, 18, 20]

# max_bars = up to 6 per diameter (you may change)
combo, ast = best_bar_combination(required_ast, diameters, max_bars=3)

print("Best combination (number of bars for each diameter):")
for d, n in zip(diameters, combo):
    print(f"Dia {d} mm → {n} bars")

print("\nAst provided =", ast)
print("Excess steel =", ast - required_ast)