import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

def procesar_datos_dbld(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()[2:]
    data_rows = []
    for line in lines:
        if ':' in line:
            clean_line = line.split(':')[1].strip()
            row = [int(val) for val in clean_line.split()]
            data_rows.append(row)
    data = np.array(data_rows)

    total_p = np.sum(data)
    y, x = np.indices(data.shape)

    # CoP y Distribuciones
    cop_x = np.sum(x * data) / total_p
    cop_y = np.sum(y * data) / total_p
    mitad_c = data.shape[1] // 2
    izq_p = (np.sum(data[:, :mitad_c]) / total_p) * 100
    der_p = (np.sum(data[:, mitad_c:]) / total_p) * 100

    # Front/Back (F/B) pressure distribution
    mitad_f = data.shape[0] // 2
    frente_p = (np.sum(data[:mitad_f, :]) / total_p) * 100
    detras_p = (np.sum(data[mitad_f:, :]) / total_p) * 100

    # Rotación: Centros de masa laterales
    data_izq, data_der = data[:, :mitad_c], data[:, mitad_c:]
    c_x_izq = np.sum(np.indices(data_izq.shape)[1] * data_izq) / np.sum(data_izq)
    c_y_izq = np.sum(np.indices(data_izq.shape)[0] * data_izq) / np.sum(data_izq)
    c_x_der = (np.sum(np.indices(data_der.shape)[1] * data_der) / np.sum(data_der)) + mitad_c
    c_y_der = np.sum(np.indices(data_der.shape)[0] * data_der) / np.sum(data_der)

    angulo = np.degrees(np.arctan2(c_y_izq - c_y_der, c_x_izq - c_x_der))
    # Ensure rotation angle is between 0 and 90 degrees
    rotacion = abs(angulo) if abs(angulo) <= 90 else 180 - abs(angulo)

    return {
        'data': data, 'cop': (cop_x, cop_y), 'izq': izq_p, 'der': der_p,
        'frente': frente_p, 'detras': detras_p,
        'rotacion': rotacion, 'puntos_rot': [(c_x_izq, c_y_izq), (c_x_der, c_y_der)]
    }

def comparar_ajustes_completo(file1, file2, notas=""):
    res1 = procesar_datos_dbld(file1)
    res2 = procesar_datos_dbld(file2)

    # Calcular Mapa de Diferencia
    diff_map = res2['data'].astype(float) - res1['data'].astype(float)

    fig, axes = plt.subplots(1, 3, figsize=(20, 10))
    fig.suptitle(f"INFORME DE AJUSTE BIOMECÁNICO\nCambios: {notas}", fontsize=16, fontweight='bold')

    datasets = [res1, res2]
    titles = ["ESTADO INICIAL", "POST-AJUSTE"]

    for i in range(2):
        sns.heatmap(datasets[i]['data'], ax=axes[i], cmap='magma', cbar=False)
        axes[i].set_title(titles[i])
        p1, p2 = datasets[i]['puntos_rot']
        axes[i].plot([p1[0], p2[0]], [p1[1], p2[1]], color='lime', linestyle='--', marker='o')
        axes[i].scatter(datasets[i]['cop'][0], datasets[i]['cop'][1], color='cyan', marker='X', s=150)

        info = f"L/R: {datasets[i]['izq']:.1f}% / {datasets[i]['der']:.1f}%\nF/B: {datasets[i]['frente']:.1f}% / {datasets[i]['detras']:.1f}%\nRot: {datasets[i]['rotacion']:.2f}°"
        axes[i].text(0.5, 0.05, info, transform=axes[i].transAxes, ha='center',
                     bbox=dict(facecolor='white', alpha=0.7))

    # Mapa de Diferencia (Subplot 3)
    limit = max(abs(diff_map.min()), abs(diff_map.max()))
    sns.heatmap(diff_map, ax=axes[2], cmap='RdBu_r', center=0, vmin=-limit, vmax=limit, cbar_kws={'label': 'Delta Presión'})
    axes[2].set_title("MAPA DE CAMBIOS (Diferencia)")
    axes[2].text(0.5, -0.1, "AZUL = Menos presión | ROJO = Más presión", transform=axes[2].transAxes, ha='center', color='gray')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

    # Create comparative table
    metrics_data = {
        'Metric': [
            'L/R Distribution (%)',
            'F/B Distribution (%)',
            'Rotation (°)'
        ],
        'ESTADO INICIAL': [
            f"{res1['izq']:.1f} / {res1['der']:.1f}",
            f"{res1['frente']:.1f} / {res1['detras']:.1f}",
            f"{res1['rotacion']:.2f}"
        ],
        'POST-AJUSTE': [
            f"{res2['izq']:.1f} / {res2['der']:.1f}",
            f"{res2['frente']:.1f} / {res2['detras']:.1f}",
            f"{res2['rotacion']:.2f}"
        ]
    }
    comparative_df = pd.DataFrame(metrics_data)
    print("\n--- Comparative Metrics ---")
    print(comparative_df.to_string(index=False))
