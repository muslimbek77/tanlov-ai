// Zamonaviy animatsiya funksiyalari va Tailwind animation konfiglari
export const fadeIn = (delay: number = 0) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay, ease: 'easeOut' }
})

export const slideIn = (direction: 'left' | 'right' | 'up' | 'down' = 'up', delay: number = 0) => {
  const offset = { left: -20, right: 20, up: 20, down: -20 }
  return {
    initial: { opacity: 0, x: direction === 'left' || direction === 'right' ? offset[direction] : 0, y: direction === 'up' || direction === 'down' ? offset[direction] : 0 },
    animate: { opacity: 1, x: 0, y: 0 },
    transition: { duration: 0.6, delay, ease: 'easeOut' }
  }
}

export const staggerContainer = (staggerChildren: number = 0.1, delayChildren: number = 0) => ({
  animate: {
    transition: {
      staggerChildren,
      delayChildren
    }
  }
})

export const scaleIn = (delay: number = 0) => ({
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.4, delay, ease: 'easeOut' }
})

export const pulse = {
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
}

export const shimmer = {
  initial: { backgroundPosition: '1000px 0' },
  animate: { backgroundPosition: '-1000px 0' },
  transition: {
    duration: 1.5,
    repeat: Infinity,
    ease: 'linear'
  }
}

// Framer Motion variantlari
export const pageTransition = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
  transition: { duration: 0.3 }
}

export const cardHover = {
  whileHover: { 
    y: -4, 
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    transition: { duration: 0.2 }
  },
  whileTap: { scale: 0.98 }
}

export const buttonHover = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: { type: 'spring', stiffness: 400, damping: 17 }
}

// Tailwind animation uchun CSS classlar
export const animationClasses = {
  'gradient-bg': 'bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20',
  'glass-effect': 'bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg border border-white/20 dark:border-gray-700/20',
  'shimmer-bg': 'bg-gradient-to-r from-transparent via-gray-100 to-transparent dark:via-gray-800',
  'float-animation': 'animate-pulse',
  'slide-up': 'animate-slide-up',
  'fade-in': 'animate-fade-in'
} as const

// Custom CSS animatsiyalar uchun
export const customAnimations = `
@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes shimmer {
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}

.animate-slide-up {
  animation: slide-up 0.5s ease-out;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-shimmer {
  animation: shimmer 1.5s infinite linear;
  background-size: 1000px 100%;
}
`
