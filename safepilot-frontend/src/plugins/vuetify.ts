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
                // 根据新配色方案设计的主题
                primary: '#E7D1BB',      // --primary-100: 主要强调色
                'primary-darken-1': '#c8b39e', // --primary-200: 主要色深色变体
                'primary-darken-2': '#84725e', // --primary-300: 主要色最深变体
                secondary: '#8E9AAF',     // 保持原有的辅助色
                accent: '#A096A5',        // --accent-100: 强调色
                'accent-darken-1': '#463e4b', // --accent-200: 强调色深色变体
                success: '#6EE7B7',       // 保持成功色
                warning: '#FDE68A',       // 保持警告色
                error: '#FCA5A5',         // 保持错误色
                info: '#93C5FD',          // 保持信息色
                surface: '#252841',       // --bg-200: 表面色
                'surface-variant': '#3d3f5b', // --bg-300: 表面变体色
                background: '#151931',    // --bg-100: 背景色
                'on-background': '#A096A2', // --text-100: 背景上的文字
                'on-surface': '#847a86',  // --text-200: 表面上的文字
                'on-primary': '#151931',  // 主要色上的文字（使用深色背景）
                'on-accent': '#151931',   // 强调色上的文字
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