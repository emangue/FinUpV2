interface ProgressBarProps {
  percentage: number; // 0-100
  color: string; // HEX color
  height?: number; // px (default: 12)
  percentageLabel?: number; // Percentual para exibir dentro da barra
}

export function ProgressBar({
  percentage,
  color,
  height = 12,
  percentageLabel
}: ProgressBarProps) {
  return (
    <div
      className="relative bg-gray-100 rounded-lg overflow-hidden"
      style={{ height }}
    >
      <div
        className="h-full rounded-lg transition-all duration-500 ease-out flex items-center justify-start px-3"
        style={{
          width: `${percentage}%`,
          backgroundColor: color
        }}
      >
        {percentageLabel !== undefined && (
          <span className="text-white text-xs font-semibold whitespace-nowrap">
            {percentageLabel}%
          </span>
        )}
      </div>
    </div>
  );
}
