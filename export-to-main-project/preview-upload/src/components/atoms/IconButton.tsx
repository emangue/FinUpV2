interface IconButtonProps {
  icon: 'edit' | 'close' | 'expand';
  onClick?: () => void;
  className?: string;
  ariaLabel?: string;
}

export default function IconButton({ icon, onClick, className = '', ariaLabel }: IconButtonProps) {
  const icons = {
    edit: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
      />
    ),
    close: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M6 18L18 6M6 6l12 12"
      />
    ),
    expand: (
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M9 5l7 7-7 7"
      />
    ),
  };

  return (
    <button
      onClick={onClick}
      aria-label={ariaLabel}
      className={`text-gray-400 hover:text-gray-600 transition-colors ${className}`}
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        {icons[icon]}
      </svg>
    </button>
  );
}
