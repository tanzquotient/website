(() => {
    'use strict'

    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)
    const icon_classes = {auto: 'fa-circle-half-stroke', light: 'fa-sun', dark: 'fa-moon'}

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        if (storedTheme) {
            return storedTheme
        }

        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = theme => {
        if (theme === 'auto') {
            theme = (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
            document.documentElement.setAttribute('data-bs-theme', theme)
        } else {
            document.documentElement.setAttribute('data-bs-theme', theme)
        }
    }

    setTheme(getPreferredTheme())

    const setThemeIcon = theme => {
        document.querySelectorAll('#theme-icon').forEach((themeIcon) => {
            themeIcon.classList.remove(...Array.from(icon_classes))
            themeIcon.classList.add(icon_classes[theme])
        });
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const storedTheme = getStoredTheme()
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
            setTheme(getPreferredTheme())
            setThemeIcon(getPreferredTheme())
        }
    })

    window.addEventListener('DOMContentLoaded', () => {

        const toggles = document.querySelectorAll('.dropdown-item.color-theme-selector')
        setTheme(getPreferredTheme())
        setThemeIcon(getPreferredTheme())

        toggles.forEach((toggle) => {
            toggle.addEventListener('click', () => {
                const theme = toggle.getAttribute("data-bs-color-theme")
                setThemeIcon(theme)
                setStoredTheme(theme)
                setTheme(theme)
            })
        })
    })
})()