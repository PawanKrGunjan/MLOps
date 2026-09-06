/* =========================================================
HOME PAGE
Login Modal + Authentication
========================================================= */

"use strict";

/* =========================================================
ELEMENTS
========================================================= */

const loginModal =
document.getElementById("loginModal");

const loginForm =
document.getElementById("loginForm");

const loginUsername =
document.getElementById("loginUsername");

const loginPassword =
document.getElementById("loginPassword");

const loginError =
document.getElementById("loginError");

const loginButton =
document.getElementById("loginButton");

/* =========================================================
OPEN LOGIN MODAL
========================================================= */

function openLoginModal() {


if (!loginModal) {
    return;
}

loginModal.classList.add("active");

loginModal.setAttribute(
    "aria-hidden",
    "false"
);

document.body.classList.add(
    "login-modal-open"
);


/* Clear previous error */
if (loginError) {
    loginError.textContent = "";

    loginError.style.display = "none";
}


/* Focus username field */
if (loginUsername) {

    setTimeout(function () {

        loginUsername.focus();

    }, 100);

}


}

/* =========================================================
CLOSE LOGIN MODAL
========================================================= */

function closeLoginModal() {

if (!loginModal) {
    return;
}

loginModal.classList.remove("active");

loginModal.setAttribute(
    "aria-hidden",
    "true"
);

document.body.classList.remove(
    "login-modal-open"
);


/* Clear error */
if (loginError) {

    loginError.textContent = "";

    loginError.style.display = "none";

} 

}

/* =========================================================
LOGIN ERROR
========================================================= */

function showLoginError(message) {
 
if (!loginError) {
    return;
}

loginError.textContent =
    message || "Login failed.";

loginError.style.display =
    "block"; 

}

/* =========================================================
LOGIN FORM
========================================================= */

if (loginForm) {
 
loginForm.addEventListener(
    "submit",
    async function (event) {

        event.preventDefault();


        const username =
            loginUsername
                ? loginUsername.value.trim()
                : "";

        const password =
            loginPassword
                ? loginPassword.value
                : "";


        /*
         * Basic client-side validation.
         */
        if (!username || !password) {

            showLoginError(
                "Please enter username and password."
            );

            return;
        }


        /*
         * Clear previous error.
         */
        if (loginError) {

            loginError.textContent = "";

            loginError.style.display =
                "none";

        }


        /*
         * Disable login button.
         */
        if (loginButton) {

            loginButton.disabled = true;

            loginButton.textContent =
                "Signing in...";

        }


        try {

            /*
             * FastAPI Form(...) expects:
             *
             * application/x-www-form-urlencoded
             */
            const formData =
                new URLSearchParams();

            formData.append(
                "username",
                username
            );

            formData.append(
                "password",
                password
            );


            /*
             * IMPORTANT:
             *
             * Same-origin request.
             *
             * There is NO port 8001.
             */
            const response =
                await fetch(
                    "/login",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/x-www-form-urlencoded"
                        },

                        body: formData,

                        credentials:
                            "same-origin"
                    }
                );


            /*
             * Try to parse JSON.
             */
            let data;

            try {

                data =
                    await response.json();

            } catch (jsonError) {

                throw new Error(
                    "Invalid response from server."
                );

            }


            /*
             * Authentication failed.
             */
            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Invalid username or password."
                );

            }


            /*
             * Verify token exists.
             */
            if (!data.access_token) {

                throw new Error(
                    "Authentication succeeded but no access token was returned."
                );

            }


            /*
             * IMPORTANT:
             *
             * DO NOT LOG THE TOKEN.
             *
             * Redirect:
             *
             * http://127.0.0.1:8000/<JWT>
             */
            window.location.href =
                "/" +
                encodeURIComponent(
                    data.access_token
                );

        }


        catch (error) {

            showLoginError(
                error.message ||
                "Unable to login. Please try again."
            );

        }


        finally {

            if (loginButton) {

                loginButton.disabled =
                    false;

                loginButton.textContent =
                    "Sign In";

            }

        }

    }
); 

}

/* =========================================================
KEYBOARD HANDLING
========================================================= */

document.addEventListener(
"keydown",
function (event) {


    /*
     * ESC closes the modal.
     */
    if (
        event.key === "Escape" &&
        loginModal &&
        loginModal.classList.contains("active")
    ) {

        closeLoginModal();

    }

}


);

/* =========================================================
CLICK OUTSIDE MODAL
========================================================= */

if (loginModal) {


loginModal.addEventListener(
    "click",
    function (event) {

        /*
         * Only close when the actual overlay
         * is clicked.
         */
        if (
            event.target.classList.contains(
                "login-modal-overlay"
            )
        ) {

            closeLoginModal();

        }

    }
);


}
