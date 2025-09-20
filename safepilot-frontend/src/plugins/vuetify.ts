/**
 * Vuetify3 配置
 * 实现 SafePilot 专用深色主题
 */
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'



const dark_theme = {
        dark: true,
        colors: {
                primary: '#5B9BD5',
                secondary: '#8E9AAF',
                accent: '#7DD3FC',
                success: '#6EE7B7',
                warning: '#FDE68A',
                error: '#FCA5A5',
                info: '#93C5FD',
                surface: '#2A2D3A',
                background: '#1F2329',
                'on-background': '#E2E8F0',
                'on-surface': '#CBD5E0',
                'on-primary': '#FFFFFF',
        }
}

export default createVuetify({
        components,
        directives,
        icons: {
                defaultSet: 'mdi',
                aliases,
                sets: {
                        mdi,
                },
        },
        theme: {
                defaultTheme: 'dark',
                themes: {
                        dark: dark_theme,
                },
        },
        defaults: {
                VCard: {
                        elevation: 2,
                        rounded: 'lg',
                },
                VBtn: {
                        rounded: 'lg',
                        elevation: 1,
                },
                VTextField: {
                        rounded: 'lg',
                        variant: 'outlined',
                },
        },
})