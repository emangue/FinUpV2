interface ProgressBarProps {
  percentage: number;
  color?: string;
  height?: string;
}

export default function ProgressBar({ percentage, color = 'bg-blue-500', height = 'h-2' }: ProgressBarProps) {
  return (
    <div className={`w-full ${height} bg-gray-200 rounded-full overflow-hidden`}>
      <div 
        className={`${height} ${color} rounded-full transition-all duration-500`}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  );
}
