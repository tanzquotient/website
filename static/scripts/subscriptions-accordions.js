function expandAll() {
    const collapseElements = document.querySelectorAll('.accordion-subscrption-body.collapse')
    const collapseInstances = [...collapseElements].map(collapseElement => bootstrap.Collapse.getOrCreateInstance(collapseElement, { toggle: false }))
    collapseInstances.forEach(instance => {
        instance.show()
    })

}

function collapseAll() {
    const collapseElements = document.querySelectorAll('.accordion-subscrption-body.collapse')
    const collapseInstances = [...collapseElements].map(collapseElement => bootstrap.Collapse.getOrCreateInstance(collapseElement, { toggle: false }))
    collapseInstances.forEach(instance => {
        instance.hide()
    })

}