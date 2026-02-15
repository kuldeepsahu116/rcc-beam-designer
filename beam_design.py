import math
from Ast_calc_try4 import min_ast_by_bars_required
from shear_stress import get_tau_c

# #-------------------------------------------
# # Input
# #-------------------------------------------

# factoredmoment=200   # in Knm
# width=250            # in mm
# fck=30
# fy=415
# clear_cover=30         # in mm
# side_cover=20           # in mm
# Max_bar_dia=20       # in mm
# aggregate_size= 12       #in mm
# diameters = [20, 16, 12, 10]                  # descending priority
# D_given=0
# factored_shear_force=200    #in KN


#-------------------------------------------
# Bending Design function
#-------------------------------------------
 
def Calc(factoredmoment,width,fck,fy,side_cover,aggregate_size,diameters,d_effective,Xulim_by_d,D_roundedoff):
    A_st=round((-((-1)*0.87*fy*d_effective) - math.sqrt(((-1)*0.87*fy*d_effective)**2 - 4*((0.87*(fy**2)/(width*fck))*factoredmoment*1000000))) / (2*0.87*(fy**2)/(width*fck)),2)
    A_st_min=0.85*width*d_effective/fy

    if A_st<A_st_min:
        A_st=A_st_min


    combo, ast, distribution, layers = min_ast_by_bars_required(A_st, width, side_cover, aggregate_size,diameters)
    Ast_provided=round(ast,2)
    Xu_lim=Xulim_by_d*d_effective
    Xu=round((0.87*fy*Ast_provided)/(0.36*fck*width),2)

    return Xu,Xu_lim,d_effective,A_st,distribution,Ast_provided,combo,layers



def bending_design(factoredmoment,width,fck,fy,clear_cover,side_cover,Max_bar_dia,aggregate_size,diameters,D_given):
    
    Xulim_by_d=round(0.0035/((0.87*fy/200000)+0.0055),2)
    Q_max=round(0.36*fck*Xulim_by_d*(1-0.42*Xulim_by_d),2)
    d=round((factoredmoment*1000000/(Q_max*width))**0.5,0)
    D=d+clear_cover+Max_bar_dia/2
    if D_given==0 :
        D_roundedoff=max(round(D,-1),round(D+5,-1))
    else:
        D_roundedoff=D_given

    d_effective=D_roundedoff-clear_cover-Max_bar_dia/2
    Mu_lim=Q_max*width*(d_effective**2)

    
    if factoredmoment*1000000<Mu_lim:
    
        Xu,Xu_lim,d_effective,A_st,distribution,Ast_provided,combo,layers= Calc(factoredmoment,width,fck,fy,side_cover,aggregate_size,diameters,d_effective,Xulim_by_d,D_roundedoff)
    
        # for doubly design we need to focus here for singly it is ok but if we limit the depth and Xu exceeds the limit it we fail
        if Xu>Xu_lim and D_given==0:
            D_roundedoff+=10
            Xu,Xu_lim,d_effective,A_st,distribution,Ast_provided,combo,layers= Calc(
                factoredmoment,width,fck,fy,side_cover,aggregate_size,diameters,d_effective,Xulim_by_d,D_roundedoff)
            return D_roundedoff,d_effective,A_st,distribution,Ast_provided,layers,combo,Xu,Xu_lim,d
        if Xu>Xu_lim and D_given!=0:
            print ("error-Depth taken is not sufficient")
            return 0,0,0,0,0,0,0,0,0,0
        else:
            return D_roundedoff,d_effective,A_st,distribution,Ast_provided,layers,combo,Xu,Xu_lim,d
    else:
            print ("error-doubly design required")
            return 0,0,0,0,0,0,0,0,0,0


#-------------------------------------------
#Shear Design 
#-------------------------------------------


def Shear_spacing(factored_shear_force,fy,width,d_effective,tau_c,tau_c_max,tau_v,shearbar_dia,number_of_stirup_legs):
    if tau_v<=tau_c_max:
        A_sv=number_of_stirup_legs*3.14*(shearbar_dia**2)/4
        sv=min(300,0.75*d_effective)
        if tau_v<=tau_c:
            S=math.floor(min(sv,(0.87*fy*A_sv/(0.4*width)))/5)*5
        else:
            S=math.floor(min(sv,(0.87*fy*A_sv*d_effective/((factored_shear_force*1000)-(tau_c*width*d_effective))))/5)*5

    else:
        S=0
    return S


def Shear_design(factored_shear_force,Ast_percent,fck,fy,width,d_effective):
    
    Shear_diameters = [8, 10, 12]
    tau_c,tau_c_max = get_tau_c(Ast_percent,fck)
    tau_v=factored_shear_force*1000/(width*d_effective)
    MIN_SPACING = 75

    # 2-legged
    for dia in Shear_diameters:
        Sv = Shear_spacing(factored_shear_force,fy,width,d_effective,tau_c,tau_c_max,tau_v,dia,2)

        if Sv >= MIN_SPACING:
            return dia, 2, Sv

    # 3-legged
    for dia in Shear_diameters:
        Sv = Shear_spacing(factored_shear_force,fy,width,d_effective,tau_c,tau_c_max,tau_v,dia,3)

        if Sv >= MIN_SPACING:
            return dia, 3, Sv

    # 4-legged
    for dia in Shear_diameters:
        Sv = Shear_spacing(factored_shear_force,fy,width,d_effective,tau_c,tau_c_max,tau_v,dia,4)

        if Sv >= MIN_SPACING:
            return dia, 4, Sv

    return 0,0,0


#-------------------------------------------
# RUN FUNCTION
#-------------------------------------------


def design_beam(data):

    factoredmoment=float(data["moment"])
    width=float(data["width"])
    fck=float(data["fck"])
    fy=float(data["fy"])
    clear_cover=float(data["clear_cover"])
    side_cover=float(data["side_cover"])
    Max_bar_dia=float(data["bar_dia"])
    aggregate_size=float(data["agg"])
    factored_shear_force=float(data["shear"])

    diameters=[20,16,12,10]
    D_given=0

    D_roundedoff,d_effective,A_st,distribution,Ast_provided,layers,combo,Xu,Xu_lim,d = bending_design(
        factoredmoment,width,fck,fy,clear_cover,side_cover,
        Max_bar_dia,aggregate_size,diameters,D_given)

    Ast_percent=Ast_provided*100/(width*d_effective)

    Shear_bar_dia,No_of_legs,Sv = Shear_design(
        factored_shear_force,Ast_percent,fck,fy,width,d_effective)

    return {
        "depth":D_roundedoff,
        "effective_depth":d_effective,
        "Ast_req":A_st,
        "Ast_prov":Ast_provided,
        "Xu":Xu,
        "Xu_lim":Xu_lim,
        "shear_dia":Shear_bar_dia,
        "legs":No_of_legs,
        "spacing":Sv
    }
