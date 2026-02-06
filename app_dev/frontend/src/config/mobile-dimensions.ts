// src/config/mobile-dimensions.ts
// Mobile Experience V1.0 - Design Tokens: Dimensions
// Data: 01/02/2026

export const mobileDimensions = {
  // Spacing
  spacing: {
    screenHorizontal: { px: 20, rem: 1.25, tailwind: 'px-5' },
    cardGap: { px: 16, rem: 1, tailwind: 'gap-4' },
    cardPadding: { px: 16, rem: 1, tailwind: 'p-4' },
    iconTextGap: { px: 12, rem: 0.75, tailwind: 'gap-3' },
  },
  
  // Sizes
  sizes: {
    iconCircle: { px: 48, rem: 3, tailwind: 'w-12 h-12' },
    iconSize: { px: 24, rem: 1.5, tailwind: 'w-6 h-6' },
    progressHeight: { px: 6, rem: 0.375, tailwind: 'h-[6px]' },
    cardMinHeight: { px: 72, rem: 4.5, tailwind: 'min-h-[72px]' },
    navButtonSize: { px: 48, rem: 3, tailwind: 'w-12 h-12' },
    touchTargetMinimum: { px: 44, rem: 2.75, tailwind: 'w-11 h-11' }, // WCAG 2.5.5
  },
  
  // Border Radius
  borderRadius: {
    card: { px: 16, rem: 1, tailwind: 'rounded-2xl' },
    icon: { px: 9999, rem: 9999, tailwind: 'rounded-full' },
    progress: { px: 3, rem: 0.1875, tailwind: 'rounded-[3px]' },
  },
  
  // Shadow
  shadows: {
    card: '0px 1px 3px rgba(0, 0, 0, 0.04), 0px 1px 2px rgba(0, 0, 0, 0.02)',
  },
  
  // Breakpoints
  breakpoints: {
    mobile: 768,  // < 768px = mobile
    tablet: 1024, // 768-1024px = tablet
    desktop: 1440, // > 1024px = desktop
  },
};

// Helper function: responsive padding
export function getResponsivePadding(screen: 'mobile' | 'tablet' | 'desktop'): string {
  const map = {
    mobile: mobileDimensions.spacing.screenHorizontal.tailwind,
    tablet: 'px-8',
    desktop: 'px-12',
  };
  return map[screen];
}
