import math

class Beam:
    """
    RCC Beam Design Module
    IS 456:2000 Based Design
    All forces in kN, dimensions in mm
    Moment in kN-m
    """

    def __init__(self, span, width, depth, load_udl, fck=20, fy=500, cover=25):
        self.L = span                  # span in meters
        self.b = width                 # width in mm
        self.D = depth                 # overall depth in mm
        self.load = load_udl           # UDL kN/m
        self.fck = fck
        self.fy = fy
        self.cover = cover

        # Effective depth
        self.d = self.D - self.cover - 10  # assuming 10mm bar (approx), modify later

    # ---- LOAD & ANALYSIS PART ----------------------------------------------

    def bending_moment(self):
        """
        BM = wL^2/8  (Simply Supported Beam with UDL)
        Returns BM in kN-m
        """
        return (self.load * self.L**2) / 8

    def shear_force(self):
        """
        SF = wL/2
        Returns SF in kN
        """
        return (self.load * self.L) / 2

    # ---- DESIGN OF FLEXURE -------------------------------------------------

    def design_Ast(self):
        """
        Ast = 0.5 * fck/fy * b * d (1 - sqrt(1 - (4.6*M)/(fck*b*d^2)))
        Returns Ast in mm2
        """

        M = self.bending_moment() * 10**6  # convert kN-m to N-mm

        b = self.b
        d = self.d
        fck = self.fck
        fy = self.fy

        # Check if limiting moment is exceeded
        Mu_lim = 0.138 * fck * b * d * d  # limiting moment N-mm

        if M > Mu_lim:
            return {"status": "FAIL", "msg": "Increase depth! Mu > Mu_lim"}

        # Ast formula
        numerator = 1 - math.sqrt(1 - (M / (0.87 * fy * b * d * d)))

        Ast = (0.87 * fy * b * d * numerator) / fy

        # Minimum Ast (IS 456 – 26.5.1)
        Ast_min = 0.85 * b * d / fy

        if Ast < Ast_min:
            Ast = Ast_min

        return round(Ast, 2)

    # ---- DESIGN OF SHEAR ---------------------------------------------------

    def design_stirrups(self):
        """
        Simple shear design using τv and τc chart values
        You can expand this later with full τc table lookup
        """

        V = self.shear_force() * 10**3  # kN to N
        b = self.b
        d = self.d

        tau_v = V / (b * d)  # shear stress N/mm2

        # For M20, assume tau_c = 0.48 (simple default – later replace with table)
        tau_c = 0.48

        if tau_v <= tau_c:
            spacing = 200   # mm (default safe spacing)
        else:
            spacing = 100

        return {
            "tau_v": round(tau_v, 3),
            "tau_c": tau_c,
            "stirrups": f"8mm 2-legged @ {spacing} mm c/c"
        }

    # ---- SUMMARY -----------------------------------------------------------

    def design_summary(self):
        return {
            "Span_m": self.L,
            "Width_mm": self.b,
            "Depth_mm": self.D,
            "Effective_depth_mm": self.d,
            "UDL_kN_per_m": self.load,
            "BM_kNm": round(self.bending_moment(), 2),
            "SF_kN": round(self.shear_force(), 2),
            "Ast_required_mm2": self.design_Ast(),
            "Shear_design": self.design_stirrups()
        }

from beam import Beam

beam1 = Beam(span=4.5, width=230, depth=450, load_udl=18)

result = beam1.design_summary()

print(result)
