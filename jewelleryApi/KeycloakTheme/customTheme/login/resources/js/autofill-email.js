window.onload = function () {
    function getQueryParam(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    }

    const email = getQueryParam('email');

    if (email) {
        console.log(email)
        const usernameInput = document.querySelector('#username');

        if (usernameInput) {
            usernameInput.value = email;
            usernameInput.dispatchEvent(new Event('input', { bubbles: true }));
        }
    }
};


