import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Hacker Terminal theme
        'hacker-bg': '#000000',
        'hacker-text': '#00ff00',
        'hacker-accent': '#00ff00',
        
        // Soft Serenity theme
        'serenity-bg': '#fff5f7',
        'serenity-text': '#4a4a4a',
        'serenity-accent': '#ffb3c1',
        
        // Deep Ocean theme
        'ocean-bg': '#0a1929',
        'ocean-text': '#ffffff',
        'ocean-accent': '#00bcd4',
      },
    },
  },
  plugins: [],
}
export default config
