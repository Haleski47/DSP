# 一阶 Butterworth IIR （高通）滤波器设计文档

## 1. 引言

本文档介绍一阶高通 IIR 滤波器的原理推导、数学建模、仿真以及 RTL 实现方法。  
包括以下几个部分：  
- IIR 高通滤波器的原理推导与算法细节  
- 浮点与定点模型仿真（Python）  
- RTL 实现（基于 Stratus SystemC）

---

## 2.1 Butterworth 高通滤波器简介

一阶 Butterworth 高通滤波器具有最大通带平坦度（无波纹），在低频处具有良好的衰减特性。  
其归一化模拟域频率响应为：

$$
|H(j\omega)|^2 = \frac{\omega^2}{\omega^2 + \omega_c^2}
$$

其中：  
- ω<sub>c</sub>：截止角频率  
- 阶数 n = 1  

---

## 2.2 一阶 Butterworth 模拟高通传输函数

一阶高通 Butterworth 模拟域标准形式为：

$$
H(s) = \frac{s}{s + \omega_c}
$$

---

## 2.3 双线性变换公式

### 2.3.1 模拟域到数字域的转换公式
$$
s = \frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}}, \quad T = \frac{1}{f_s}
$$

### 2.3.2 代入 $H(s)$：
$$
H(z) = \frac{\frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}}}{\frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}} + \omega_c}
$$

### 2.3.3 分子分母同乘 $(1 + z^{-1})$：
$$
H(z) = \frac{\frac{2}{T}(1 - z^{-1})}{\frac{2}{T}(1 - z^{-1}) + \omega_c(1 + z^{-1})}
$$

### 2.3.4 展开分母（用 d 表示）
令：
$$
d = \frac{\omega_c T}{2}
$$

则分母可以写成：
$$
(1 + d) + ( -1 + d ) z^{-1}
$$

### 2.3.5 归一化传递函数
分子分母同除以 $(1 + d)$，得到：
$$
H(z) = \frac{\frac{1}{1 + d} - \frac{1}{1 + d} z^{-1}}{1 + \frac{d - 1}{1 + d} z^{-1}}
$$

因此滤波器系数为：
$$
\begin{aligned}
b_0 &= \frac{1}{1 + d} = 1 -\frac{d}{1 + d} \\
b_1 &= -\frac{1}{1 + d} = -1 + \frac{d}{1 + d} \\
a_1 &= \frac{d - 1}{1 + d}= -1 + 2\frac{d}{1 + d}
\end{aligned}
$$


## 2.4 时域差分方程

由系统函数：
$$
H(z) = \frac{b_0 + b_1 z^{-1}}{1 + a_1 z^{-1}}
$$

时域差分方程为：
$$
y[n] + a_1 y[n-1] = b_0 x[n] + b_1 x[n-1]
$$
整理得到：
$$
y[n] = b_0 x[n] + b_1 x[n-1] - a_1 y[n-1]
$$

---

## 2.5 IIR 高通滤波器的典型特性

### 2.5.1 系数关系
| 特性 | 数学关系 | 物理意义 |
|------|----------|----------|
| 系数和为零 | $b_0 + b_1 = 0$ | 高通滤波器在直流处衰减为零 |
| 稳定性 | $\|a_1\| < 1$ | 极点在单位圆内 |
| 高频增益 | $H(-1) \approx 1$ | 在奈奎斯特频率接近全通 |

---

### 2.5.2 零极点
- 零点：
$$
b_0 + b_1 z^{-1} = 0 \quad \Rightarrow \quad z = -1
$$
- 极点：
$$
p = -a_1
$$
- 稳定性条件：$|a_1| < 1$

---
### 2.5.3 建立时间
IIR滤波器对于阶跃响应可以拆分为常量增益+指数衰减；当指数衰减项达到预期的抖动范围 $ \alpha=0.01$ 时，我们判定滤波器达到稳定，其建立时间为$t_s = n_s T \approx \frac{ \ln(1/\alpha) \cdot T }{ |\ln r|}=\frac{ \ln(\alpha) \cdot T }{ \ln a_1}$
其中 $T$ 是采样时间


## 2.6 定点量化模型

与二阶 IIR 类似，一阶高通滤波器的量化误差包含：
1. **系数量化误差**（U1.15 格式）
2. **反馈量化误差**（$y[n-1]$ 定点表示）

### 2.6.0 量化方法
实际使用高通滤波器时(propus gyro的HPF)，fc/fs通常设置为极小值，如propus HPF的fc/fs要求在(2e-6 ~ 64e-6), 滤波器系数接近±1，无法直接量化。在本文档中采用的量化方案如下：
#### 2.6.0.1 系数量化
观察到公式2.3.5中，$b_0$ $b_1$ $b_2$均可写为$1±(2*)\frac{d}{1 + d}$,因此针对$\frac{d}{1 + d}$进行量化，即:
$$
\begin{aligned}
coef^{fq} &= round(\frac{(\frac{d}{1 + d})}{scale_{coeff}}) * scale_{coeff} \\
scale_{coeff} &= \frac{1}{2^{26}} \\
b_0^{fq} &= 1 + coef^{fq} \\
b_1^{fq} &= -1 + coef^{fq} \\
a_1^{fq} &= -1 + 2*coef^{fq}
\end{aligned}
$$
其中，fq为fakequant，表示系数经过定点量化与反量化后，所得到的浮点值(也可以理解为定点化后，定点值表示的浮点值)。实际运行时，首先根据fc/fs计算浮点的$b_0$系数；然后计算得到$coef^{fq}$；最后依据选定的$scale_{coeff}$计算真实的定点化后的$coef^{quant}$完成高通滤波器的运算。在计算$coef^{fq}$时，可以采用如下方法降低浮点系数与fakequant系数的量化误差：
```
import numpy as np
from scipy.signal import butter
import matplotlib.pyplot as plt
# 2e-6 ~ 64e-6
fc_fs_values = np.arange(62e-6, 64e-6 + 0.01e-6, 0.00001e-6)
left_shift = 26
errors = []

for fc_fs in fc_fs_values:
    # 设计高通滤波器
    b, a = butter(1, 2 * fc_fs, btype="high")
    
    # 重新计算 b_new 和 a_new
    b_new = [1 - b[0], 1 + b[1]]
    a_new = [1 - a[0], 1 + a[1]]
    
    # 左移位转换并计算误差
    scaled_b0 = b_new[0] * (2 ** left_shift)
    rounded_b0 = np.round(scaled_b0)
    error = np.abs(rounded_b0 - scaled_b0)
    errors.append(error)

plt.figure(figsize=(10, 6))
plt.plot(fc_fs_values * 1e6, errors, label="Quantization Error")
plt.xlabel("fc/fs (μ)")
plt.ylabel("Error after shifting and rounding")
plt.title("Quantization Error of b_new[0] after Left Shift and Rounding")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

fc_fs_error_pairs = list(zip(fc_fs_values, errors))
sorted_pairs = sorted(fc_fs_error_pairs, key=lambda x: x[1])

# 打印误差最小的前10个点
print("误差最小的前10个点:")
for i, (fc, err) in enumerate(sorted_pairs[:10]):
    print(f"{i+1:2d}: fc/fs = {fc:.8e}, 误差 = {err:.8e}")
```
此方法的核心为在目标fc/fs附近搜寻最小量化误差量化方案
#### 2.6.0.2 运算公式量化(浮点->fakquant->quant)
浮点公式：
$$
y_n = b_0 x_0 + b_1 x_1 - a_1 y_1
$$
fakequant公式(等效于浮点公式)：
$$
\begin{aligned}
y_n^{fq} &= b_0^{fq} x_0 + b_1^{fq} x_1 - a_1^{fq} y_1^{fq} \\ 
y_n^{fq} &= y_n^{quant} * scale_{out}\\
y_{output} &=round(y_n^{fq}) \\
\end{aligned}
$$
其中，$x_0$在硬件/算法仿真时，其值均为定点后的数据输入(-32768~+32168)，所以float/fa/quant值一致；反馈的$y_1$带有小数部分，输出会将小数部分截断，以整数输出，需注意区分；

quant定点公式：
$$
\begin{aligned}
x_0 &= x_0^{fq} = x_0^{float} = x_0^{quant} \\
x_1 &= x_1^{fq} = x_1^{float} = x_1^{quant} \\
scale_{out} &= \frac{1}{2^{out_{dec}}}\\
scale_{coeff} &= \frac{1}{2^{coeff_{leftshift}}} = \frac{1}{2^{26}}\\
y_n^{fq} &=(1 + coef^{fq})x_0 + (-1 + coef^{fq}) x_1 - (-1 + 2*coef^{fq}) y_1^{fq}  \\
&= (x_0 - x_1 + y1^{fq}) + coef^{fq}(x_0+ x_1 - 2y_1^{fq}) \\
y_n^{quant} * scale_{out} &=(x_0^{quant}-x_1^{quant}+y_1^{quant}*scale_{out})  \\
&+ coef^{quant}*scale_{coeff}(x_0^{quant}+x_1^{quant}-2y_1^{quant} * scale_{out})\\
y_n^{quant}(低精度，低乘法位宽)&= ((x_0^{quant}-x_1^{quant}) << out_{dec} + y_1^{quant}) \\
&+(coef^{quant}(x_0^{quant}+x_1^{quant}-2y_1^{quant}>>out_{dec}) + 2^{coeff_{leftshift}-1})>>coeff_{leftshift} \\
y_n^{quant}(高精度，高乘法位宽)&=((x_0^{quant}-x_1^{quant}) << out_{dec} + y_1^{quant}) \\
&+((coef^{quant}x_0^{quant}+coef^{quant}x_1^{quant}-2coef^{quant}y_1^{quant}>>out_{dec})+ 2^{coeff_{leftshift}-1})>>coeff_{leftshift} \\
\end{aligned}
$$

其中，右移$coeff_{leftshift}$前,加$2^{coeff_{leftshift}-1}$的原因为：补0.5lsb,保证系数与数据的乘积为零偏(不偏向0也不偏向1)；低精度与高精度实际使用时，差距很小，其原因系数的数值过小，小数与小数的乘法可以忽略


