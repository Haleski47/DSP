import numpy as np

lut =   [131072, 77376, 40883, 20753, 10416, 5213, 2607, 1303, 651, 325,
        162, 81, 40, 20, 10, 5, 2, 1]

angle45 = 131072
angle90 = 262144
angle180 = 524288
angle270 = 786432
angle360 = 1048576  # 2^20

steps = 18
frac_bit = 5

def phase_detec(x : int):
    ### 0~90    -> phase 0
    ### 90~180  -> phase 1
    ### 180~270 -> phase 2
    ### 270~360 -> phase 3
    if x >= angle90 and x < angle180:
        return 1
    elif x >= angle180 and x < angle270:
        return 2
    elif x >= angle270 and x < angle360:
        return 3
    elif x >= 0 and x < angle90:
        return 0
    else:
        return 0

def map_angle_to_phase1(x: int):
    if x >= angle90 and x < angle180:
        return angle180 - x
    elif x >= angle180 and x < angle270:
        return x - angle180
    elif x >= angle270 and x < angle360:
        return angle360 - x
    elif x >= 0 and x < angle90:
        return x
    else:
        print("Only support u20 input")
        return x

def vectory_recover(x, y, phase):
    if phase == 0:
        x = x
        y = y
    elif phase == 1:
        x = - x
        y = y
    elif phase == 2:
        x = -x
        y = -y
    elif phase == 3:
        x = x
        y = -y
    return x, y


def cordic_angle(angle: int, x : int, y : int):
    # x, y is just for initiation, set x 
    # 1. get phase 
    # 2. move to phase 0, x=abs(x) y=abs(y)
    # 3. rescale input to 16384 ~ 32767
    # 3. 18 steps to cal angle
    angle = np.clip(angle, 0, angle360-1)
    phase = phase_detec(angle)
    angle = map_angle_to_phase1(angle)

    # scale and clip to 32767
    angle_out = angle

    frac_scale = 1 / (2 ** frac_bit) 
    for step in range(steps):
        if angle_out < 0:
            angle_out = angle_out +  lut[step]
            x_new = x + np.floor(y / (2**step) / frac_scale) * frac_scale
            y_new = -np.floor(x / (2**step) / frac_scale) * frac_scale + y
        else:
            angle_out = angle_out - lut[step]
            x_new = x - np.floor(y / (2**step) / frac_scale) * frac_scale
            y_new = np.floor(x / (2**step) / frac_scale) * frac_scale + y
        
        # print(f"step: {step}, x_new: {x_new}, y_new: {y_new}, angle: {angle_out}")
        x = x_new
        y = y_new
    
    x, y = vectory_recover(x, y, phase)
    return x, y

def reference_sin_cos(angle_u20):
    angle_rad = (angle_u20 / 1048576.0) * 2 * np.pi
    return np.cos(angle_rad) * 32768, np.sin(angle_rad) * 32768

# 验证
np.random.seed(0)
angles = np.random.randint(0, 1048576, 100000)

errors_cos = []
errors_sin = []

for ang in angles:
    cx, sy = cordic_angle(ang, 19898, 0)
    ref_c, ref_s = reference_sin_cos(ang)
    errors_cos.append(cx - ref_c)
    errors_sin.append(sy - ref_s)

errors_cos = np.array(errors_cos)
errors_sin = np.array(errors_sin)

print("=== CORDIC vs NumPy (Rotation Mode) ===")
print(f"Max error (cos): {np.max(np.abs(errors_cos)):.3f}")
print(f"Max error (sin): {np.max(np.abs(errors_sin)):.3f}")
print(f"Mean abs error:  {np.mean(np.abs(errors_cos)):.3f} (cos), {np.mean(np.abs(errors_sin)):.3f} (sin)")
print(f"RMS error:       {np.sqrt(np.mean(errors_cos**2)):.3f} (cos), {np.sqrt(np.mean(errors_sin**2)):.3f} (sin)")