async function processImage(file, action, parameters) {
    // Load the WASM module
    const wasmModule = await import('../pkg/bonemeal_bg.wasm');

    // Read the file and convert it to a byte array
    const reader = new FileReader();
    reader.readAsArrayBuffer(file);
    reader.onload = async () => {
        const arrayBuffer = reader.result;
        const bytes = new Uint8Array(arrayBuffer);

        async function processSelectedImage() {
            const fileInput = document.getElementById('imageInput');
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];

                // Example: Call the resize function
                await processImage(file, 'run-resize', {percentage: 50}); // Adjust parameters as needed
            }
        }
        try {
            let result;
            switch(action) {
                case 'run-resize':
                    result = await wasmModule.resize_image(bytes, parameters.percentage);
                    break;
                // Handle other actions like 'convert_to_indexed_color', 'compress_image'
            }

            // Handle the result - display or download
            // [...]
        } catch (error) {
            console.error('Error processing image:', error);
        }
    };
}
