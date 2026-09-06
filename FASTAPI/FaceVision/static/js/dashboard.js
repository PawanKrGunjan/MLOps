/* =========================================================
   DASHBOARD.JS
   ========================================================= */


/*
 * TOKEN is injected by dashboard.html.
 *
 * dashboard.html must define:
 *
 * const TOKEN = "{{ token }}";
 *
 * before loading this script.
 */


/* =========================================================
   DOM ELEMENTS
========================================================= */

const camera =
    document.getElementById("cameraStream");

const cameraPlaceholder =
    document.getElementById("cameraPlaceholder");

const cameraStatus =
    document.getElementById("cameraStatus");

const startCameraButton =
    document.getElementById("startCameraButton");

const stopCameraButton =
    document.getElementById("stopCameraButton");

const imageInput =
    document.getElementById("imageInput");

const uploadBox =
    document.getElementById("uploadBox");

const selectedFile =
    document.getElementById("selectedFile");

const fileName =
    document.getElementById("fileName");

const fileSize =
    document.getElementById("fileSize");

const detectButton =
    document.getElementById("detectButton");

const detectButtonText =
    document.getElementById("detectButtonText");

const detectSpinner =
    document.getElementById("detectSpinner");

const saveResult =
    document.getElementById("saveResult");

const resultSection =
    document.getElementById("resultSection");

const resultImage =
    document.getElementById("resultImage");

const faceCount =
    document.getElementById("faceCount");

const resultUser =
    document.getElementById("resultUser");

const resultRole =
    document.getElementById("resultRole");

const resultFile =
    document.getElementById("resultFile");

const faceCoordinates =
    document.getElementById("faceCoordinates");

const errorMessage =
    document.getElementById("errorMessage");


/* =========================================================
   CAMERA
========================================================= */

function startCamera() {

    hideError();


    camera.src =
        "/" +
        TOKEN +
        "/video?t=" +
        Date.now();


    camera.style.display =
        "block";


    cameraPlaceholder.style.display =
        "none";


    cameraStatus.classList.add(
        "active"
    );


    cameraStatus.innerHTML =
        '<span class="dot"></span> Camera Running';


    startCameraButton.disabled =
        true;


    stopCameraButton.disabled =
        false;

}


function stopCamera() {

    camera.src = "";


    camera.style.display =
        "none";


    cameraPlaceholder.style.display =
        "flex";


    cameraStatus.classList.remove(
        "active"
    );


    cameraStatus.innerHTML =
        '<span class="dot"></span> Camera Stopped';


    startCameraButton.disabled =
        false;


    stopCameraButton.disabled =
        true;

}


/* =========================================================
   FILE SELECTION
========================================================= */

imageInput.addEventListener(
    "change",
    function () {

        if (
            !imageInput.files ||
            imageInput.files.length === 0
        ) {
            return;
        }


        const file =
            imageInput.files[0];


        const allowedTypes = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ];


        if (
            !allowedTypes.includes(
                file.type
            )
        ) {

            showError(
                "Unsupported image format. " +
                "Please select JPG, JPEG, PNG or WEBP."
            );


            removeSelectedFile();

            return;
        }


        fileName.textContent =
            file.name;


        fileSize.textContent =
            formatFileSize(file.size);


        uploadBox.style.display =
            "none";


        selectedFile.style.display =
            "flex";


        detectButton.disabled =
            false;


        hideError();

    }
);


/* =========================================================
   DRAG & DROP
========================================================= */

uploadBox.addEventListener(
    "dragover",
    function (event) {

        event.preventDefault();

        uploadBox.classList.add(
            "drag-over"
        );

    }
);


uploadBox.addEventListener(
    "dragleave",
    function () {

        uploadBox.classList.remove(
            "drag-over"
        );

    }
);


uploadBox.addEventListener(
    "drop",
    function (event) {

        event.preventDefault();


        uploadBox.classList.remove(
            "drag-over"
        );


        const files =
            event.dataTransfer.files;


        if (
            !files ||
            files.length === 0
        ) {
            return;
        }


        imageInput.files =
            files;


        imageInput.dispatchEvent(
            new Event("change")
        );

    }
);


/* =========================================================
   REMOVE FILE
========================================================= */

function removeSelectedFile() {

    imageInput.value = "";


    uploadBox.style.display =
        "flex";


    selectedFile.style.display =
        "none";


    detectButton.disabled =
        true;

}


/* =========================================================
   FILE SIZE
========================================================= */

function formatFileSize(bytes) {

    if (bytes === 0) {
        return "0 Bytes";
    }


    const units = [
        "Bytes",
        "KB",
        "MB",
        "GB"
    ];


    const index =
        Math.floor(
            Math.log(bytes) /
            Math.log(1024)
        );


    return (
        parseFloat(
            (
                bytes /
                Math.pow(
                    1024,
                    index
                )
            ).toFixed(2)
        ) +
        " " +
        units[index]
    );

}


/* =========================================================
   FACE DETECTION
========================================================= */

async function detectFaces() {

    if (
        !imageInput.files ||
        imageInput.files.length === 0
    ) {

        showError(
            "Please select an image first."
        );

        return;
    }


    hideError();


    const file =
        imageInput.files[0];


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    formData.append(
        "save_result",
        saveResult.checked
    );


    detectButton.disabled =
        true;


    detectButtonText.textContent =
        "Detecting...";


    detectSpinner.style.display =
        "inline-block";


    resultSection.style.display =
        "none";


    try {

        const response =
            await fetch(
                "/" +
                TOKEN +
                "/detect-faces/",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Face detection failed."
            );

        }


        displayDetectionResult(
            data
        );


    } catch (error) {

        showError(
            error.message ||
            "An unexpected error occurred."
        );


    } finally {

        detectButton.disabled =
            false;


        detectButtonText.textContent =
            "🔍 Detect Faces";


        detectSpinner.style.display =
            "none";

    }

}


/* =========================================================
   DISPLAY RESULT
========================================================= */

function displayDetectionResult(
    data
) {

    resultSection.style.display =
        "block";


    faceCount.textContent =
        data.num_faces ?? 0;


    resultUser.textContent =
        data.user ?? "-";


    resultRole.textContent =
        data.role ?? "-";


    const imagePath =
        data.image_path;


    if (imagePath) {

        const filename =
            imagePath
                .split("/")
                .pop();


        resultFile.textContent =
            filename;


        /*
         * Important:
         *
         * We do not expose LOCAL/detected
         * directly.
         *
         * Image is served through:
         *
         * /{token}/images/{filename}
         */

        resultImage.src =
            "/" +
            TOKEN +
            "/images/" +
            encodeURIComponent(
                filename
            ) +
            "?t=" +
            Date.now();

    } else {

        resultFile.textContent =
            "Not saved";


        resultImage.removeAttribute(
            "src"
        );

    }


    renderFaceCoordinates(
        data.faces || []
    );


    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });

}


/* =========================================================
   FACE COORDINATES
========================================================= */

function renderFaceCoordinates(
    faces
) {

    faceCoordinates.innerHTML =
        "";


    if (!faces.length) {

        faceCoordinates.innerHTML =
            `
            <div class="no-faces">
                No faces detected.
            </div>
            `;

        return;
    }


    faces.forEach(
        function (face, index) {

            const item =
                document.createElement(
                    "div"
                );


            item.className =
                "coordinate-item";


            item.innerHTML =
                `
                <span class="face-number">
                    Face ${index + 1}
                </span>

                <span>
                    X: <strong>${face.x}</strong>
                </span>

                <span>
                    Y: <strong>${face.y}</strong>
                </span>

                <span>
                    W: <strong>${face.w}</strong>
                </span>

                <span>
                    H: <strong>${face.h}</strong>
                </span>
                `;


            faceCoordinates.appendChild(
                item
            );

        }
    );

}


/* =========================================================
   ERROR
========================================================= */

function showError(message) {

    errorMessage.textContent =
        message;


    errorMessage.style.display =
        "block";


    errorMessage.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


function hideError() {

    errorMessage.style.display =
        "none";


    errorMessage.textContent =
        "";

}


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    stopCamera();

    window.location.href =
        "/";

}


/* =========================================================
   CLEANUP
========================================================= */

window.addEventListener(
    "beforeunload",
    function () {

        camera.src = "";

    }
);