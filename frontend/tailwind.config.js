/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary Forest Palette
        forest: {
          50: '#f0f4f2',
          100: '#e8f0ed',
          200: '#d1e0d9',
          300: '#a8c3b8',
          400: '#7fa597',
          500: '#44645c',
          600: '#315649',
          700: '#2a3f37',
          800: '#1f2e27',
          900: '#141d18',
          950: '#0a0f0c'
        },
        // Sunshine Accent
        sunshine: {
          50: '#fffef5',
          100: '#fffce8',
          200: '#fef9d1',
          300: '#fef3a3',
          400: '#fde047',
          500: '#fab21c',
          600: '#e09915',
          700: '#b97c11',
          800: '#925f0e',
          900: '#6b450a'
        },
        // Warm Neutrals
        cream: '#dedcce',
        ivory: '#fffce8',
        'warm-white': '#fdfbf7',
        // Supporting Colors
        sage: '#a8b5a0',
        terra: '#d4a574',
        mist: '#e8f0ed',
        shadow: '#2a3f37'
      },
      fontFamily: {
        'display': ['SF Pro Display', 'system-ui', '-apple-system', 'sans-serif'],
        'body': ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      fontSize: {
        'hero': 'clamp(2.5rem, 5vw, 4.5rem)',
        'display': 'clamp(2rem, 4vw, 3.5rem)',
        'title': 'clamp(1.5rem, 3vw, 2.5rem)',
        'subtitle': 'clamp(1.25rem, 2vw, 1.75rem)',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'fade-in-up': 'fadeInUp 0.6s ease-out',
        'fade-in-down': 'fadeInDown 0.6s ease-out',
        'scale-in': 'scaleIn 0.4s ease-out',
        'slide-in-right': 'slideInRight 0.5s ease-out',
        'slide-in-left': 'slideInLeft 0.5s ease-out',
        'bounce-soft': 'bounceSoft 2s ease-in-out infinite',
        'pulse-soft': 'pulseSoft 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s ease-in-out infinite',
        'breathe': 'breathe 4s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
        'gradient-shift': 'gradientShift 15s ease infinite',
        'wave': 'wave 2.5s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.9)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        slideInRight: {
          '0%': { transform: 'translateX(100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        slideInLeft: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.8' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px rgba(250, 178, 28, 0.5)' },
          '50%': { boxShadow: '0 0 40px rgba(250, 178, 28, 0.8)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        breathe: {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.05)' },
        },
        gradientShift: {
          '0%, 100%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
        },
        wave: {
          '0%': { transform: 'rotate(0deg)' },
          '10%': { transform: 'rotate(14deg)' },
          '20%': { transform: 'rotate(-8deg)' },
          '30%': { transform: 'rotate(14deg)' },
          '40%': { transform: 'rotate(-4deg)' },
          '50%': { transform: 'rotate(10deg)' },
          '60%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
        'shimmer-gradient': 'linear-gradient(105deg, transparent 40%, rgba(255, 255, 255, 0.7) 50%, transparent 60%)',
        'forest-gradient': 'linear-gradient(135deg, #44645c 0%, #315649 100%)',
        'sunshine-gradient': 'linear-gradient(135deg, #fab21c 0%, #e09915 100%)',
        'nature-gradient': 'linear-gradient(170deg, #44645c 0%, #315649 50%, #2a3f37 100%)',
      },
      boxShadow: {
        'soft': '0 2px 20px rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 30px rgba(0, 0, 0, 0.1)',
        'hard': '0 10px 40px rgba(0, 0, 0, 0.15)',
        'glow': '0 0 30px rgba(250, 178, 28, 0.4)',
        'inner-soft': 'inset 0 2px 10px rgba(0, 0, 0, 0.06)',
        'forest': '0 10px 40px rgba(68, 100, 92, 0.3)',
        'sunshine': '0 10px 40px rgba(250, 178, 28, 0.3)',
      },
      backdropBlur: {
        'xs': '2px',
        'sm': '4px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
        '3xl': '40px',
      },
      transitionDuration: {
        '400': '400ms',
        '600': '600ms',
        '800': '800ms',
        '900': '900ms',
        '1200': '1200ms',
        '1500': '1500ms',
        '2000': '2000ms',
      },
      transitionTimingFunction: {
        'bounce-in': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'smooth-out': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'smooth-in-out': 'cubic-bezier(0.645, 0.045, 0.355, 1)',
      },
      screens: {
        'xs': '475px',
        '3xl': '1920px',
      },
    },
  },
  plugins: [
    // Custom plugin for glass effect utilities
    function({ addUtilities }) {
      const newUtilities = {
        '.glass': {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        },
        '.glass-dark': {
          background: 'rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          border: '1px solid rgba(255, 255, 255, 0.1)',
        },
        '.glass-forest': {
          background: 'rgba(68, 100, 92, 0.1)',
          backdropFilter: 'blur(10px)',
          borderRadius: '16px',
          border: '1px solid rgba(68, 100, 92, 0.2)',
        },
        '.text-gradient': {
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundImage: 'linear-gradient(135deg, #44645c 0%, #fab21c 100%)',
        },
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
        '.animation-delay-200': {
          animationDelay: '200ms',
        },
        '.animation-delay-400': {
          animationDelay: '400ms',
        },
        '.animation-delay-600': {
          animationDelay: '600ms',
        },
        '.animation-delay-800': {
          animationDelay: '800ms',
        },
        '.animation-delay-1000': {
          animationDelay: '1000ms',
        },
      }
      addUtilities(newUtilities)
    }
  ],
}