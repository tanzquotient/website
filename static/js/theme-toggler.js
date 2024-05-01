(() => {
    'use strict'

    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)

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
            themeIcon.className = (theme === 'dark') ? "fa-solid fa-circle-half-stroke" : (theme === 'auto' ? "fa-solid fa-sun fa-fw" : "fa-solid fa-moon fa-fw");
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

        const toggles = document.querySelectorAll('#theme-toggle')
        setTheme(getPreferredTheme())
        setThemeIcon(getPreferredTheme())

        toggles.forEach((toggle) => {
            toggle.addEventListener('click', () => {
                const current = getPreferredTheme();
                const theme = current === 'dark' ? 'auto' : (current === 'auto' ? 'light' : 'dark')
                setThemeIcon(theme)
                setStoredTheme(theme)
                setTheme(theme)
            })
        })
    })
})()