function expandAll() {
    const collapseElements = document.querySelectorAll('.accordion-subscription-body.collapse')
    const collapseInstances = [...collapseElements].map(collapseElement => bootstrap.Collapse.getOrCreateInstance(collapseElement, {toggle: false}))
    collapseInstances.forEach(instance => {
        instance.show()
    })

}

function collapseAll() {
    const collapseElements = document.querySelectorAll('.accordion-subscription-body.collapse')
    const collapseInstances = [...collapseElements].map(collapseElement => bootstrap.Collapse.getOrCreateInstance(collapseElement, {toggle: false}))
    collapseInstances.forEach(instance => {
        instance.hide()
    })
}