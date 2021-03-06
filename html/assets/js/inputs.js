if (!document.querySelector("#no-break")) {
    const node = document.createElement("div");
    node.id = "no-break";
    document.body.appendChild(node);
}

window._get_wrapper = function() {
    // document.body.classList.add("no-scroll");

    const alertWrapper = document.createElement("div");
    alertWrapper.id = "prompt";

    const alertBox = document.createElement("div");
    alertBox.id = "prompt-inner";

    const buttonsBox = document.createElement("div");
    const cancelButton = document.createElement("button");
    const okButton = document.createElement("button");
    cancelButton.innerHTML = "Cancel";
    okButton.innerHTML = "OK";
    cancelButton.classList.add("red");
    cancelButton.classList.add("margin-right-m");
    okButton.classList.add("green");
    buttonsBox.classList.add("buttons");

    const header = document.createElement("p");
    header.classList.add("header");

    const content = document.createElement("span");
    content.classList.add("content");

    const customBox = document.createElement("div");
    customBox.classList.add("custom");

    alertBox.appendChild(header);
    alertBox.appendChild(content);
    alertBox.appendChild(customBox);
    buttonsBox.appendChild(cancelButton);
    buttonsBox.appendChild(okButton);
    alertBox.appendChild(buttonsBox);
    alertWrapper.appendChild(alertBox);
    return [alertWrapper, alertBox, customBox, buttonsBox, okButton, cancelButton, header, content];
}

window.rawWrapper = function(headerText, contentText) {
    const [alertWrapper, alertBox, customBox, buttonsBox, okButton, cancelButton, header, content] = window._get_wrapper();
    okButton.addEventListener("click", _ => _hide_wrapper(alertWrapper));
    cancelButton.addEventListener("click", _ => _hide_wrapper(alertWrapper));
    alertWrapper.addEventListener("click", ev => ev.target == alertWrapper ? _hide_wrapper(alertWrapper) : null);

    header.innerHTML = headerText;
    content.innerHTML = contentText;

    document.getElementById("no-break").appendChild(alertWrapper);

    return {
        content: customBox,
        ok: okButton,
        cancel: cancelButton,
        header: header,
        text: content,
        _wrapper: alertWrapper,
        _innerWrapper: alertBox,
        hide: () => { window._hide_wrapper(alertWrapper) }
    };
}

window._hide_wrapper = function(wrapperElement) {
    document.body.classList.remove("no-scroll");
    wrapperElement.classList.add("hidden");
    setTimeout(function() {
        wrapperElement.remove();
    }, 0.25 * 1000);
}

window.alertQueue = [];

function handleAlertQueue() {
    if (alertQueue.length > 0 && !document.getElementById("prompt")) {
        let alertObject = alertQueue.shift();
        try {
            window[alertObject.functionName](...alertObject.functionArguments);
        } catch (er) { console.log("error in handleAlertQueue", alertObject, er); }
    }
    setTimeout(handleAlertQueue, 500);
}
handleAlertQueue();

window.alert = function(headerText, descriptionText, customElement=null) {
    return new Promise(function(resolve, reject) {
        if (document.getElementById("prompt")) {
            alertQueue.push({
                functionName: "alert",
                functionArguments: [headerText, descriptionText, customElement]
            });
            reject(new Error("another alert is already shown, add to alertQueue"));
            return;
        }

        const [wrapper, box, customBox, buttonsBox, okButton, cancelButton, header, content] = _get_wrapper();
        document.getElementById("no-break").appendChild(wrapper);

        if (descriptionText) {
            header.innerHTML = headerText;
            content.innerHTML = descriptionText;
        } else {
            header.innerHTML = "Alert";
            content.innerHTML = headerText;
        }

        try {
            console.log(customElement, arguments);
            if (customElement)
                customBox.appendChild(customElement);
        } catch (er) { console.error(er); }
        
        okButton.addEventListener("click", ev => {
            resolve(true);
            _hide_wrapper(wrapper);
        });
        cancelButton.addEventListener("click", ev => {
            resolve(false);
            _hide_wrapper(wrapper);
        });
        wrapper.addEventListener("click", ev => {
            if (ev.target == wrapper) {
                resolve(false);
                _hide_wrapper(wrapper);
            }
        });
    });
}

window.prompt = function(headerText, descriptionText, placeholder, matcherFunction = undefined) {
    if (!placeholder) {
        placeholder = descriptionText;
        descriptionText = undefined;
    }
    if (!matcherFunction) {
        matcherFunction = () => true;
    }

    return new Promise(function(resolve, reject) {
        if (document.getElementById("prompt")) {
            reject(new Error("another alert is already shown"));
            return;
        }

        const [wrapper, box, customBox, buttonsBox, okButton, cancelButton, header, content] = _get_wrapper();
        customBox.classList.add("input");
        const input = document.createElement("input");
        input.placeholder = " ";
        const placeholderEl = document.createElement("span");
        placeholderEl.innerHTML = placeholder;

        customBox.appendChild(input);
        customBox.appendChild(placeholderEl);

        document.getElementById("no-break").appendChild(wrapper);

        header.innerHTML = headerText;
        content.innerHTML = descriptionText;

        input.focus();
        input.addEventListener("keyup", ev => {
            if (ev.key == "Enter" || ev.keyCode == 13) {
                if (input.value.trim() == "" || !matcherFunction(input.value.trim())) {
                    input.classList.add("transition");
                    input.classList.add("error");
                    setTimeout(function() {
                        input.classList.remove("error");
                    }, 700);
                } else {
                    resolve(input.value.trim());
                    _hide_wrapper(wrapper);
                }
            } else {
                if (input.value != "" && !matcherFunction(input.value.trim())) {
                    input.classList.add("border-red");
                } else {
                    input.classList.remove("border-red");
                }
            }
        });
        okButton.addEventListener("click", ev => {
            if (input.value.trim() == "" || !matcherFunction(input.value.trim())) {
                input.classList.add("transition");
                input.classList.add("error");
                setTimeout(function() {
                    input.classList.remove("error");
                }, 700);
            } else {
                resolve(input.value.trim());
                _hide_wrapper(wrapper);
            }
        });
        cancelButton.addEventListener("click", ev => {
            resolve(false);
            _hide_wrapper(wrapper);
        });
        wrapper.addEventListener("click", ev => {
            if (ev.target == wrapper) {
                resolve(false);
                _hide_wrapper(wrapper);
            }
        });
    });
}

window.longPrompt = function(headerText, descriptionText, inputPlaceholder, textAreaPlaceholder, inputMatcherFunction = undefined, textAreaMatcherFunction = undefined) {
    if (!inputMatcherFunction) {
        inputMatcherFunction = () => { return true };
    }
    if (!textAreaMatcherFunction) {
        textAreaMatcherFunction = () => { return true };
    }

    return new Promise(function(resolve, reject) {
        if (document.getElementById("prompt")) {
            reject(new Error("another alert is already shown"));
            return;
        }

        const [wrapper, box, customBox, buttonsBox, okButton, cancelButton, header, content] = _get_wrapper();
        
        const inputBox = document.createElement("div");
        inputBox.classList.add("input");
        const input = document.createElement("input");
        input.placeholder = " ";
        const placeholderEl = document.createElement("span");
        placeholderEl.innerHTML = inputPlaceholder;

        const textAreaBox = document.createElement("div");
        textAreaBox.classList.add("input");
        const textArea = document.createElement("textarea");
        textArea.placeholder = " ";
        textArea.classList.add("v-resize");
        const textAreaPlaceholderEl = document.createElement("span");
        textAreaPlaceholderEl.innerHTML = textAreaPlaceholder;

        inputBox.appendChild(input);
        inputBox.appendChild(placeholderEl);
        textAreaBox.appendChild(textArea);
        textAreaBox.appendChild(textAreaPlaceholderEl);

        customBox.appendChild(inputBox);
        customBox.appendChild(textAreaBox);

        document.getElementById("no-break").appendChild(wrapper);

        header.innerHTML = headerText;
        content.innerHTML = descriptionText;

        let tryToSubmit = function() {
            if (inputMatcherFunction(input.value.trim()) && textAreaMatcherFunction(textArea.value.trim())) {
                resolve({input: input.value.trim(), text: textArea.value.trim()});
                _hide_wrapper(wrapper);
            }
        }

        input.focus();
        input.addEventListener("keyup", ev => {
            if (ev.key == "Enter" || ev.keyCode == 13) {
                if (input.value.trim() == "" || !inputMatcherFunction(input.value.trim())) {
                    input.classList.add("transition");
                    input.classList.add("error");
                    setTimeout(function() {
                        input.classList.remove("error");
                    }, 700);
                } else {
                    textArea.focus();
                }
            } else {
                if (input.value != "" && !inputMatcherFunction(input.value.trim())) {
                    input.classList.add("border-red");
                } else {
                    input.classList.remove("border-red");
                }
            }
        });
        okButton.addEventListener("click", ev => {
            if (input.value.trim() == "" || !inputMatcherFunction(input.value.trim())) {
                input.classList.add("transition");
                input.classList.add("error");
                setTimeout(function() {
                    input.classList.remove("error");
                }, 700);
            } else {
                tryToSubmit();
            }
        });
        cancelButton.addEventListener("click", ev => {
            resolve(false);
            _hide_wrapper(wrapper);
        });
        wrapper.addEventListener("click", ev => {
            if (ev.target == wrapper) {
                resolve(false);
                _hide_wrapper(wrapper);
            }
        });
    });
}


window.dispatchEvent(new Event("alertOverride"));