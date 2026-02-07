#!/usr/bin/env python3
"""
Script de prueba para verificar barridos sin límite de puntos hasta 10000
Analiza configuraciones óptimas considerando tiempo y resolución
"""

import numpy as np

def test_sweep_segmentation(points, start=100, end=100000, scale='log'):
    """Prueba la lógica de segmentación de barridos"""
    
    MAX_POINTS_PER_SEGMENT = 255
    
    if points <= MAX_POINTS_PER_SEGMENT:
        segments = [(start, end, points)]
    else:
        num_segments = (points + MAX_POINTS_PER_SEGMENT - 1) // MAX_POINTS_PER_SEGMENT
        
        # Generar frecuencias
        if scale == 'log':
            all_freqs = np.logspace(np.log10(start), np.log10(end), points)
        else:
            all_freqs = np.linspace(start, end, points)
        
        # Dividir en segmentos
        segments = []
        for i in range(num_segments):
            seg_start_idx = i * MAX_POINTS_PER_SEGMENT
            seg_end_idx = min((i + 1) * MAX_POINTS_PER_SEGMENT, points)
            seg_points = seg_end_idx - seg_start_idx
            seg_start_freq = all_freqs[seg_start_idx]
            seg_end_freq = all_freqs[seg_end_idx - 1]
            segments.append((seg_start_freq, seg_end_freq, seg_points))
    
    # Verificar totales
    total_points = sum(seg[2] for seg in segments)
    return segments, total_points == points


def analyze_optimal_configurations():
    """Analiza configuraciones óptimas de puntos considerando tiempo y resolución"""
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE CONFIGURACIONES ÓPTIMAS (hasta 10000 puntos)")
    print("="*80)
    
    MAX_POINTS_PER_SEGMENT = 255
    TIME_PER_POINT = 3  # segundos aproximados por punto
    
    configurations = []
    
    test_points = [50, 100, 150, 200, 255, 300, 400, 500, 750, 1000, 
                   1500, 2000, 2500, 3000, 4000, 5000, 7500, 10000]
    
    for points in test_points:
        num_segments = max(1, (points + MAX_POINTS_PER_SEGMENT - 1) // MAX_POINTS_PER_SEGMENT)
        estimated_time = points * TIME_PER_POINT
        
        # Calcular puntos por década (asumiendo 3 décadas: 100Hz-100kHz)
        decades = 3
        points_per_decade = points / decades
        
        # Eficiencia: más puntos por segmento es mejor
        avg_points_per_seg = points / num_segments
        efficiency = avg_points_per_seg / MAX_POINTS_PER_SEGMENT * 100
        
        configurations.append({
            'points': points,
            'segments': num_segments,
            'time_min': estimated_time / 60,
            'time_sec': estimated_time,
            'ppd': points_per_decade,
            'efficiency': efficiency,
            'avg_per_seg': avg_points_per_seg
        })
    
    # Mostrar tabla completa
    print("\n{:<8} {:<5} {:<10} {:<10} {:<12} {:<10}".format(
        "Puntos", "Segs", "Tiempo", "Pts/década", "Pts/seg", "Efic%"))
    print("-" * 80)
    
    for cfg in configurations:
        print("{:<8} {:<5} {:<10} {:<10.0f} {:<12.1f} {:<10.1f}".format(
            cfg['points'],
            cfg['segments'],
            f"{cfg['time_min']:.1f} min",
            cfg['ppd'],
            cfg['avg_per_seg'],
            cfg['efficiency']
        ))
    
    # Análisis de categorías
    print("\n" + "="*80)
    print("🎯 RECOMENDACIONES POR CATEGORÍA")
    print("="*80)
    
    print("\n📌 RÁPIDAS (< 5 minutos) - Para pruebas rápidas y screening:")
    for cfg in configurations:
        if cfg['time_min'] < 5:
            print(f"   • {cfg['points']:4d} pts → {cfg['time_min']:4.1f} min, "
                  f"{cfg['ppd']:3.0f} pts/déc, {cfg['segments']:2d} seg, "
                  f"Efic: {cfg['efficiency']:5.1f}%")
    
    print("\n📌 EQUILIBRADAS (5-15 minutos) - Balance tiempo/resolución:")
    for cfg in configurations:
        if 5 <= cfg['time_min'] < 15:
            print(f"   • {cfg['points']:4d} pts → {cfg['time_min']:4.1f} min, "
                  f"{cfg['ppd']:3.0f} pts/déc, {cfg['segments']:2d} seg, "
                  f"Efic: {cfg['efficiency']:5.1f}%")
    
    print("\n📌 ALTA RESOLUCIÓN (15-30 minutos) - Análisis detallado:")
    for cfg in configurations:
        if 15 <= cfg['time_min'] < 30:
            print(f"   • {cfg['points']:4d} pts → {cfg['time_min']:4.1f} min, "
                  f"{cfg['ppd']:3.0f} pts/déc, {cfg['segments']:2d} seg, "
                  f"Efic: {cfg['efficiency']:5.1f}%")
    
    print("\n📌 MUY ALTA RESOLUCIÓN (> 30 minutos) - Publicación/Investigación:")
    for cfg in configurations:
        if cfg['time_min'] >= 30:
            print(f"   • {cfg['points']:4d} pts → {cfg['time_min']:4.1f} min, "
                  f"{cfg['ppd']:3.0f} pts/déc, {cfg['segments']:2d} seg, "
                  f"Efic: {cfg['efficiency']:5.1f}%")
    
    # Encontrar valores óptimos por eficiencia
    print("\n" + "="*80)
    print("⭐ VALORES ÓPTIMOS RECOMENDADOS")
    print("="*80)
    
    # Criterios de selección
    optimal_selections = {
        'Screening rápido': (100, "Balance entre rapidez y datos útiles"),
        'Caracterización estándar': (500, "Resolución adecuada para mayoría de casos"),
        'Análisis detallado': (1000, "Alta resolución sin tiempos excesivos"),
        'Publicación científica': (2000, "Muy alta resolución para figuras"),
        'Investigación detallada': (5000, "Máxima resolución para análisis profundo"),
        'Límite superior práctico': (10000, "Resolución extrema (50min, solo casos especiales)")
    }
    
    for category, (points, reason) in optimal_selections.items():
        cfg = next((c for c in configurations if c['points'] == points), None)
        if cfg:
            print(f"\n💡 {category}:")
            print(f"   → {cfg['points']} puntos")
            print(f"   → Tiempo: {cfg['time_min']:.1f} min ({cfg['time_sec']:.0f}s)")
            print(f"   → {cfg['ppd']:.0f} puntos/década")
            print(f"   → {cfg['segments']} segmentos de ~{cfg['avg_per_seg']:.0f} pts")
            print(f"   → Eficiencia: {cfg['efficiency']:.1f}%")
            print(f"   → Razón: {reason}")
    
    # Puntos con máxima eficiencia (múltiplos de 255)
    print("\n" + "="*80)
    print("🔥 PUNTOS DE MÁXIMA EFICIENCIA (100% - múltiplos exactos de 255)")
    print("="*80)
    
    for cfg in configurations:
        if cfg['efficiency'] == 100.0:
            print(f"   ⚡ {cfg['points']} pts = {cfg['segments']} seg × 255 pts/seg → {cfg['time_min']:.1f} min")
    
    return configurations


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 PRUEBAS EXTENDIDAS - BARRIDOS HASTA 10000 PUNTOS")
    print("="*80)
    
    # Casos de prueba clave
    test_cases = [
        (100, 100, 100000, 'log'),     # Rápido
        (255, 100, 100000, 'log'),     # Óptimo 1 segmento
        (500, 100, 100000, 'log'),     # Estándar
        (510, 100, 100000, 'log'),     # Óptimo 2 segmentos
        (1000, 100, 100000, 'log'),    # Alta resolución
        (2000, 100, 100000, 'log'),    # Muy alta
        (5000, 10, 1000000, 'log'),    # Máxima
        (10000, 10, 1000000, 'log'),   # Límite superior
    ]
    
    print("\n📋 VERIFICANDO SEGMENTACIÓN:")
    print("-" * 80)
    
    results = []
    for points, start, end, scale in test_cases:
        segments, success = test_sweep_segmentation(points, start, end, scale)
        status = "✅" if success else "❌"
        print(f"{status} {points:5d} pts → {len(segments):2d} segmentos")
        results.append((points, success))
    
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    print("\n" + "="*80)
    print(f"Resultado: {passed}/{total} pruebas exitosas")
    print("="*80)
    
    if passed == total:
        print("\n✅ TODAS LAS PRUEBAS PASARON\n")
        
        # Mostrar análisis de configuraciones óptimas
        analyze_optimal_configurations()
        
        print("\n" + "="*80)
        print("✨ ANÁLISIS COMPLETADO")
        print("="*80 + "\n")
        exit(0)
    else:
        print("\n❌ ALGUNAS PRUEBAS FALLARON\n")
        exit(1)
