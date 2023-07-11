function createTooltips(tooltipList) {
    const popperInstances = []
    tooltipList.forEach((item,index) => {
        const createElement = document.createElement('div')
        createElement.innerText = item
        createElement.setAttribute('class', `popper-tooltip tooltip${index}`)
        document.body.appendChild(createElement)
        const createArrow = document.createElement('div')
        createArrow.setAttribute('class', 'arrow')
        createArrow.setAttribute('data-popper-arrow', '')
        createElement.appendChild(createArrow)
    });
    const buttonElement = document.querySelectorAll('.button-tooltip')
    buttonElement.forEach((buttonElement,index) => {
        const toolTipElement = document.querySelector(`.tooltip${index}`)
        const popperInstance = Popper.createPopper(buttonElement, toolTipElement, {
                                modifiers: ['preventOverflow', 'flip', {
                                  name: 'offset',
                                  options: {
                                    offset: [0, 8],
                                  },
                                }, ],
                            });
        popperInstances.push(popperInstance)
    });
    const showEvents = ['mouseenter', 'focus'];
    const hideEvents = ['mouseleave', 'blur'];

    showEvents.forEach((event) => {
        buttonElement.forEach((buttonElement,index) => {
            buttonElement.addEventListener(event, () => {
                // Make the tooltip visible
                const tooltip = document.querySelector(`.tooltip${index}`)
                tooltip.setAttribute('data-show', '');
                const popperInstance = popperInstances[index]
                //console.log(index, tooltip, popperInstance)
                // Enable the event listeners
                popperInstance.setOptions((options) => ({
                    ...options,
                    modifiers: [
                        ...options.modifiers,
                        { name: 'eventListeners', enabled: true },
                    ],
                }));

                // Update its position
                popperInstance.update();
            });
        })
    });

    hideEvents.forEach((event) => {
        buttonElement.forEach((buttonElement,index) => {
            buttonElement.addEventListener(event, () => {
                // Hide the tooltip
                const tooltip = document.querySelector(`.tooltip${index}`)
                tooltip.removeAttribute('data-show');
                const popperInstance = popperInstances[index]
                // Disable the event listeners
                popperInstance.setOptions((options) => ({
                    ...options,
                    modifiers: [
                        ...options.modifiers,
                        { name: 'eventListeners', enabled: false },
                    ],
                }));
            });
        })
    });
}
