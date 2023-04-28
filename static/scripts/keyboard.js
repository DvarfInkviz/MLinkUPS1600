const Keyboard = {
    elements: {
        main: null,
        keysContainer_en: null,
        keysContainer_ru: null,
        keys_en: [],
        keys_ru: []
    },

    eventHandlers: {
        oninput: null,
        onclose: null
    },

    properties: {
        value: "",
        capsLock: false,
        language: 'rus'
    },

    init() {
        // Create main elements
        this.elements.main = document.createElement("div");
        this.elements.keysContainer_en = document.createElement("div");
        this.elements.keysContainer_ru = document.createElement("div");

        // Setup main elements
        this.elements.main.classList.add("keyboard", "keyboard--hidden");
        this.elements.keysContainer_en.classList.add("keyboard__keys");
        this.elements.keysContainer_en.appendChild(this._createKeys('eng'));
        this.elements.keysContainer_en.setAttribute('id', 'kbd_eng');
        this.elements.keysContainer_ru.classList.add("keyboard__keys");
        this.elements.keysContainer_ru.appendChild(this._createKeys('rus'));
        this.elements.keysContainer_ru.setAttribute('id', 'kbd_rus');

        // Add to DOM
        this.elements.main.appendChild(this.elements.keysContainer_ru);
        this.elements.main.appendChild(this.elements.keysContainer_en);
        document.body.appendChild(this.elements.main);
        this.elements.keys_ru = this.elements.keysContainer_ru.querySelectorAll(".keyboard__key");
        this.elements.keys_en = this.elements.keysContainer_en.querySelectorAll(".keyboard__key");
        if (this.properties.language == 'rus') {
            document.getElementById("kbd_eng").classList.add("keyboard__keys--hidden");
            document.getElementById("kbd_rus").classList.remove("keyboard__keys--hidden");
        }
        else {
            document.getElementById("kbd_rus").classList.add("keyboard__keys--hidden");
            document.getElementById("kbd_eng").classList.remove("keyboard__keys--hidden");
        }

        // Automatically use keyboard for elements with .use-keyboard-input
        document.querySelectorAll(".use-keyboard-input").forEach(element => {
            element.addEventListener("focus", () => {
                this.open(element.value, currentValue => {
                    element.value = currentValue;
                });
            });
        });
    },

    _createKeys(language) {
        const fragment = document.createDocumentFragment();
        const keyLayout_en = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "backspace",
            "lang", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
            "caps", "a", "s", "d", "f", "g", "h", "j", "k", "l", "done",
            "z", "x", "c", "v", "b", "n", "m", ",", ".", "?", "space"
        ];
        const keyLayout_ru = [
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "backspace",
            "lang", "й", "ц", "у", "к", "е", "н", "г", "ш", "щ", "з", "х", "ъ",
            "caps", "ф", "ы", "в", "а", "п", "р", "о", "л", "д", "ж", "э", "done",
            "я", "ч", "с", "м", "и", "т", "ь", "б", "ю", ",", ".", "?", "space"
        ];

        if (language == 'rus') {keyLayout = keyLayout_ru;}
        else {keyLayout = keyLayout_en;}

        keyLayout.forEach(key => {
            const keyElement = document.createElement("button");
            const insertLineBreak = ["backspace", "p", "ъ", "done"].indexOf(key) !== -1;

            // Add attributes/classes
            keyElement.setAttribute("type", "button");
            keyElement.classList.add("keyboard__key");

            switch (key) {
                case "backspace":
                    keyElement.classList.add("keyboard__key--wide");
                    keyElement.innerHTML = '\u27F5';

                    keyElement.addEventListener("click", () => {
                        this.properties.value = this.properties.value.substring(0, this.properties.value.length - 1);
                        this._triggerEvent("oninput");
                    });

                    break;

                case "caps":
                    keyElement.classList.add("keyboard__key--wide", "keyboard__key--activatable", "caps_lock");
                    keyElement.innerHTML = '\u21E7';

                    keyElement.addEventListener("click", () => {
                        this._toggleCapsLock();
                        let elements = document.querySelectorAll('.caps_lock');
                        for (let elem of elements) {
                            elem.classList.toggle("keyboard__key--active", this.properties.capsLock);
                            console.log('1 - '+elem+' - '+this.properties.capsLock);
                        }
                    });

                    break;

                case "lang":
                    keyElement.classList.add("keyboard__key--wide");
                    keyElement.innerHTML = 'Eng/Рус';

                    keyElement.addEventListener("click", () => {
                    if (this.properties.language == 'rus') {
                        this.properties.language = 'eng';
                        document.getElementById("kbd_rus").classList.add("keyboard__keys--hidden");
                        document.getElementById("kbd_eng").classList.remove("keyboard__keys--hidden");
                    }
                    else {
                        this.properties.language = 'rus';
                        document.getElementById("kbd_eng").classList.add("keyboard__keys--hidden");
                        document.getElementById("kbd_rus").classList.remove("keyboard__keys--hidden");
                    }
                    });

                    break;

                case "space":
                    keyElement.classList.add("keyboard__key--wide");
                    keyElement.innerHTML = 'space';

                    keyElement.addEventListener("click", () => {
                        this.properties.value += " ";
                        this._triggerEvent("oninput");
                    });

                    break;

                case "done":
                    keyElement.classList.add("keyboard__key--wide", "keyboard__key--dark");
                    keyElement.innerHTML = '\u2713';

                    keyElement.addEventListener("click", () => {
                        this.close();
                        this._triggerEvent("onclose");
                    });

                    break;

                default:
                    keyElement.textContent = key.toLowerCase();

                    keyElement.addEventListener("click", () => {
                        this.properties.value += this.properties.capsLock ? key.toUpperCase() : key.toLowerCase();
                        this._triggerEvent("oninput");
                    });

                    break;
            }

            fragment.appendChild(keyElement);

            if (insertLineBreak) {
                fragment.appendChild(document.createElement("br"));
            }
        });

        return fragment;
    },

    _triggerEvent(handlerName) {
        if (typeof this.eventHandlers[handlerName] == "function") {
            this.eventHandlers[handlerName](this.properties.value);
        }
    },

    _toggleCapsLock() {
        this.properties.capsLock = !this.properties.capsLock;
        console.log('2 - '+this.properties.capsLock);
        for (const key of this.elements.keys_en) {
            if (key.childElementCount === 0) {
                key.textContent = this.properties.capsLock ? key.textContent.toUpperCase() : key.textContent.toLowerCase();
            }
        }
        for (const key of this.elements.keys_ru) {
            if (key.childElementCount === 0) {
                key.textContent = this.properties.capsLock ? key.textContent.toUpperCase() : key.textContent.toLowerCase();
            }
        }
    },

    open(initialValue, oninput, onclose) {
        this.properties.value = initialValue || "";
        this.eventHandlers.oninput = oninput;
        this.eventHandlers.onclose = onclose;
        this.elements.main.classList.remove("keyboard--hidden");
        if (this.properties.language == 'rus') {
            document.getElementById("kbd_eng").classList.add("keyboard__keys--hidden");
            document.getElementById("kbd_rus").classList.remove("keyboard__keys--hidden");
        }
        else {
            document.getElementById("kbd_rus").classList.add("keyboard__keys--hidden");
            document.getElementById("kbd_eng").classList.remove("keyboard__keys--hidden");
        }
    },

    close() {
        this.properties.value = "";
        this.eventHandlers.oninput = oninput;
        this.eventHandlers.onclose = onclose;
        this.elements.main.classList.add("keyboard--hidden");
    }
};

window.addEventListener("DOMContentLoaded", function () {
    Keyboard.init();
});