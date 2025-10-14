# 二阶 Butterworth IIR （低通）滤波器设计文档


## 1. 引言

简要介绍滤波器的原理推导、模型仿真与RTL实现。

- IIR滤波器的原理推导与算法细节  
- 浮点与定点模型仿真(python)  
- RTL实现(基于stratus system C)

---

### 2.1 Butterworth 滤波器简介

Butterworth 滤波器是一种具有最大通带平坦度的模拟滤波器，其频率响应的平方在通带内单调递减，没有波纹。其归一化频率响应为：

$$
|H(j\omega)|^2 = \frac{1}{1 + \left(\frac{\omega}{\omega_c}\right)^{2n}}
$$

其中：

- ω<sub>c</sub>：截止角频率  
- n：滤波器阶数（本文中为 2）

---

### 2.2 二阶巴特沃斯模拟低通传输函数

二阶 Butterworth 模拟低通滤波器的标准形式为：

$$
H(s) = \frac{\omega_c^2}{s^2 + \sqrt{2} \cdot \omega_c s + \omega_c^2}
$$

---

### 2.3 双线性变换公式（补充）

#### 2.3.1 将模拟域转换为数字域时所使用的双线性变换公式为：

$$
s = \frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}}
$$
$$ 
T = \frac{1}{f_s}，f_s为采样频率
$$


#### 2.3.2 代入$H(s)$：
$$H(z) = \frac{\omega_c^2}{\left( \frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}} \right)^2 + \sqrt{2}\omega_c \left( \frac{2}{T} \cdot \frac{1 - z^{-1}}{1 + z^{-1}} \right) + \omega_c^2}$$


#### 2.3.3 分子分母同乘$(1 + z^{-1})^2$：
$$
H(z) = \frac{ \omega_c^2 (1 + z^{-1})^2 }{
    \dfrac{4}{T^2} (1 - z^{-1})^2
    + \dfrac{2\sqrt{2}\omega_c}{T} (1 - z^{-2})
    + \omega_c^2 (1 + z^{-1})^2
}
$$

#### 2.3.4 展开分母：
$$
\text{分母} = 
\underbrace{\left[ \left( \frac{2}{T} \right)^2 + \sqrt{2}\omega_c \frac{2}{T} + \omega_c^2 \right]}_{K_0} + 
\underbrace{\left[ -2 \left( \frac{2}{T} \right)^2 + 2\omega_c^2 \right]}_{K_1} z^{-1} + 
\underbrace{\left[ \left( \frac{2}{T} \right)^2 - \sqrt{2}\omega_c \frac{2}{T} + \omega_c^2 \right]}_{K_2} z^{-2}
$$

#### 2.3.5 归一化传递函数
$$H(z) = \frac{
\frac{\omega_c^2}{K_0} + \frac{2\omega_c^2}{K_0} z^{-1} + \frac{\omega_c^2}{K_0} z^{-2}
}{
1 + \frac{K_1}{K_0} z^{-1} + \frac{K_2}{K_0} z^{-2}
}$$
一般定义：$$
\omega_c = 2 \pi f_c
$$
但是，matlab等工具对$\omega_c$进行预失真变换：
$$
\omega_c = 2 f_s \tan\!\left( \frac{\pi f_c}{f_s} \right)
$$

系数为：
$$
\begin{aligned}
b_0 &= \omega_c^2 / K_0 \\
b_1 &= 2\omega_c^2 / K_0 \\
b_2 &= \omega_c^2 / K_0 \\
a_1 &= K_1 / K_0 \\
a_2 &= K_2 / K_0
\end{aligned}
$$

---

### 2.4 滤波器的时域实现（差分方程）


由 IIR 滤波器的系统函数表达式：

$$
H(z) = \frac{Y(z)}{X(z)} = \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}
$$

将其变形为：

$$
Y(z) \cdot (1 + a_1 z^{-1} + a_2 z^{-2}) = X(z) \cdot (b_0 + b_1 z^{-1} + b_2 z^{-2})
$$

对上述等式进行展开，并取反 Z 变换（对应回到时域），得到：

$$
y[n] + a_1 y[n-1] + a_2 y[n-2] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2]
$$

接着，我们将带有 \( y[n] \) 的项移到左边，将其解出为：

$$
y[n] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2] - a_1 y[n-1] - a_2 y[n-2]
$$

---

### 2.5 IIR低通滤波器的典型特性
#### 2.5.1 滤波器系数关系
| 特性 | 数学关系 | 物理意义 |
|------|----------|----------|
| **分子对称性** | $b_0 = b_2$ <br> $b_1 = 2b_0$ | 低通滤波器在通带内的对称频率响应特性 |
| **系数和** | $\sum b = \sum a$ <br> $b_0 + b_1 + b_2 = 1 + a_1 + a_2$ | 保证滤波器在直流（零频率）处的增益为1 |
| **稳定性条件** | $\|a_2\| < 1$ <br> $\|a_1\| < 1 + a_2$ | 确保系统稳定，特征方程的根在单位圆内 |
| **增益约束** | $H(1) = \frac{\sum b}{\sum a} = 1$ | 零频率响应为1（无衰减） |
| **高频衰减** | $H(-1) = \frac{b_0 - b_1 + b_2}{1 - a_1 + a_2} \approx 0$ | 在奈奎斯特频率处有最大衰减 |

##### 说明：
 - 分子对称性与系数和可由前文的公式中得出
 - 稳定性条件与见后文的极点章节描述
 - 增益约束中, 零频: $z = e^{j\theta}, \theta=0, z=1 $
 - 高频衰减中, 高频: $z = e^{j\theta}, \theta=\pi, z=-1 $

#### 2.5.2 零极点
##### 2.5.2.1 零极点的公式推导：
零点：$ B(z) = b_0 + b_1 z^{-1} + b_2 z^{-2} = 0 $ 利用对称性 $b_0 = b_2$ 和 $b_1 = 2b_0$可以得到 $ z=-1$

极点：$ {p_{1,2} = \frac{-a_1 \pm j \sqrt{4a_2 - a_1^2}}{2}} $

极点的模：$ \sqrt{a_2}$
##### 📌 IIR 滤波器零极点核心概念总结

| 概念             | 数学表达式                                                                 | 物理意义                                                                                  |
|------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 零点位置         | $z_{\text{zero}} = -1$ （二重根）                                            | 位于单位圆上，对应奈奎斯特频率 ($f_s/2$)，提供高频完全衰减                             |
| 极点位置         | $p_{1,2} = \dfrac{-a_1 \pm j \sqrt{4a_2 - a_1^2}}{2}$                          | 决定通带特性，靠近 $z=1$ 增强低频通过，角度 $\theta$ 决定谐振频率                     |
| 零点方程         | $z^2 + 2z + 1 = 0$                                                          | 源于分子多项式对称性 $b_0 = b_2$, $b_1 = 2b_0$                                           |
| 极点方程         | $z^2 + a_1 z + a_2 = 0$                                                     | 分母多项式决定系统动力学特性                                                             |
| 零极点模值       | $r = \sqrt{a_2}$                                      | $r_{\text{pole}}$ 决定谐振强度（$r \uparrow \Rightarrow Q \uparrow$），零点 $r=1$     |
| 零极点角度 | $\theta_{\text{pole}} = \tan^{-1}\left(\dfrac{\sqrt{4a_2 - a_1^2}}{a_1}\right)$ | $\theta_{\text{pole}}$ 决定谐振频率：$f_{\text{res}} = \dfrac{\theta}{2\pi}f_s$ |
| 稳定性条件 | $ \sqrt{a_2} < 1$  | 所有极点必须在单位圆内，保证系统稳定    |
| 频率响应         | $H(e^{j\omega}) = \dfrac{\prod\| e^{j\omega} - z_k\|}{\prod\|e^{j\omega} - p_k\|}$ | 零点衰减特定频率，极点增强特定频率 
| 直流响应         | $H(1) = \dfrac{\sum b_k}{\sum a_k} = 1$                                     | 保证零频率信号无衰减通过                                                                 |
| 高频响应         | $H(-1) = \dfrac{b_0 - b_1 + b_2}{1 - a_1 + a_2} = 0$                         | 奈奎斯特频率处完全衰减                                                                   |
| 脉冲响应         | $h[n] = r^n \cos(\theta n) u[n]$                                             | 极点决定衰减速率 ($r$) 和振荡频率 ($\theta$)                                            |
| 品质因数         | $Q = \dfrac{1}{2(1 - r)}$                                                   | 衡量滤波器选择性，$r \uparrow \Rightarrow Q \uparrow$                                   |

#### 2.5.3 建立时间、衰减效应、振铃效应
##### 2.5.3.1 建立时间
为了推导建立时间，我们分析滤波器的阶跃响应。输入为阶跃序列 $x[n] = u[n]$（单位阶跃），其 $z$ 变换为：

$$
X(z) = \frac{1}{1 - z^{-1}}
$$

输出的 $z$ 变换为：

$$
Y(z) = H(z) \cdot X(z) = H(z) \cdot \frac{1}{1 - z^{-1}}
$$

假设 $H(z)$ 的分母多项式有两个极点 $p_1$ 和 $p_2$（复共轭），且 $H(z)$ 在 $z = 1$ 处无极点（即直流增益存在），则 $Y(z)$ 可表示为部分分式分解：

$$
Y(z) = \frac{A}{1 - z^{-1}} + \frac{B}{1 - p_1 z^{-1}} + \frac{C}{1 - p_2 z^{-1}}
$$
其中：
 - $ \frac{A}{1 - z^{-1}} $, 其逆$z$变换$Au[n]$,是稳态的增益
 - $ \frac{B}{1 - p_1 z^{-1}} $, 其逆$z$变换$B p_1^n u[n]$,是以$p_1$极点为核心的衰减响应
 - $ \frac{C}{1 - p_2 z^{-1}} $, 其逆$z$变换$C p_2^n u[n]$,是以$p_2$极点为核心的衰减响应
 - 考虑到$p_1$ $p_2$为共轭复数，$\frac{B}{1 - p_1 z^{-1}} + \frac{C}{1 - p_2 z^{-1}}$在时域的响应$B p_1^n u[n] + C p_2^n u[n]$可以转变为$e[n] = D r^n \cos(\theta n + \phi)$, $D$经过推导，约为1

可以看到，IIR滤波器对于阶跃响应可以拆分为常量增益+指数衰减；当指数衰减项达到预期的抖动范围 $ \alpha=0.01$ 时，我们判定滤波器达到稳定，其建立时间为$t_s = n_s T \approx \frac{ \ln(1/\alpha) \cdot T }{ |\ln r|}=\frac{ 2 \ln(\alpha) \cdot T }{ \ln a_2}$
其中 $T$ 是采样时间

##### 2.5.3.2 衰减效应与振铃效应：
由前文推导可以知道，IIR滤波器的时域响应可以拆分为常量的阶跃信号+衰减的余弦信号，衰减的余弦信号在时域上表现为振铃；

振铃的幅值: $r^n =a_2^{n/2}$

振铃的周期: $T=\dfrac{2 \pi}{\theta} = \dfrac{2 \pi} {\arctan\left( \dfrac{\sqrt{4 a_2 - a_1^2}}{\left| a_1 \right|} \right) }$

###### D的推导（计算太复杂，后续待补充）

### 2.6 IIR低通滤波器的量化误差分析
IIR滤波器的浮点传递函数如前文所述：
$$
H(z) = \frac{Y(z)}{X(z)} = \frac{b_0^{\text{float}} + b_1^{\text{float}} z^{-1} + b_2^{\text{float}} z^{-2}}{1 + a_1^{\text{float}} z^{-1} + a_2^{\text{float}} z^{-2}}
$$
在实际硬件实现(atria2, Pollux)时，输入为S16定点数(输入由模拟传给数字，不需要量化);滤波器系数量化至U16,量化系数为$2^{-15}$,数值范围[0, 2);反馈的的$y_1$ $y_2$为S16.11,包含S16的整数部分与*U11*的小数部分。

IIR滤波器的量化误差包含2部分:**滤波器系数的量化误差与反馈$y_1$ $y_2$的量化误差。需要注意的是，由于反馈路径与衰减效应的存在，量化误差会积累并放大至特定倍率后稳定。**。

可以运行仿真代码 **IIR_quant_error_simulator.ipynb** 观测误差

#### 2.6.1 系数量化误差(忽视反馈$y_1$ $y_2$的量化误差)
##### 2.6.1.1 低频(常数) 输入的量化误差
当输入信号为幅值为SignalRange的常数或低频信号时，$z=1$
$$
\frac{Y^{float}}{X} = \frac{b_0^{\text{float}} + b_1^{\text{float}} z^{-1} + b_2^{\text{float}} z^{-2}}{1 + a_1^{\text{float}} z^{-1} + a_2^{\text{float}} z^{-2}}=\frac{b_0^{\text{float}}+b_1^{\text{float}}+b_2^{\text{float}}}{1+a_1^{\text{float}}+a_2^{\text{float}}}=\frac{\Sigma{b}}{\Sigma{a}}
$$

IIR滤波器的系数在进行定点量化时，其传递函数为：
$$
b_0^{\text{fix}} = b_0^{\text{float}} + \delta_{b_0} \\
b_1^{\text{fix}} = b_1^{\text{float}} + \delta_{b_1} \\
b_2^{\text{fix}} = b_2^{\text{float}} + \delta_{b_2} \\
a_1^{\text{fix}} = a_1^{\text{float}} + \delta_{a_1} \\
a_2^{\text{fix}} = a_2^{\text{float}} + \delta_{a_2} \\
\delta_{b}=\delta_{b_0} + \delta_{b_1} + \delta_{b_2}\\
\delta_{a}=\delta_{a_1} + \delta_{a_2}\\
H(z)^{fix} = \frac{Y^{fix}}{X} = \frac{b_0^{\text{fix}} + b_1^{\text{fix}} z^{-1} + b_2^{\text{fix}} z^{-2}}{1 + a_1^{\text{fix}} z^{-1} + a_2^{\text{fix}} z^{-2}} = \frac{b_0^{\text{fix}} + b_1^{\text{fix}} + b_2^{\text{fix}} }{1 + a_1^{\text{fix}} + a_2^{\text{fix}} }=\frac{\Sigma{b}+\delta_{b}}{\Sigma{a}+\delta_{a}}
$$
总的量化误差为：
$$
CoeffQuantError=Y^{fix}-Y^{float}=(\frac{\Sigma{b}+\delta_{b}}{\Sigma{a}+\delta_{a}}-\frac{\Sigma{b}}{\Sigma{a}})X=\frac{\Sigma{a}\Sigma{b}+\Sigma{b}\delta_{a}-\Sigma{a}\Sigma{b}-\Sigma{a}\delta_{b}}{(\Sigma{a}+\delta_{a})\Sigma{a}}X
$$
考虑到低通滤波器中，$\Sigma{a}=\Sigma{b}$且$\delta_{a}<<\Sigma{a}$,上式可以进一步优化：
$$
CoeffQuantError=\frac{\Sigma{b}\delta_{a}-\Sigma{a}\delta_{b}}{\Sigma{a} \Sigma{a}}X=\frac{\delta_{a}-\delta_{b}}{\Sigma{a}}X=\frac{\delta_{a}-\delta_{b}}{\Sigma{a}}\text{SignalRange}
$$
其中，$\Sigma{a}$与$\delta_{a}-\delta_{b}$在设置截至频率与量化系数(位宽)时即可确定。
##### 2.6.1.2 低频(常数) 输入的量化误差
在输入信号频率不为0时，传递函数$H(z)$内的$z$无法取0；因此实际的噪声误差需要通过仿真得到。由实验结果可以观测到：随着频率增加到fc，量化噪声逐渐增加，约达到1.5倍；超过截至频率，量化噪声衰减。

#### 2.6.2 反馈$y_1$ $y_2$的量化误差(忽视滤波器系数的量化误差)
当反馈回路$y_1$与$y_2$的位宽较小时，反馈回路的量化噪声无法忽视，在定点模型仿真/RTL实现时，设置反馈$y_1 y_2$的小数位宽为$r_b$
$$
y[n] = b_0 x[n] + b_1 x[n-1] + b_2 x[n-2] - ⌊a_1 y[n-1] + a_2 y[n-2]⌋)>>r_b
$$
其中，⌊x⌋为向下取整；$b_0 b_1 b_2 a_1 a_2$均为U1.15的定点数 $x[n]$为S16的定点数，$y[n-1]$与$y[n-2]$均为用于反馈的S$16.r_b$的定点数。下述代码展示了$\Sigma(bx)-\Sigma(ay)$的数据类型;
```
sum = 0 1 1 0 1 0 1 0 1 1 0 1 1 1 1 0 0 0 0 0 1 1 1 1 1 0 1 0 1 0 1 0
      └───Integer (High S16 bits) ──┘ └───Fraction (Low 16 bits)────┘
      <---------------  used for feed back  --------------->
      <--- Y(usd for y[n]output) ---> <----Reserved rb ---->
```
由上述$y[n]$的时序公式可以得到实际的传递函数;需要注意的是，在本小章节的公式推导中中，忽视滤波器系数的定点误差，即$b^{float}=b^{fix}$；此外，反馈的量化噪声是与输入$X$无关：
$$
H(z)^{fix} = \frac{Y^{fix}}{X} = \frac{b_0 + b_1z^{-1} + b_2z^{-2}}{1 + a_1 z^{-1} + a_2z^{-2} + \delta_{y}} 
$$
其中，$\delta_{y}$是引入的量化误差小量，可以得到反馈误差：
$$
FeedbackQuantError=Y^{fix}-Y^{float}=(\frac{\Sigma{b}}{\Sigma{a}+\delta_{y}}-\frac{\Sigma{b}}{\Sigma{a}})=\frac{\Sigma{a}\Sigma{b}-\Sigma{a}\Sigma{b}-\Sigma{b}\delta_{y}}{(\Sigma{a}+\delta_{y})\Sigma{a}}=\frac{\delta_{y}}{\Sigma{b}+\delta_{y}}=\frac{\delta_{y}}{\Sigma{b}}=\frac{2 ^ {-r_b}}{\Sigma{b}}
$$

#### 2.6.3 多级模块级联引入输入量化误差
$$
FeedbackQuantError=Y^{fix}-Y^{float}=\frac{\Sigma{b}\delta_{x}}{\Sigma{a}}=\delta_{x}
$$
即输出的量化误差为输入的量化误差的直传，无增益。