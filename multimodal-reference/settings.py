import numpy as np
import matplotlib.pyplot as plt

# 解决中文显示，优先试DejaVuSans不行再换SimHei
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

z = np.linspace(-6, 6, 200)
y = sigmoid(z)

plt.plot(z, y, color="#1f77b4", label=r'$\sigma(z)=\frac{1}{1+e^{-z}}$')
plt.axhline(y=0.5, color='red', linestyle='--', lw=0.8, label='阈值 0.5')
plt.axvline(x=0, color='gray', linestyle='--', lw=0.8)

# 【修复重点】公式放$内，中文放在外面
plt.xlabel(r"$z = X\beta$（线性部分输出）")
plt.ylabel(r"概率 $P(y=1|X)$")
plt.title("Sigmoid 函数曲线（逻辑回归）")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
