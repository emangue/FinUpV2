'use client';

import { useMemo } from 'react';

interface DonutChartData {
  label: string;
  value: number;
  color: string;
  percentage: number;
}

interface DonutChartProps {
  data: DonutChartData[];
  centerText: {
    title: string;      // "$327.50"
    subtitle: string;   // "September 2026"
    caption: string;    // "saved out of $1000"
  };
  size?: number;        // Default: 250px
  strokeWidth?: number; // Default: 16px
  gapSize?: number;     // Default: 2px (em graus)
}

export function DonutChart({
  data,
  centerText,
  size = 250,
  strokeWidth = 16,
  gapSize = 2
}: DonutChartProps) {
  const radius = (size / 2) - (strokeWidth / 2);
  const circumference = 2 * Math.PI * radius;
  
  // Calcular segmentos com gaps
  const segments = useMemo(() => {
    let currentAngle = -90; // Começar no topo
    
    return data.map((item) => {
      const segmentAngle = (item.percentage / 100) * 360 - gapSize;
      const segmentLength = (segmentAngle / 360) * circumference;
      const gapLength = (gapSize / 360) * circumference;
      
      const dashArray = `${segmentLength} ${gapLength} ${circumference}`;
      const dashOffset = -(currentAngle / 360) * circumference;
      
      currentAngle += item.percentage / 100 * 360;
      
      return {
        ...item,
        dashArray,
        dashOffset
      };
    });
  }, [data, circumference, gapSize]);
  
  return (
    <div className="flex flex-col items-center gap-6">
      {/* Gráfico SVG */}
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="transform -rotate-90"
      >
        {/* Segmentos */}
        {segments.map((segment, index) => (
          <circle
            key={index}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={segment.color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={segment.dashArray}
            strokeDashoffset={segment.dashOffset}
            className="transition-all duration-500"
          />
        ))}
        
        {/* Texto central (usar foreignObject para melhor controle) */}
        <foreignObject
          x={strokeWidth}
          y={strokeWidth}
          width={size - (strokeWidth * 2)}
          height={size - (strokeWidth * 2)}
          className="transform rotate-90"
        >
          <div className="w-full h-full flex flex-col items-center justify-center text-center px-4">
            <p className="text-xs text-gray-500 mb-1 whitespace-nowrap">
              {centerText.subtitle}
            </p>
            <p className="text-2xl font-bold text-gray-900 mb-1 whitespace-nowrap">
              {centerText.title}
            </p>
            <p className="text-xs text-gray-500 whitespace-nowrap">
              {centerText.caption}
            </p>
          </div>
        </foreignObject>
      </svg>
    </div>
  );
}
