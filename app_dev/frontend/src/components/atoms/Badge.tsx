interface BadgeProps {
  color: string; // HEX color
  size?: number; // px
}

export function Badge({ color, size = 8 }: BadgeProps) {
  return (
    <div
      className="rounded-full"
      style={{
        width: size,
        height: size,
        backgroundColor: color
      }}
    />
  );
}
