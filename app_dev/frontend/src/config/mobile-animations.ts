// src/config/mobile-animations.ts
// Mobile Experience V1.0 - Design Tokens: Animations
// Data: 01/02/2026

export const mobileAnimations = {
  // Transitions (duração)
  transitions: {
    fast: {
      ms: 100,
      tailwind: 'transition-all duration-100',
      css: 'transition: all 100ms ease-in-out'
    },
    default: {
      ms: 150,
      tailwind: 'transition-all duration-150',
      css: 'transition: all 150ms ease-in-out'
    },
    slow: {
      ms: 300,
      tailwind: 'transition-all duration-300',
      css: 'transition: all 300ms ease-in-out'
    }
  },

  // Progress bars (smooth fill)
  progressBar: {
    duration: 300, // ms
    easing: 'ease-out',
    tailwind: 'transition-all duration-300 ease-out',
    css: 'transition: width 300ms ease-out'
  },

  // Cards (hover/active states)
  card: {
    hover: {
      duration: 100, // ms
      scale: 1.02,
      tailwind: 'transition-transform duration-100 hover:scale-[1.02]'
    },
    active: {
      duration: 100, // ms
      scale: 0.98,
      tailwind: 'transition-transform duration-100 active:scale-[0.98]'
    }
  },

  // Buttons (touch feedback)
  button: {
    duration: 150, // ms
    scale: 0.95,
    tailwind: 'transition-all duration-150 active:scale-95',
    css: 'transition: all 150ms ease-in-out'
  },

  // Bottom sheets (slide up)
  bottomSheet: {
    duration: 300, // ms
    easing: 'cubic-bezier(0.4, 0, 0.2, 1)', // Material Design easing
    tailwind: 'transition-transform duration-300',
    css: 'transition: transform 300ms cubic-bezier(0.4, 0, 0.2, 1)'
  },

  // Fade in/out
  fade: {
    in: {
      duration: 200, // ms
      tailwind: 'animate-in fade-in duration-200'
    },
    out: {
      duration: 150, // ms
      tailwind: 'animate-out fade-out duration-150'
    }
  },

  // Skeleton loading
  skeleton: {
    pulse: {
      tailwind: 'animate-pulse',
      css: 'animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite'
    }
  }
};

// Helper functions
export function getTransitionClass(speed: keyof typeof mobileAnimations.transitions = 'default'): string {
  return mobileAnimations.transitions[speed].tailwind;
}

export function getProgressBarTransition(): string {
  return mobileAnimations.progressBar.tailwind;
}

export function getButtonAnimation(): string {
  return mobileAnimations.button.tailwind;
}
