设：

$$
x(t) = \text{rect}\left(\frac{t}{2}\right), \quad h(t) = \text{rect}\left(\frac{t}{4}\right)
$$

即：

- \( x(t) = 1 \) for \( |t| < 1 \)，0 otherwise  
- \( h(t) = 1 \) for \( |t| < 2 \)，0 otherwise

它们的卷积为：

$$
y(t) = (x * h)(t) = \int_{-\infty}^{\infty} x(\tau) h(t - \tau) \, d\tau
$$

---

分段计算 \( y(t) \)：

#### 1. \( t < -3 \)

两函数无重叠，积分为 0：

$$
y(t) = 0
$$

---

#### 2. \( -3 \le t < -1 \)

重叠区间：\( \tau \in [ -1, t + 2 ] \)

$$
y(t) = \int_{-1}^{t + 2} 1 \cdot 1 \, d\tau = t + 3
$$

---

#### 3. \( -1 \le t < 1 \)

完全重叠，重叠区间：\( \tau \in [ -1, 1 ] \)

$$
y(t) = \int_{-1}^{1} 1 \cdot 1 \, d\tau = 2
$$

---

#### 4. \( 1 \le t < 3 \)

重叠区间：\( \tau \in [ t - 2, 1 ] \)

$$
y(t) = \int_{t - 2}^{1} 1 \cdot 1 \, d\tau = 3 - t
$$

---

#### 5. \( t \ge 3 \)

无重叠，积分为 0：

$$
y(t) = 0
$$

---

### 结果：

\[
y(t) =
\begin{cases}
0, & t < -3 \\
t + 3, & -3 \le t < -1 \\
2, & -1 \le t < 1 \\
3 - t, & 1 \le t < 3 \\
0, & t \ge 3
\end{cases}
\]
