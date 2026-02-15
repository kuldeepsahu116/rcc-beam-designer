import math

# =========================================================
# INPUT DATA
# =========================================================
L=4
B=9

# Geometry (m)
Lx = min(L,B)          # Short span
Ly = max(L,B)          # Long span
support = "simply_supported"   # simply_supported / continuous

#resting wall width
wall_width=250              # mm

# Material
fck = 20          # MPa
fy = 415          # MPa

# Loads (kN/m2)
floor_finish = 1.6
live_load = 3.0

# Detailing
cover = 15        # mm
bar_dia = 10      # mm

# Slab strip width
b = 1000          # mm

# =========================================================
# IS 456 TABLE 27 – αx, αy (Simply supported on four sides)
# Ly/Lx : (alpha_x, alpha_y)
# =========================================================

ALPHA_TABLE = {
    1.0: (0.062, 0.062),
    1.1: (0.074, 0.061),
    1.2: (0.084, 0.059),
    1.3: (0.093, 0.055),
    1.4: (0.099, 0.051),
    1.5: (0.104, 0.046),
    1.75: (0.113, 0.037),
    2.0: (0.118, 0.029),
    2.5: (0.122, 0.020),
    3.0: (0.124, 0.014)
}

# =========================================================
# FUNCTIONS
# =========================================================

def slab_type(Lx, Ly):
    return "one_way" if (Ly / Lx) > 2 else "two_way"


def effective_depth(Lx, support):
    if support == "simply_supported":
        ratio = 30
    elif support == "continuous":
        ratio = 26
    elif support =="cantilever":
        ratio = 7
    return (Lx * 1000) / ratio

def effective_span(clear_span, cc_span, d, support_type):
    """
    Calculates effective span as per IS 456 Clause 22.2

    Parameters:
    clear_span  : clear distance between supports (m)
    cc_span     : centre-to-centre distance of supports (m)
    d           : effective depth (mm)
    support_type: 'simply_supported', 'continuous', 'cantilever'

    Returns:
    Effective span in metres (m)
    """

    if support_type in ["simply_supported", "continuous"]:
        # Clause 22.2(a)
        return min(clear_span + d / 1000, cc_span)

    elif support_type == "cantilever":
        # Clause 22.2(b)
        return clear_span + d / 1000

    else:
        raise ValueError("Invalid support type")

def factored_load(thickness, floor_finish, live_load):
    self_weight = thickness * 25
    return 1.5 * (self_weight + floor_finish + live_load)


def one_way_moment(wu, L):
    return wu * (L**2) / 8

def one_way_shear(wu,L):
    return wu*L/2

def bending_moment_depth(factoredmoment,fck,fy,b):
    Xulim_by_d=round(0.0035/((0.87*fy/200000)+0.0055),2)
    Q_max=round(0.36*fck*Xulim_by_d*(1-0.42*Xulim_by_d),2)
    d=round((factoredmoment*1000000/(Q_max*b))**0.5,0)
    return d


def get_alpha(Lx, Ly):
    ratio = round(Ly / Lx, 2)
    keys = sorted(ALPHA_TABLE.keys())

    for i in range(len(keys) - 1):
        if keys[i] <= ratio <= keys[i + 1]:
            return ALPHA_TABLE[keys[i]]

    return ALPHA_TABLE[keys[-1]]


def two_way_moment(wu, Lx, Ly):
    alpha_x, alpha_y = get_alpha(Lx, Ly)
    Mx = alpha_x * wu * Lx**2
    My = alpha_y * wu * Lx**2
    return Mx, My, alpha_x, alpha_y


def limiting_moment(fck, b, d):
    return 0.138 * fck * b * d**2 / 1e6


def steel_required(Mu, fck, fy, b, d):
    Mu = Mu * 1e6
    A = 0.87 * fy * d
    B = (0.87 * fy) ** 2 / (fck * b)
    Ast = (A - math.sqrt(A**2 - 4 * B * Mu)) / (2 * B)
    return Ast


def minimum_steel(b, d, fy):
    return 0.0012 * b * d if fy >= 415 else 0.0015 * b * d


def bar_spacing(Ast, dia ,d):
    area_bar = math.pi * dia**2 / 4
    return min((((area_bar * 1000) / Ast)//5)*5,300,3*d)


# =========================================================
# MASTER DESIGN FUNCTION
# =========================================================

def design_slab():
    slab = slab_type(Lx, Ly)

    d = effective_depth(Lx, support)

    cc_span_Lx=Lx+wall_width
    effective_Lx=effective_span(Lx, cc_span_Lx, d, support)

    def load(d,cover,bar_dia,floor_finish,live_load,slab):
        D = (math.ceil((d + cover + bar_dia/2)/10))*10
        d=D-cover-bar_dia/2
        wu = factored_load(D / 1000, floor_finish, live_load)


        results = {
            "Slab Type": slab,
            "Overall Depth": f"{D} mm",
            "Factored Load ": F"{round(wu, 2)} kN/m2"
        }
        return D,d,wu,results

    if slab == "one_way":
        D,d,wu,results=load(d,cover,bar_dia,floor_finish,live_load,slab)
        Mu = one_way_moment(wu, effective_Lx)
        Vu= one_way_shear(wu,effective_Lx)
        d_moment=bending_moment_depth(Mu,fck,fy,b)
        
        d=max(d,d_moment)
        Main_Ast = steel_required(Mu, fck, fy, b, d)
        Main_Ast = max(Main_Ast, minimum_steel(b, D, fy))
        Main_bar_spacing = bar_spacing(Main_Ast, bar_dia ,d)
        Distribution_Ast= minimum_steel(b, D, fy)
        Distribution_bar_spacing = bar_spacing(Distribution_Ast, bar_dia ,d)

        results.update({
            "depth": d,
            "Moment":f"{ round(Mu, 2)} kNm/m",
            "Shear": f"{round(Vu,2)} kN",
            "Main Ast Required": f"{round(Main_Ast, 1)} mm2/m",
            "Provide Main Bars": f"{bar_dia} mm @ {Main_bar_spacing} mm c/c",
            "Distribution Ast Required": f"{round(Distribution_Ast, 1)} mm2/m",
            "Provide Distribution Bars": f"{bar_dia} mm @ {Distribution_bar_spacing} mm c/c"
            
        })

    else:
        Mx, My, ax, ay = two_way_moment(wu, Lx, Ly)

        Ast_x = max(
            steel_required(Mx, fck, fy, b, d),
            minimum_steel(b, d, fy)
        )
        Ast_y = max(
            steel_required(My, fck, fy, b, d),
            minimum_steel(b, d, fy)
        )

        sx = bar_spacing(Ast_x, bar_dia)
        sy = bar_spacing(Ast_y, bar_dia)

        results.update({
            "Ly/Lx": round(Ly / Lx, 2),
            "alpha_x": ax,
            "alpha_y": ay,
            "Mx (kNm/m)": round(Mx, 2),
            "My (kNm/m)": round(My, 2),
            "Ast_x (mm2/m)": round(Ast_x, 1),
            "Ast_y (mm2/m)": round(Ast_y, 1),
            "Steel in short span": f"{bar_dia} mm @ {round(sx,0)} mm c/c",
            "Steel in long span": f"{bar_dia} mm @ {round(sy,0)} mm c/c"
        })

    return results


# =========================================================
# RUN DESIGN
# =========================================================

output = design_slab()

for key, value in output.items():
    print(f"{key}: {value}")
