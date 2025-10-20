# 一阶低通指数滑动平均滤波器（EMA IIR）
## 1 时域模型与Z域模型
\[
y[n] = \alpha x[n] + (1-\alpha) y[n-1], \quad 0 < \alpha \le 1
\]
其系统函数：
\[
H(z) = \frac{Y(z)}{X(z)} = \frac{\alpha}{1 - (1 - \alpha) z^{-1}}
\]
对照通用形式：
\[
H(z) = \frac{b_0 + b_1 z^{-1}}{1 + a_1 z^{-1}}
\]
得：
\[
b_0 = \alpha, \quad b_1 = 0, \quad a_1 = -(1 - \alpha)
\]
低频增益 $ (z = 1) $：
\[
H(1) = \frac{1}{1 - (1 - \alpha)} = 1
\]

高频增益 $ (z = -1) $：
\[
H(1) = \frac{1}{1 - (\alpha - 1)} = \frac{1}{2 - \alpha}
\]

## 2 零极点与频率响应
- **极点**：\(p = 1 - \alpha\)（位于实轴，\(0 < \alpha < 1 \Rightarrow |p| < 1\)，系统稳定）
- **零点**：无（有限零点），等价为在 \(z = \infty\) 处一个零

- **频率响应：**
\[
H(e^{j\omega}) = \frac{\alpha}{1 - (1 - \alpha) e^{-j\omega}} \\ 
|H(e^{j\omega})|^2 = \left( \frac{\alpha}{1 - (1 - \alpha) e^{-j\omega}} \right) \cdot \left( \frac{\alpha}{1 - (1 - \alpha) e^{j\omega}} \right) = \frac{\alpha^2}{ [1 - (1 - \alpha) e^{-j\omega}] [1 - (1 - \alpha) e^{j\omega}] } 
\]
带入欧拉公式：
\[
e^{j\omega} + e^{-j\omega} = 2 \cos \omega 
\]
可以得到：
\[
\quad |H(e^{j\omega})|^2 = \frac{\alpha^2}{1 + (1 - \alpha)^2 - 2(1 - \alpha) \cos\omega} \\
\]


- **截止频率：**
\[
|H(e^{j\omega_c})|^2 = \frac{1}{2} \\
\]
带入可以得到：
\[
2\alpha^2 = 1 + (1 - 2\alpha + \alpha^2) - 2(1 - \alpha) \cos \omega_c
\]
\[
2\alpha^2 = 2 - 2\alpha + \alpha^2 - 2(1 - \alpha) \cos \omega_c
\]
\[
\alpha^2 = 2 - 2\alpha - 2(1 - \alpha) \cos \omega_c
\]
\[
2(1 - \alpha) \cos \omega_c = 2 - 2\alpha - \alpha^2
\]
\[
\cos \omega_c = \frac{2 - 2\alpha - \alpha^2}{2(1 - \alpha)}
\]
截止频率 $ω_c$ 满足：
\[
\cos \omega_c = 1 - \frac{\alpha^2}{2(1 - \alpha)}
\]
最终得到：
\[
\boxed{\omega_c = \arccos \left( 1 - \frac{\alpha^2}{2(1 - \alpha)} \right) \\
\quad f_c = \frac{f_s}{2\pi}  \arccos \left( 1 - \frac{\alpha^2}{2(1 - \alpha)} \right)}
\]
- **建立时间：**

极点(模值)：
\[
    p = 1 - \alpha
\]
建立时间计算方法(衰减到$\beta = 0.01$)：
\[
\boxed{p^N = \beta} \\
N = \frac{log(\beta)}{log(p)} = \frac{log(\beta)}{log(1 - \alpha)} \\
\]

## 3 典型值汇总（便于工程选型）：

| \(N\) | \(\alpha\) | \(f_c / f_s\) | 建立时间(β=0.01) |
|---:|---:|---:|---:|
| 0   | 1.0      | 0.0     | 0.0    |
| 1   | 0.5      | 0.1150  | 6.64   |
| 2   | 0.25     | 0.0461  | 16.01  |
| 3   | 0.125    | 0.0213  | 34.49  |
| 4   | 0.0625   | 0.0107  | 71.36  |
| 5   | 0.03125  | 0.0054  | 145.05 |
| 6   | 0.015625 | 0.0027  | 292.42 |
| 7   | 0.0078125| 0.0014  | 587.16 |

# 二阶低通指数滑动平均滤波器（EMA IIR）

## 1 时域模型与Z域模型

- **时域方程（\(\alpha_1,\alpha_2\)）：**

\[
\begin{cases}
u[n] = \alpha_1\,x[n] + (1-\alpha_1)\,u[n-1] \\
y[n] = \alpha_2\,u[n] + (1-\alpha_2)\,y[n-1]
\end{cases}
\qquad 0<\alpha_1,\alpha_2\le 1
\]

- **Z域方程（\(\alpha_1,\alpha_2\)）：**
\[
H(z)=\frac{\alpha_1\alpha_2}{\left[1-(1-\alpha_1)z^{-1}\right]\left[1-(1-\alpha_2)z^{-1}\right]}
= \frac{\alpha_1\alpha_2}{1-\big[(1-\alpha_1)+(1-\alpha_2)\big]z^{-1}+(1-\alpha_1)(1-\alpha_2)z^{-2}}
\]
- **(补充二阶IIR通用形式）**
\[
H(z)=\frac{b_0+b_1 z^{-1}+b_2 z^{-2}}{1+a_1 z^{-1}+a_2 z^{-2}}
\]

- **针对 \(\alpha_1,\alpha_2\) ：**
\[
b_0=\alpha_1\alpha_2,\quad b_1=0,\quad b_2=0;\qquad
a_1=-\big[(1-\alpha_1)+(1-\alpha_2)\big]=\alpha_1+\alpha_2-2,\quad
a_2=(1-\alpha_1)(1-\alpha_2).
\]

- **低频增益（\(z=1\)）**：两种情形均有
\[
H(1)=1.
\]

- **高频增益（\(z=-1\)）**：
  - \(\alpha_1,\alpha_2\)：\(\displaystyle H(-1)=\frac{\alpha_1\alpha_2}{(2-\alpha_1)(2-\alpha_2)}\).

## 2 零极点与频率响应

- **极点**：\(p_1 = 1-\alpha_1\), \(p_2 = 1-\alpha_2\)。  
- **零点**：有限平面无零点，可等价视为 \(z=\infty\) 处两个零点。
- **频率响应（一般情形）**：
\[
H(e^{j\omega})=\frac{\alpha_1\alpha_2}{\bigl(1-r_1 e^{-j\omega}\bigr)\bigl(1-r_2 e^{-j\omega}\bigr)} \\
|H(e^{j\omega})|^2=\frac{\alpha_1^2\alpha_2^2}{\bigl(1+r_1^2-2r_1\cos\omega\bigr)\bigl(1+r_2^2-2r_2\cos\omega\bigr)}
\]
对于二阶EMA滤波器，很难继续由理论进行分析，需通过仿真得到

- **建立时间：**

极点(模值)：
\[
p_1 = 1 - \alpha_1, \quad p_2 = 1 - \alpha_2
\]

建立时间由主导极点（模值较大的极点）决定(衰减到$\beta = 0.01$)：
\[
N = \frac{\log(\beta)}{\log(\max(|1-\alpha_1|, |1-\alpha_2|))}
\]

更精确地，建立时间应满足下式，但是无法直接求解：
\[
|K_1||p_1|^N + |K_2||p_2|^N \leq \beta
\]

## 3 典型值汇总（便于工程选型）：

| n1 \ n0 | 0        | 1        | 2        | 3        | 4        | 5        | 6        | 7        |
|---------|----------|----------|----------|----------|----------|----------|----------|----------|
| 0       | NaN      | 0.115027 | 0.046105 | 0.021284 | 0.010275 | 0.005053 | 0.002506 | 0.001248 |
| 1       | 0.115027 | 0.073070 | 0.040477 | 0.020583 | 0.010191 | 0.005043 | 0.002505 | 0.001248 |
| 2       | 0.046105 | 0.040477 | 0.029612 | 0.018176 | 0.009816 | 0.004994 | 0.002499 | 0.001247 |
| 3       | 0.021284 | 0.020583 | 0.018176 | 0.013692 | 0.008684 | 0.004802 | 0.002473 | 0.001244 |
| 4       | 0.010275 | 0.010191 | 0.009816 | 0.008684 | 0.006612 | 0.004251 | 0.002376 | 0.001231 |
| 5       | 0.005053 | 0.005043 | 0.004994 | 0.004802 | 0.004251 | 0.003252 | 0.002104 | 0.001182 |
| 6       | 0.002506 | 0.002505 | 0.002499 | 0.002473 | 0.002376 | 0.002104 | 0.001613 | 0.001047 |
| 7       | 0.001248 | 0.001248 | 0.001247 | 0.001244 | 0.001231 | 0.001182 | 0.001047 | 0.000803 |

# 二阶IIR与二阶EMA带外抑制比较
- **IIR比ema具有更稳定的带内平稳度与带外衰减**

以$\frac{f_c}{f_s} = 0.073070$为例
![iir](./pic/iir.jpg)
![ema](./pic/ema.jpg)