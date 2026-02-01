let selectedOperation = "";
let originalImage = null;

/* Select operation */
function selectOp(op) {
    selectedOperation = op;

    document.querySelectorAll(".operation-list div")
        .forEach(div => div.classList.remove("active"));

    event.target.classList.add("active");

    showCode(op);
}

/* Display OpenCV Code Snippet */
function showCode(op) {
    const codeBox = document.getElementById("codeSnippet");

    const codes = {
        grayscale: `gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)`,

        threshold: `gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret,th = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)`,

        adaptive: `gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
adp = cv2.adaptiveThreshold(gray,255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY,11,2)`,

        canny: `edges = cv2.Canny(img,100,200)`,

        contours: `gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
ret,th = cv2.threshold(gray,127,255,0)
contours,h = cv2.findContours(th,cv2.RETR_TREE,
    cv2.CHAIN_APPROX_SIMPLE)`,

        blur: `blur = cv2.GaussianBlur(img,(15,15),0)`,

        resize_up: `big = cv2.resize(img, None, fx=1.5, fy=1.5)`,

        resize_down: `small = cv2.resize(img, None, fx=0.5, fy=0.5)`,

        masking: `hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower_color, upper_color)
res = cv2.bitwise_and(img, img, mask=mask)`
    };

    codeBox.textContent = codes[op] || "No code";
}

/* Upload Image */
function uploadImage() {
    const file = document.getElementById("fileInput").files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.filename) {
            window.uploadedFilename = data.filename;
            document.getElementById("original").src = URL.createObjectURL(file);

            document.getElementById("statusBox").style.display = "block";
            document.getElementById("statusBox").innerText = "Image Uploaded!";
        }
    });
}


/* Process Image (Backend endpoint) */
function processImage() {
    if (!window.uploadedFilename) {
        alert("Upload an image first!");
        return;
    }

    fetch("/process", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            filename: window.uploadedFilename,
            operation: selectedOperation
        })
    })
    .then(res => res.blob())
    .then(blob => {
        const url = URL.createObjectURL(blob);

        // Only update the processed card
        document.getElementById("processed").src = url;

        // Status and download button
        const statusBox = document.getElementById("statusBox");
        statusBox.style.display = "block";
        statusBox.innerText = "Done! You can download the processed image.";

        document.getElementById("downloadBtn").style.display = "inline-block";

        // Store blob for download
        window.processedBlob = blob;

        // Close panel automatically
        document.getElementById("panel").classList.remove("open");
    });
}

function downloadImage() {
    const a = document.createElement("a");
    a.href = URL.createObjectURL(window.processedBlob);
    a.download = "processed_image.jpg";
    a.click();
}
