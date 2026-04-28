
import random



class DiceFace:
    ARROW       = "arrow"     
    BANG        = "bang1"     
    DOUBLE_BANG = "bang2"    
    BEER        = "beer"   
    DYNAMITE    = "dynamite"   
    GATLING     = "gatling"   

ALL_FACES: list[str] = [
    DiceFace.ARROW,
    DiceFace.BANG,
    DiceFace.DOUBLE_BANG,
    DiceFace.BEER,
    DiceFace.DYNAMITE,
    DiceFace.GATLING,
]



def roll_dice(current_faces: list[str], locked_indices: list[int]) -> list[str]:
    result = list(current_faces)  
    for i in range(len(result)):
        if current_faces[i] == DiceFace.DYNAMITE:
            continue
            
        if i not in locked_indices:
            result[i] = random.choice(ALL_FACES)
    return result


def apply_dice_results(faces: list[str]) -> dict:
    results = {
        "arrows":    0,
        "bang1":     0,
        "bang2":     0,
        "beers":     0,
        "dynamites": 0,
        "gatlings":  0,
    }
    for face in faces:
        if face == DiceFace.ARROW:
            results["arrows"]    += 1
        elif face == DiceFace.BANG:
            results["bang1"]     += 1
        elif face == DiceFace.DOUBLE_BANG:
            results["bang2"]     += 1
        elif face == DiceFace.BEER:
            results["beers"]     += 1
        elif face == DiceFace.DYNAMITE:
            results["dynamites"] += 1
        elif face == DiceFace.GATLING:
            results["gatlings"]  += 1
    return results