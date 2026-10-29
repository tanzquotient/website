(() => {
    'use strict'

    const resetTimeouts = new WeakMap()

    document.addEventListener('click', event => {
        const button = event.target.closest('[data-copy-link]')
        if (!button) {
            return
        }

        const url = new URL(button.dataset.copyLink, window.location.href).href
        // The clipboard API is only available in secure contexts (HTTPS or localhost)
        if (!navigator.clipboard) {
            window.prompt('Copy this link:', url)
            return
        }

        button.dataset.label ??= button.textContent
        navigator.clipboard.writeText(url).then(
            () => {
                button.textContent = 'Copied!'
                clearTimeout(resetTimeouts.get(button))
                resetTimeouts.set(button, setTimeout(() => {
                    button.textContent = button.dataset.label
                }, 2000))
            },
            () => window.prompt('Copy this link:', url),
        )
    })
})()
