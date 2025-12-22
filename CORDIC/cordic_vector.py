import numpy as np

lut =   [131072, 77376, 40883, 20753, 10416, 5213, 2607, 1303, 651, 325,
        162, 81, 40, 20, 10, 5, 2, 1]

angle45 = 131072
angle90 = 262144
angle180 = 524288
angle360 = 1048576  # 2^20

steps = 18
frac_bit = 5

def phase_detec(x : int, y : int):
    ### 0~90 -> phase 0
    ### 90~180 -> phase 1
    ### 180~270 -> phase 2
    ### 270~360 -> phase 3
    if x >= 0 and y >= 0:
        return 0
    elif x >= 0 and y < 0:
        return 3
    elif x < 0 and y >= 0:
        return 1
    else:
        return 2

def angle_recover(x, phase):
    if phase == 0:
        x = x
    elif phase == 1:
        x = angle180 - x
    elif phase == 2:
        x = angle180 + x
    elif phase == 3:
        x = angle360 - x
    return x

def scale_to_range(x, y, low=16384, high=32768):
    # scale x, y to (low, high)
    x = np.floor(x)
    y = np.floor(y)
    
    if (x >= low and x <= high) or (y >= low and y <= high):
        return x, y
    l_shift = 0
    while(x < low and y < low):
        x = x * 2
        y = y * 2
    
    return x, y


def cordic_vector(x : int, y : int):
    # x, y is both s16
    # 1. get phase 
    # 2. move to phase 0, x=abs(x) y=abs(y)
    # 3. rescale input to 16384 ~ 32767
    # 3. 18 steps to cal angle
    phase = phase_detec(x, y)
    x = abs(x)
    y = abs(y)

    # scale and clip to 32767
    x, y = scale_to_range(x, y, low=16384, high=32768)
    x = np.clip(x, 0, 32767)
    y = np.clip(y, 0, 32767)
    angle_out = 0

    frac_scale = 1 / (2 ** frac_bit) 

    for step in range(steps):
        if y >= 0:
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
    
    angle_out = angle_recover(angle_out, phase)
    return angle_out


# --- 验证脚本 ---
def numpy_cordic_angle(x, y):
    """用 numpy 计算角度，并转为你的 2^20 = 360° 单位"""
    angle_rad = np.arctan2(y, x)
    # 转为 [0, 2π)
    angle_rad = np.mod(angle_rad, 2 * np.pi)
    # 转为你的单位
    angle_scaled = angle_rad * (angle360 / (2 * np.pi))
    return angle_scaled

def angle_diff(a, b, full_circle=angle360):
    """计算两个角度的最小差值（考虑环绕）"""
    diff = np.abs(a - b)
    return np.minimum(diff, full_circle - diff)

# 生成随机测试数据
np.random.seed(42)  # 可复现
N = 100000
# 生成浮点 (x, y)，避免原点
x_float = np.random.uniform(-1e4, 1e4, N)
y_float = np.random.uniform(-1e4, 1e4, N)
# 避免 (0,0)
mask = (np.abs(x_float) > 1e-6) | (np.abs(y_float) > 1e-6)
x_float = x_float[mask]
y_float = y_float[mask]

# 转为整数（模拟 s16 输入，但允许更大范围，你的 scale_to_range 会处理）
x_int = np.round(x_float).astype(int)
y_int = np.round(y_float).astype(int)

# 计算参考角度
ref_angles = np.array([numpy_cordic_angle(x, y) for x, y in zip(x_int, y_int)])

# 调用你的 CORDIC
cordic_angles = np.array([cordic_vector(x, y) for x, y in zip(x_int, y_int)])

# 计算误差（单位：你的角度单位，可转为度）
errors = angle_diff(ref_angles, cordic_angles)
max_error = np.max(errors)
mean_error = np.mean(errors)
std_error = np.std(errors)

# 转为角度（度）便于理解
max_error_deg = max_error * 360 / angle360
mean_error_deg = mean_error * 360 / angle360

print(f"Total test cases: {len(ref_angles)}")
print(f"Max error: {max_error:.2f} units ({max_error_deg:.4f} degrees)")
print(f"Mean error: {mean_error:.2f} units ({mean_error_deg:.4f} degrees)")
print(f"Std error: {std_error:.2f} units ({std_error * 360 / angle360:.4f} degrees)")