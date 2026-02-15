import pandas as pd


# ---------------------------------------
# Load τc table from Excel
# ---------------------------------------
def load_tau_c_table(filename, sheet_name=0):
    """
    Reads shear stress table from Excel using pandas
    Returns a DataFrame indexed by Ast%
    """
    df = pd.read_excel(filename, sheet_name=sheet_name)

    # Set Ast% as index
    df.set_index("Ast%", inplace=True)

    # Ensure index is float and sorted
    df.index = df.index.astype(float)
    df.sort_index(inplace=True)

    return df


# ---------------------------------------
# Get τc value by interpolation
# ---------------------------------------
def get_tau_c(ast_percent, fck):
    grade = int(fck)

    #tau_c_max
    Max_shear_stress={
    "15":2.5,
    "20":2.8,
    "25":3.1,
    "30":3.5,
    "35":3.7,
    "40":4.0

    }
    tau_c_max = Max_shear_stress.get(str(grade))

    #load excel
    df = load_tau_c_table("shear_table.xlsx")


    if grade not in df.columns:
        raise ValueError(f"Concrete grade {grade} not found")

    # Clamp Ast%
    ast_percent = max(df.index.min(), min(ast_percent, df.index.max()))

    # Insert Ast% into index
    temp_series = df[grade].reindex(
        df.index.union([ast_percent])
    ).sort_index()

    # Interpolate
    temp_series = temp_series.interpolate(method="index")



    # Now this WILL work
    return float(temp_series.loc[ast_percent]),tau_c_max



# ---------------------------------------
# Example usage (RUN THIS PART)
# ---------------------------------------

if __name__ == "__main__":

    # Inputs (from your beam design)
    Ast_percent =1.237    # %
    concrete_grade = 25

        # Get τc
    tau_c,tau_c_max = get_tau_c(Ast_percent, concrete_grade)

    print("===================================")
    print(" SHEAR STRESS (τc) CALCULATION ")
    print("===================================")
    print(f"Ast %           : {Ast_percent}")
    print(f"Concrete grade  : {concrete_grade}")
    print(f"τc (N/mm²)      : {tau_c:.3f}")
    print(f"τc_max (N/mm²)      : {tau_c_max:.3f}")
