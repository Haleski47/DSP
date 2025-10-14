# CIC (Sinc) 滤波器设计文档

# 1. 引言

本文档介绍 CIC（Cascaded Integrator-Comb）滤波器的理论分析、数学推导、频率响应特性与实现要点。  
包括以下几个部分：
- CIC 滤波器的基本原理与冲激响应
- 数学建模与频率响应推导
---
# 2 CIC滤波器理论分析
## 2.1 CIC 滤波器简介

CIC 滤波器是一种特殊的 FIR 滤波器，系数全为 1，可通过累加器与延时单元实现，无需乘法器和系数存储。  
其核心优点：
- 系数为 1，硬件实现极其简单  
- 适合大倍率抽取/插值场景  
- 频率响应为 sinc 函数形式，具有明显的低通特性(积分器)

---
## 2.2 冲激响应

CIC 滤波器的冲激响应(不包含下采样)为：

$$
h(n) =
\begin{cases}
1, & 0 \leq n \leq D - 1 \\
0, & \text{others}
\end{cases}
$$

其中：  
- \( D \)：抽取因子（decimation factor）

---
## 2.3 系统函数与幅频响应推导

对冲激响应进行 \( z \)-变换，得到：

$$
H(z) = \sum_{n=0}^{D-1} h(n) z^{-n} = \frac{1 - z^{-D}}{1 - z^{-1}}
$$

## 2.3.1 频率响应推导

令 \(z=e^{j\omega}\)（\(\omega\) 为归一化的数字角频率，$\omega = 2\pi \cdot \frac{f}{f_s}$），得到:
$$
H(e^{j\omega})=\frac{1-e^{-j\omega D}}{1-e^{-j\omega}} \tag{1}
$$

### 2.3.2 欧拉恒等式：  
$$
e^{j\theta}-e^{-j\theta}=2j\sin\theta \\
1-e^{-j\theta}=e^{-j\theta/2}\big(e^{j\theta/2}-e^{-j\theta/2}\big)
$$

### 2.3.3 简化分子
$$
\begin{aligned}
1-e^{-j\omega D}
&=e^{-j\omega D/2}\Big(e^{j\omega D/2}-e^{-j\omega D/2}\Big) \\
&=e^{-j\omega D/2}\cdot 2j\,\sin\!\left(\frac{\omega D}{2}\right)
\end{aligned}
$$

### 2.3.4 简化分母
$$
\begin{aligned}
1-e^{-j\omega}
&=e^{-j\omega} \\ 
\end{aligned}
$$

### 2.3.5 得到 CIC 滤波器的频率响应为：

$$
H(e^{j\omega}) = e^{-j\omega \frac{(D-1)}{2}} \frac{\sin\left( \frac{\omega D}{2} \right)}{\sin\left( \frac{\omega}{2} \right)}
$$

其中：
- \( D \)：抽取因子  
- \( e^{-j\omega \frac{(D-1)}{2}} \)：线性相位项  
- 分子分母之比为 sinc 函数形式

### 2.3.6 零点分析

由系统函数：

$$
H(z) = \frac{1 - z^{-D}}{1 - z^{-1}}
$$

可知零点分布为：

$$
z^D = 1 \quad \Rightarrow \quad z = e^{j\frac{2\pi k}{D}}, \quad k = 0, 1, \dots, D-1
$$

说明 CIC 滤波器在抽取倍频点处具有零点，对混叠信号有强抑制作用。

---

### 2.3.7 幅频响应 (sinc1, D=8)
幅频响应像梳子，又名梳状滤波器
![CIC滤波器幅频响应](./pic/sinc_freq.jpg)


### 2.3.8 第一旁瓣的幅值衰减：
即第一旁瓣幅度为：

$$
A = \left| H(e^{j\omega}) \right|_{\omega = \frac{3\pi}{D}} 
   = \left| \frac{\frac{3\pi}{2}}{\sin\left(\frac{3\pi}{2D}\right)} \right| 
   = \left| \frac{1}{\sin\left(\frac{3\pi}{2D}\right)} \right|
\tag{5}
$$

当 \( D \gg 1 \) 时，有近似关系：

$$
\sin\left(\frac{3\pi}{2D}\right) \approx \frac{3\pi}{2D}
\tag{6}
$$

因此，第一旁瓣幅度可近似为：

$$
A = \left| \frac{1}{\sin\left(\frac{3\pi}{2D}\right)} \right| 
  \approx \frac{2D}{3\pi}
\tag{7}
$$

则 CIC 滤波器的阻带衰减为：

$$
\alpha = 20\log\left( \frac{A}{D} \right) 
\approx 20\log\left( \frac{2}{3\pi} \right) 
\approx -13.46\,\mathrm{dB}
\tag{8}
$$

可以看到，不同D下，第一旁瓣的信号衰减几乎一致
![CIC滤波器幅频响应](./pic/sinc1_different_osr.png)

## 2.4 CIC滤波器+下采样
原始的cic滤波器结构如下,在经过CIC滤波后，采用下采样降低数据率：
![原始CIC滤波器](./pic/cic_ori.jpg)
根据Noble变换恒等式，可以将CIC滤波器结构变换为：
![改进CIC滤波器](./pic/cic_modify.jpg)
经过改善，差分的数据率得到降低

### 补充：Noble变换恒等式
### 2.4.1. 定义

**Noble 变换恒等式（Noble Identity）** 是多速率数字信号处理中的一个重要数学工具，用于描述**抽取（Decimation）或插值（Interpolation）操作与线性时不变系统（LTI 系统）之间的等价变换关系**。  
它允许我们**交换滤波器与抽取/插值的顺序**，在不改变系统整体输入输出关系的前提下，大幅降低运算复杂度。

---
### 2.4.2 抽取（Decimation）形式

当系统中存在抽取操作 \( \downarrow M \) 时，Noble 恒等式表明：

$$
\boxed{ [H(z)x[n]] \downarrow M = H(z^M)[x[n] \downarrow M] }
$$

含义如下：

- 左侧：先对信号 \( x[n] \) 进行滤波，再抽取（每隔 \( M \) 个样本取一个）  
- 右侧：先对信号抽取，然后通过系统函数为 \( H(z^M) \) 的滤波器

📌 **解释：**  
- 滤波器 \( H(z) \) 与抽取 \( \downarrow M \) 可交换位置  
- 交换后系统函数变量由 \( z \) 变为 \( z^M \)，例\( z^{-D} \) -> \( ({z^M})^{-D} \) -> \( z^{-DM} \)

---

### 2.4.3 插值（Interpolation）形式

对于插值操作 \( \uparrow L \)，Noble 恒等式同样成立：

$$
\boxed{ \uparrow L [H(z)x[n]] = H(z^L) [\uparrow L x[n]] }
$$

含义如下：

- 左侧：先滤波再插值（在样本之间插入 \( L-1 \) 个零）  
- 右侧：先插值，再通过系统函数为 \( H(z^L) \) 的滤波器

📌 **解释：**  
- 插值器 \( \uparrow L \) 与滤波器可交换位置  
- 交换后滤波器的系统函数变量变为 \( z^L \)

---

### 2.4.4 CIC差分+下采样的nobel定理证明
#### 2.4.4.1 时域证明
设原始高速采样序列为：

$$
v[m] = x[mR]
$$

其中：
- \( x[n] \)：高速域输入信号
- \( R \)：抽取因子
- \( v[m] \)：抽取后的低速域序列

在抽取后进行梳状差分（延时 \( M \)）：

$$
\begin{aligned}
y[m] &= v[m] - v[m - M] \\
     &= x[mR] - x[(m - M)R] \\
     &= x[mR] - x[mR - MR]
\end{aligned}
$$

现在把它改写为“**先在高速域做差分，再抽取**”的形式。定义高速域差分（延时 \( MR \)）：

$$
u[n] = x[n] - x[n - MR]
$$

则抽取后的输出可以表示为：

$$
y[m] = u[mR] = (x[n] - x[n - MR])\Big|_{n = mR}
$$

因此，得到等效关系：

$$
\boxed{\downarrow R \rightarrow (1 - Z^{-M}) } 
\quad \equiv \quad 
\boxed{ (1 - z^{-MR}) \rightarrow \downarrow R }
$$

也就是说：**抽取后延时为 \( M \) 的梳状器，等效于抽取前延时为 \( MR \) 的梳状器**。

---
#### 2.4.4.2 Z域证明
抽取后的低速域梳状器传递函数为：

$$
H_{\mathrm{comb,low}}(Z) = 1 - Z^{-M}
$$

低速域复变量 \( Z \) 与高速域复变量 \( z \) 的关系为：

$$
Z = z^R
$$

---
补充直观理解$Z = z^R$（频率角度）

在抽取前后，采样频率从 \( f_s \) 变为 \( \frac{f_s}{R} \)，  
这意味着“一个数字频率周期”对应的角度缩小了 \( R \) 倍。

- 抽取前数字频率变量为 \( \omega \)
- 抽取后数字频率变量为 \( \Omega \)

它们的关系为：

$$
\Omega = R\omega
$$

而在 \( z \)-域中：

$$
z = e^{j\omega}, \quad Z = e^{j\Omega} = e^{jR\omega} = (e^{j\omega})^R = z^R
$$

---

因此，将低速域传函换算回高速域：

$$
\begin{aligned}
H_{\mathrm{comb,high}}(z) 
&= H_{\mathrm{comb,low}}(Z)\Big|_{Z = z^R} \\
&= 1 - (z^R)^{-M} \\
&= 1 - z^{-MR}
\end{aligned}
$$

✅ 这个结果与时域推导的结论完全一致：**低速域延时 \( M \) 的梳状器，等价于高速域延时 \( MR \) 的梳状器**。

---
## 2.5 CIC滤波器的级联
![CIC滤波器级联](./pic/cic_multi.jpg)
### 2.5.1 时域分析
N 阶 CIC 的冲激响应等于长度为 \(D\) 的矩形序列
\[
h[n]=
\begin{cases}
1, & 0\le n\le D-1\\
0, & \text{else}
\end{cases}
\]
的 N 次自卷积：
\[
h_N[n]=\underbrace{h[n]*h[n]*\cdots*h[n]}_{\text{N 次}}.
\]
因此：
- **非零支撑**：\(n\in[0,\ N(D-1)]\)，长度为 \(N(D-1)+1\)；
- **系数**：为多项式 \(\big(1+z^{-1}+\cdots+z^{-(D-1)}\big)^{N}\) 的系数（对应该区间的整数点）。  
  等价地，可用递推卷积实现：
  \[
  h_1[n]=h[n],\quad h_k[n]=(h_{k-1}*h)[n],\ k=2,\dots,N.
  \]
- **系数可视化**
![CIC滤波器等效系数](./pic/CIC_Coeff.jpg)
---

### 2.5.2 Z域分析
N 阶 CIC（等价为长度为 \(D\) 的箱体序列做 N 次自卷积）的系统函数：
\[
H_N(z)=\left(\frac{1-z^{-D}}{1-z^{-1}}\right)^{N}.
\]

- **零点**：\(1-z^{-D}=0 \Rightarrow z^{D}=1\)。所有 \(D\) 次单位根处均为**N 重零点**。
- **极点**：\((1-z^{-1})^{-N}\) 在 \(z=1\) 处为 N 重极点，与分子在 \(z=1\) 的 N 重零点**相消**，因此 \(H_N(z)\) 在 \(z=1\) 处**有限**。
- **直流增益**（取极限或直接代入频响极限）：
\[
H_N(e^{j0})=\lim_{\omega\to 0}\left(\frac{\sin\frac{D\omega}{2}}{\sin\frac{\omega}{2}}\right)^{\!N}
= D^{N}.
\]
- **群时延（线性相位）**：\( \tau_g = \dfrac{N(D-1)}{2} \) 个采样。

#### 2.5.3 频率响应（\(z=e^{j\omega}\)）
\[
H_N(e^{j\omega})
= e^{-j\omega\,\frac{N(D-1)}{2}}
\left(\frac{\sin\!\left(\frac{D\omega}{2}\right)}{\sin\!\left(\frac{\omega}{2}\right)}\right)^{\!N}.
\]
- **幅度**：
\[
\big|H_N(e^{j\omega})\big|
= \left|\frac{\sin\!\left(\frac{D\omega}{2}\right)}{\sin\!\left(\frac{\omega}{2}\right)}\right|^{\!N}.
\]
- **归一化幅度（对直流）**：
\[
\frac{|H_N(e^{j\omega})|}{D^{N}}
= \left|\frac{\mathrm{sinc}\!\left(\frac{D\omega}{2}\right)}{\mathrm{sinc}\!\left(\frac{\omega}{2}\right)}\right|^{\!N}
\quad\text{（此处 }\mathrm{sinc}(x)=\frac{\sin x}{x}\text{）}.
\]
![CIC滤波器级联的幅频响应](./pic/cic_mul_order.jpg)

- **零点频率**：\(\omega_k = \dfrac{2\pi k}{D},\ k=1,\dots,D-1\)（各为 **N 重零点**）。
- **旁瓣趋势**：幅度包络随频率高次衰减，第一旁瓣（相对 N=1 的 \(-13.26\) dB）在 **dB 量级上近似乘以 N**：
\[
A_{\text{1st\,sidelobe,dB}} \approx N \times (-13.26\ \mathrm{dB}).
\]
---

## 2.6 CIC的补偿滤波器

### 待补充

## 2.7 其他
### 2.7.1 差分延时delay


## 4 特性总结

## 4 特性总结

| 特性类别 | 表达式 / 数学关系 | 物理意义与解释 |
|----------|--------------------|------------------|
| **系数结构** | $h[n] = 1,\quad 0 \le n \le D-1$ | 系数全部为 1，无需乘法器，硬件极为简单 |
| **系统函数** | $H(z) = \dfrac{1 - z^{-D}}{1 - z^{-1}}$ | 积分器 + 梳状结构等效，实质为箱形滤波器的 Z 域表示 |
| **冲激响应长度** | $L = D$（单级） <br> $L = N(D-1)+1$（N 级） | 随阶数 N 增大而变长，时域响应逐渐平滑，近似多项式形状 |
| **幅频响应** | $H(e^{j\omega}) = e^{-j\omega\frac{(D-1)}{2}} \dfrac{\sin(\frac{D\omega}{2})}{\sin(\frac{\omega}{2})}$ | 为 sinc 型低通响应，具有梳状零点特性，抑制抽取频率倍频点上的混叠分量 |
| **主瓣带宽** | $\Delta\omega \approx \dfrac{2\pi}{D}$ | 随抽取率 \(D\) 增大而变窄，频率选择性提高 |
| **零点位置** | $z^D = 1$ <br> $\omega_k = \dfrac{2\pi k}{D}$ | 在抽取倍频点出现零点，对混叠信号有强抑制作用 |
| **旁瓣特性** | $A_{\mathrm{1st}} \approx 20\log_{10}\dfrac{2}{3\pi} \approx -13.46\ \mathrm{dB}$（单级） <br> $A_{\mathrm{1st}} \approx N\times(-13.26\ \mathrm{dB})$（N 级） | 第一旁瓣抑制固定，级联后旁瓣衰减随 N 增强 |
| **直流增益** | $ D^N $ | 直流处增益大，需在定标或补偿时考虑（通常后续模块需除以 \(D^N\)） |
| **相位响应** | $e^{-j\omega\frac{(D-1)}{2}}$ | 线性相位，群时延常数：$\tau_g = \dfrac{(D-1)}{2}$（单级）<br> $\tau_g = \dfrac{N(D-1)}{2}$（N 级） |
| **系统阶数影响** | $H_N(z)=\left(\dfrac{1 - z^{-D}}{1 - z^{-1}}\right)^N$ | 增大 N 会加深阻带抑制、增宽冲激响应、提高旁瓣衰减、直流增益变为 $D^N$ |
| **复杂度与实现** | 积分器 + 梳状器：$N$ 个加法器、$N$ 个延时单元 | 不含乘法运算、无系数存储，硬件实现代价极低，适合 FPGA/ASIC 高速采样系统 |
| **适用场景** | 大倍率抽取/插值、ΣΔ-ADC 数字降采样链路、软件无线电前端等 | CIC 滤波器通过前端抑制混叠，常与补偿 FIR 配合以提升通带平坦度 |


---

