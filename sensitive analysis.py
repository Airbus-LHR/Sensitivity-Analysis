import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.colors as mcolors
from matplotlib.ticker import MaxNLocator, FormatStrFormatter
from matplotlib.colors import ListedColormap

params = {
    'W': 225000 * 0.95,      # Efficient Energy (J)
    'g': 9.81,               # Acceleration due to Gravity (m/s²)
    'rho': 1.22,             # Air density (kg/m³)
    'A': 665e-4,             # Contact Surface Area (m²)
    'Cd': 0.3069,            # Drag Coefficient
    'm_drone': 0.734,        # Weight (kg)
    'eta': 0.6471,           # Efficiency
}

def calculate_range(m_total, v, cd, eta, rho):
    M = params['W'] * eta
    g = params['g']
    
    c = m_total * g * np.sqrt((m_total * g)/(rho * params['A']))
    k = 0.5 * cd * rho * params['A']
    numerator = M - m_total * g * 20 - 0.5 * m_total * v ** 2
    
    denominator = k*v**2 + c/v
    
    s = numerator / denominator / 1000
    
    return max(0, s)

weight = np.round(np.arange(0.1, 1.1, 0.1), 1)
speeds = np.round(np.arange(5, 21, 1), 1)
cd_values = np.round(np.arange(0.2, 0.51, 0.05), 2)
efficient = np.round(np.arange(0.5, 0.91, 0.02), 2)
density = np.round(np.arange(1.1, 1.31, 0.01), 2)

fixed_speed = 12

payload_analysis = pd.DataFrame({
    'Weight (kg)': weight,
    'Range (km)': [calculate_range(w, fixed_speed, params['Cd'], params['eta'], params['rho']) for w in weight]
})

efficiency_analysis = pd.DataFrame({
    'Efficiency': efficient,
    'Range (km)': [calculate_range(params['m_drone'], fixed_speed, params['Cd'], e, params['rho']) for e in efficient]
})

cd_analysis = pd.DataFrame({
    'C_d': cd_values,
    'Range (km)': [calculate_range(params['m_drone'], fixed_speed, CD, params['eta'], params['rho']) for CD in cd_values]
})

density_analysis = pd.DataFrame({
    'Density': density,
    'Range (km)': [calculate_range(params['m_drone'], fixed_speed, params['Cd'], params['eta'], ro) for ro in density]
})

payload_grid, speed_grid = np.meshgrid(weight, speeds)
results = np.zeros_like(payload_grid)

for i in range(payload_grid.shape[0]):
    for j in range(payload_grid.shape[1]):
        results[i,j] = calculate_range(payload_grid[i,j], speed_grid[i,j], 
                                      params['Cd'], params['eta'], params['rho'])

matrix_analysis = pd.DataFrame(
    results,
    index=[f"{v}m/s" for v in speeds],
    columns=[f"{w}kg" for w in weight]
)

plt.figure(figsize=(12, 6))

plt.subplot(2, 2, 1)
sns.lineplot(data=payload_analysis, x='Weight (kg)', y='Range (km)')
plt.title('Weight Sensitivity Analysis')

plt.subplot(2, 2, 2)
sns.lineplot(data=efficiency_analysis, x='Efficiency', y='Range (km)')
plt.title('Efficiency Sensitivity Analysis')

plt.subplot(2, 2, 3)
sns.lineplot(data=cd_analysis, x='C_d', y='Range (km)')
plt.title('Drag Coefficient Sensitivity Analysis')

plt.subplot(2, 2, 4)
sns.lineplot(data=density_analysis, x='Density', y='Range (km)')
plt.title('Density Sensitivity Analysis')

plt.tight_layout()

plt.figure(figsize=(12, 8))
max_range = matrix_analysis.values.max()
custom_cmap = sns.color_palette("YlGnBu", n_colors=256)
custom_cmap = ListedColormap(custom_cmap)
sns.heatmap(
    matrix_analysis, 
    annot=False, 
    cmap=custom_cmap, 
    vmin=0, 
    vmax=100,
    cbar_kws={
        "label": "Flight Range (km)",
        "ticks": MaxNLocator(nbins=10),
        "format": FormatStrFormatter("%.2f"),
        "spacing": "proportional"
    },
)
plt.title("Dual-variable Sensitivity Analysis")
plt.xlabel("Weight (kg)")
plt.ylabel("Speed (m/s)")

print("单变量分析示例：")
print(payload_analysis.head())
print("\n双变量分析矩阵示例：")
print(matrix_analysis.iloc[:16, :6])

plt.show()
