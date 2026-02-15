from itertools import product
import math

# --------------------------------------------------
# Compute width needed for a layer
# --------------------------------------------------
def required_width(bars, spacing):
    if len(bars) == 0:
        return 0
    return sum(bars) + (len(bars) - 1) * spacing


# --------------------------------------------------
# Fit bars into 1 or 2 layers (Condition G + D + E)
# --------------------------------------------------
def fit_bars_in_layers(combo, diameters, beam_width, cover, min_spacing):

    # Build bar list with actual diameters
    bars = []
    for i, count in enumerate(combo):
        bars += [diameters[i]] * count

    if len(bars) == 0:
        return None, None  # no bars → invalid

    # Sort largest → smallest (best packing)
    bars.sort(reverse=True)

    available_width = beam_width - 2 * cover

    # --------------------------------------------------
    # 1) TRY SINGLE LAYER (Condition G)
    # --------------------------------------------------
    width_needed = required_width(bars, min_spacing)

    if width_needed <= available_width:
        if len(bars) >= 2:          # Condition D (no single bar layer)
            return 1, [bars]        # SUCCESS: single layer fits

    # --------------------------------------------------
    # 2) TRY TWO LAYERS
    # --------------------------------------------------
    layer1, layer2 = [], []

    for bar in bars:

        # Try layer 1
        test_layer1 = layer1 + [bar]
        if required_width(test_layer1, min_spacing) <= available_width:
            layer1.append(bar)
            continue

        # Try layer 2
        test_layer2 = layer2 + [bar]
        if required_width(test_layer2, min_spacing) <= available_width:
            layer2.append(bar)
            continue

        # Cannot fit → invalid combo
        return None, None

    # --------------------------------------------------
    # 3) Check layer rules (Condition D + E)
    # --------------------------------------------------
    if len(layer1) == 1 or len(layer2) == 1:
        return None, None  # invalid (single bar layer)

    if abs(len(layer1) - len(layer2)) > 2:
        return None, None  # imbalance

    return 2, [layer1, layer2]


# --------------------------------------------------
# MAIN OPTIMIZER WITH ALL CONDITIONS
# --------------------------------------------------
def min_ast_bars_required(AST_required, beam_width, cover, aggregate_size, diameters):

    areas = [math.pi * (d**2) / 4 for d in diameters]

    # min spacing as per IS456
    min_spacing = max(max(diameters), 20, aggregate_size + 5)

    # --------------------------------------------------
    # Condition F: dynamic max_bars based on beam width
    # --------------------------------------------------
    available_width = beam_width - 2 * cover
    max_d = max(diameters)

    max_bars_single_layer = (available_width + min_spacing) // (max_d + min_spacing)
    max_bars_single_layer = int(max_bars_single_layer)

    max_bars = max_bars_single_layer*2     # for two layers

    # Safety minimum
    if max_bars < 4:
        max_bars = 4

    best_combo = None
    best_ast = float('inf')
    best_layers = None
    best_distribution = None

    # --------------------------------------------------
    # TRY ALL BAR COMBINATIONS
    # --------------------------------------------------
    for combo in product(range(max_bars + 1), repeat=len(diameters)):

        # Skip empty combinations
        if sum(combo) == 0:
            continue

        # --------------------------------------------------
        # Condition A: descending rule
        # --------------------------------------------------
        valid = True
        for i in range(len(combo)):
            for j in range(i+1, len(combo)):
                if combo[i] > 0 and combo[i] < combo[j]:
                    valid = False
        if not valid:
            continue

        # --------------------------------------------------
        # Compute AST of combination
        # --------------------------------------------------
        ast = sum(combo[i] * areas[i] for i in range(len(diameters)))

        if ast < AST_required:
            continue

        # --------------------------------------------------
        # Condition B: largest diameter used must have ≥2 bars
        # --------------------------------------------------
        for i in range(len(combo)):
            if combo[i] > 0:
                if combo[i] < 2:
                    valid = False
                break
        if not valid:
            continue

        # --------------------------------------------------
        # Condition C + D + E + G: beam width + layers
        # --------------------------------------------------
        layers_used, distribution = fit_bars_in_layers(
            combo, diameters, beam_width, cover, min_spacing
        )

        if layers_used is None:
            continue

        # --------------------------------------------------
        # Keep best (minimum AST just above required)
        # --------------------------------------------------
        if ast < best_ast:
            best_ast = ast
            best_combo = combo
            best_layers = layers_used
            best_distribution = distribution

    return best_combo, best_ast, best_layers, best_distribution

# ================================
#            RUN CODE
# ================================
if __name__ == "__main__":

    AST_required = 900      # change as needed
    beam_width = 230        # mm
    cover = 25              # mm (one side)
    aggregate_size = 20     # mm
    diameters = [25, 20, 16, 12, 10, 8, 6]


    combo, ast, layers, distribution = min_ast_bars_required(
        AST_required,
        beam_width,
        cover,
        aggregate_size,
        diameters
    )

    print("=======================================")
    print("            RESULT SUMMARY             ")
    print("=======================================\n")

    if combo is None:
        print("No valid bar combination found!")
    else:
        print(f"Required Ast      : {AST_required:.2f} mm²")
        print(f"Provided Ast      : {ast:.2f} mm²")
        print(f"Layers used       : {layers}")
        print("\nBar Combination (dia : count):")

        
        for d, c in zip(diameters, combo):
            print(f"  {d} mm  :  {c} bars")

        print("\nLayer-wise Distribution:")
        for i, layer in enumerate(distribution, 1):
            print(f"Layer {i}: {layer}")

    print("\n=======================================\n")
