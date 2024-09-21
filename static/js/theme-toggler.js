(() => {
    'use strict'

    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)
    const checkIcon = "<i class='bi bi-check-circle-fill ml-1' id='color-theme-selector-check'></i>"
    let color_selectors, theme_icons

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        return storedTheme ? storedTheme : window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
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
        const icon_classes = { auto: 'bi-circle-half', light: 'bi-sun-fill', dark: 'bi-moon-fill' }
        theme_icons.forEach((themeIcon) => {
            themeIcon.classList.remove(...Object.values(icon_classes))
            themeIcon.classList.add(icon_classes[theme])
        });
    }

    const setBold = theme =>
        color_selectors.forEach((color_selector) =>
            (color_selector.getAttribute("data-bs-color-theme") === theme) ? color_selector.classList.add("fw-bold") : color_selector.classList.remove("fw-bold")
        )

    const addTick = theme => {
        document.querySelectorAll('#color-theme-selector-check').forEach((color_theme_selector_check) => color_theme_selector_check.remove())
        color_selectors.forEach((color_selector) => 
            (color_selector.getAttribute("data-bs-color-theme") === theme) ? color_selector.insertAdjacentHTML('beforeend', checkIcon) : 0
    )}


    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const storedTheme = getStoredTheme()
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
            setTheme(getPreferredTheme())
            setThemeIcon(getPreferredTheme())
        }
    })

    window.addEventListener('DOMContentLoaded', () => {

        color_selectors = document.querySelectorAll('.dropdown-item.color-theme-selector')
        theme_icons = document.querySelectorAll('#theme-icon')
        const theme = getPreferredTheme()
        setTheme(theme)
        setThemeIcon(theme)
        setBold(theme)
        addTick(theme)

        color_selectors.forEach((color_selector) => {
            color_selector.addEventListener('click', () => {
                const theme = color_selector.getAttribute("data-bs-color-theme")
                setThemeIcon(theme)
                setBold(theme)
                setStoredTheme(theme)
                setTheme(theme)
                addTick(theme)
            })
        })
    })
})()