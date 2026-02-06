// src/config/mobile-typography.ts
// Mobile Experience V1.0 - Design Tokens: Typography
// Data: 01/02/2026

export const mobileTypography = {
  pageTitle: {
    fontSize: '34px',
    fontWeight: 700,
    lineHeight: 1.2,
    color: '#000000',
    tailwind: 'text-[34px] font-bold leading-tight text-black',
  },
  
  sectionTitle: {
    fontSize: '24px',
    fontWeight: 700,
    lineHeight: 1.25,
    color: '#000000',
    tailwind: 'text-2xl font-bold leading-snug text-black',
  },
  
  categoryName: {
    fontSize: '17px',
    fontWeight: 600,
    lineHeight: 1.3,
    color: '#000000',
    tailwind: 'text-[17px] font-semibold leading-snug text-black',
  },
  
  frequency: {
    fontSize: '13px',
    fontWeight: 400,
    lineHeight: 1.4,
    color: '#9CA3AF',
    tailwind: 'text-[13px] font-normal leading-relaxed text-gray-400',
  },
  
  amountPrimary: {
    fontSize: '17px',
    fontWeight: 600,
    lineHeight: 1.3,
    color: '#000000',
    tailwind: 'text-[17px] font-semibold leading-snug text-black',
  },
  
  amountSecondary: {
    fontSize: '13px',
    fontWeight: 400,
    lineHeight: 1.4,
    color: '#9CA3AF',
    tailwind: 'text-[13px] font-normal leading-relaxed text-gray-400',
  },
  
  buttonText: {
    fontSize: '15px',
    fontWeight: 600,
    lineHeight: 1.3,
    color: '#FFFFFF',
    tailwind: 'text-[15px] font-semibold leading-snug text-white',
  },
};

// Helper function: aplicar tipografia
export function getTypographyClass(variant: keyof typeof mobileTypography): string {
  return mobileTypography[variant].tailwind;
}
