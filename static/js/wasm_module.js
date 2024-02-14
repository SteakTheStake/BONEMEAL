// The path to your WebAssembly `.wasm` file
const wasmModuleUrl = '/pkg/bonemeal_bg.wasm';

// Function to read an image file and convert it to a Uint8Array
function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(new Uint8Array(reader.result));
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

// Function to handle file input and process images
function handleFileInput(file, resizePercentage, compressionPercentage) {
    readFileAsArrayBuffer(file)
        .then(imageData => {
            // Resize the image using the WASM module
            const resizedImage = resizeWasmImage(imageData, resizePercentage);

            // Optionally, convert the resized image to indexed color
            const indexedColorImage = convertImageToIndexedColor(resizedImage);

            // Optionally, compress the image
            const compressedImage = compressWasmImage(indexedColorImage, compressionPercentage);

            // Handle the final image data (e.g., display it or send it back to the server)
            displayImage(compressedImage);
        })
        .catch(console.error);
}

// Function to display image data
function displayImage(imageData) {
    const blob = new Blob([imageData], { type: 'image/png' });
    const url = URL.createObjectURL(blob);

    const img = document.createElement('img');
    img.src = url;
    document.body.appendChild(img);

    // Remember to revoke the URL to avoid memory leaks
    img.onload = () => URL.revokeObjectURL(url);
}

// Fetch and instantiate the WebAssembly module
fetch(wasmModuleUrl)
    .then(response => response.arrayBuffer())
    .then(bytes => WebAssembly.instantiate(bytes))
    .then(results => {
        // `results.instance` contains the instantiated WebAssembly module
        const { resize_image, convert_to_indexed_color, compress_image } = results.instance.exports;

        // Define the WASM image manipulation functions
        window.resizeWasmImage = (imageData, resizePercentage) => {
            return resize_image(imageData, resizePercentage);
        }

        window.convertImageToIndexedColor = (imageData) => {
            return convert_to_indexed_color(imageData);
        }

        window.compressWasmImage = (imageData, compressionPercentage) => {
            return compress_image(imageData, compressionPercentage);
        }
    })
    .catch(console.error);
