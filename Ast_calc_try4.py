from itertools import product
import math

# --------------------------------------------------
# Compute required width for bars in a single layer
# --------------------------------------------------
def required_width(bars, spacing):
    if len(bars) == 0:
        return 0
    return sum(bars) + (len(bars) - 1) * spacing

# --------------------------------------------------
# max Ast in one layer
# --------------------------------------------------
def ast_max_one_layer(diameters, beam_width, aggregate_size,cover):
    spacing=max(max(diameters),20,aggregate_size+5)
    width_left = beam_width-2*cover
    ast_total = 0

    for d in diameters:
        
        count = int((width_left + spacing) // (d + spacing))
        ast_total += count * math.pi*d*d/4
        width_left -= count * (d + spacing)
    
    return ast_total

# --------------------------------------------------
# Fit bars into ONE layer only
# --------------------------------------------------
def fit_bars_in_layers(combo, diameters, beam_width, cover,aggregate_size):

    used_diams = [diameters[i] for i in range(len(combo)) if combo[i] > 0]
    if used_diams:
        max_d = max(used_diams)
    else:
        max_d = 0

    min_spacing=max(max_d, 20, aggregate_size + 5)

    # Expand bar list (e.g., [20,20,16])
    bars = []
    for i, count in enumerate(combo):
        bars += [diameters[i]] * count

    if len(bars) == 0:
        return None, None

    # Sort descending for best packing
    bars.sort(reverse=True)

    available_width = beam_width - 2 * cover

    # Width required for single layer
    width_needed = required_width(bars, min_spacing)

    # Must fit and must not be single bar
    if width_needed <= available_width and len(bars) >= 2:
        return 1, [bars]

    return None, None

# --------------------------------------------------
# Fit bars into TWO layer only
# --------------------------------------------------
def fit_two_layers(combo, diameters, beam_width, cover,aggregate_size):
    for i, count in enumerate(combo):
        if count!=0:
            d=diameters[i]
    min_spacing=max(d, 20, aggregate_size + 5)

    # Create bar list
    bars = []
    for i, count in enumerate(combo):
        bars += [diameters[i]] * count

    bars.sort(reverse=True)
    available_width = beam_width - 2 * cover

    layer1, layer2 = [], []

    for bar in bars:

        # Try layer 1
        test1 = layer1 + [bar]
        if required_width(test1, min_spacing) <= available_width:
            layer1.append(bar)
            continue

        # Try layer 2
        test2 = layer2 + [bar]
        if required_width(test2, min_spacing) <= available_width:
            layer2.append(bar)
            continue

        # Cannot fit in two layers
        return None, None

    # Reject if any layer has only 1 bar
    if len(layer1) <= 1 or len(layer2) <= 1:
        return None, None

    # Layers can differ max by 2 bars
    if abs(len(layer1) - len(layer2)) > 1:
        return None, None

    return 2, [layer1, layer2]

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def min_ast_by_bars_required(AST_required, beam_width, cover, aggregate_size, diameters):

    areas = [math.pi * (d**2) / 4 for d in diameters]
    Max_Ast=ast_max_one_layer(diameters,beam_width,aggregate_size,cover)

    
    Max_bars_each = []
    for d in diameters:

     # Minimum spacing required (IS456)
        min_spacing = max(d, 20, aggregate_size + 5)
        max_n = int((beam_width-min_spacing)//(d+min_spacing))
        if max_n < 2:
            max_n = 2
        if AST_required>Max_Ast:
            max_n=max_n*2
        Max_bars_each.append(max_n)
    
    best_combo = None
    best_ast = float('inf')
    best_distribution = None

    # --------------------------------------------
    # Try all combinations
    # --------------------------------------------
    for combo in product(*[range(l+1) for l in Max_bars_each]):

        if sum(combo) == 0:
            continue

        # Condition A: descending usage rule
        valid = True
        for i in range(len(combo)):
            for j in range(i + 1, len(combo)):
                if combo[i] > 0 and combo[i] <= combo[j]:
                    valid = False
        if not valid:
            continue

        # Compute AST for combination
        ast = sum(combo[i] * areas[i] for i in range(len(diameters)))
        if ast < AST_required:
            continue

        # Condition B: largest diameter used must have >=2 bars
        valid = True
        for i in range(len(combo)):
            if combo[i] > 0:
                if combo[i] < 2:
                    valid = False
                break
        if not valid:
            continue

        # Try single-layer first
        if AST_required<=Max_Ast:
            layers_used, distribution = fit_bars_in_layers(
                combo, diameters, beam_width, cover,aggregate_size)

        # If single-layer fails → try two-layer
        elif AST_required>Max_Ast:
            layers_used, distribution = fit_two_layers(
                combo, diameters, beam_width, cover,aggregate_size)

        # If both fail → skip this combo
        if layers_used is None:
            continue
        
        total_bars = sum(combo)

        if best_combo is None:
            # First valid solution
            best_ast = ast
            best_combo = combo
            best_layers = layers_used
            best_distribution = distribution
            best_total_bars = total_bars

        else:
            # Preference Rule: 
            # If AST difference < 20 mm² → choose fewer bars.
            if abs(ast - best_ast) <= 20:
                if total_bars < best_total_bars:
                    best_ast = ast
                    best_combo = combo
                    best_layers = layers_used
                    best_distribution = distribution
                    best_total_bars = total_bars

            # Otherwise choose the naturally lowest AST > required
            elif ast < best_ast:
                best_ast = ast
                best_combo = combo
                best_layers = layers_used
                best_distribution = distribution
                best_total_bars = total_bars

    return best_combo, best_ast, best_distribution,best_layers



# ================================
#            RUN CODE
# ================================
if __name__ == "__main__":

    AST_required =942    # Enter your required AST
    beam_width = 250     # mm
    cover = 20           # mm
    aggregate_size = 12  # mm
    diameters = [20, 16, 12, 10]                  # descending priority


    combo, ast, distribution, layers = min_ast_by_bars_required(
        AST_required, beam_width, cover, aggregate_size,diameters
    )

    print("=======================================")
    print("            RESULT SUMMARY             ")
    print("=======================================\n")

    if combo is None:
        print("No valid bar combination found!")
    else:
        print(f"Required Ast      : {AST_required:.2f} mm²")
        print(f"Provided Ast      : {ast:.2f} mm²")

        print("\nBar Combination (dia : count):")
    
        for d, c in zip(diameters, combo):
            print(f"  {d} mm  :  {c} bars")

        print(f"\n{layers} LAYER Distribution:")
        if layers>1:
            print(distribution[1])
        if layers>=1:
            print(distribution[0])

    print("\n=======================================\n")
