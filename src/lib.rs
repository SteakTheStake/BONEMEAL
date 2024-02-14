pub fn add(left: usize, right: usize) -> usize {
    left + right
}

use image::{ImageFormat, ImageOutputFormat, GenericImageView, ImageEncoder};
use wasm_bindgen::prelude::*;
use std::io::Cursor;

#[wasm_bindgen]
pub fn resize_image(data: &[u8], percentage: u32) -> Result<Vec<u8>, JsValue> {
    let img = image::load_from_memory(data).map_err(|e| e.to_string())?;

    // Determine the image format
    let image_format = image::guess_format(data).map_err(|e| e.to_string())?;

    // Calculate new dimensions
    let (width, height) = img.dimensions();
    let new_width = (width as f32 * (percentage as f32 / 100.0)) as u32;
    let new_height = (height as f32 * (percentage as f32 / 100.0)) as u32;

    // Resize the image
    let resized_img = img.resize_exact(new_width, new_height, image::imageops::FilterType::Nearest);

    // Save the resized image to a vector, keeping the original format
    let mut result = Vec::new();
    match image_format {
        ImageFormat::Png => {
            // For PNG, create a new PngEncoder
            let encoder = image::codecs::png::PngEncoder::new(&mut result);
            // Write the image data using the write_image method
            encoder.write_image(
                resized_img.as_bytes(),
                new_width,
                new_height,
                image::ColorType::Rgba16 // Or use the color type of the original image
            ).map_err(|e| e.to_string())?;
        },
        // Handle other formats as necessary
        // Example for JPEG
        ImageFormat::Jpeg => {
            // For JPEG, create a new JpegEncoder
            let encoder = image::codecs::jpeg::JpegEncoder::new_with_quality(&mut result, 75); // Set the quality to 75
            // Write the image data using the write_image method
            encoder.write_image(
                resized_img.as_bytes(),
                new_width,
                new_height,
                image::ColorType::Rgb16 // Use appropriate color type
            ).map_err(|e| e.to_string())?;
        },
        // Add other formats as needed
        _ => {
            // If the format is not recognized or supported, default to PNG
            let encoder = image::codecs::png::PngEncoder::new(&mut result);
            encoder.write_image(
                resized_img.as_bytes(),
                new_width,
                new_height,
                image::ColorType::Rgba16
            ).map_err(|e| e.to_string())?;
        }
    }

    Ok(result)
}




// Function to convert an image to indexed color
#[wasm_bindgen]
pub fn convert_to_indexed_color(data: &[u8]) -> Result<Vec<u8>, JsValue> {
    let img = image::load_from_memory(data).map_err(|e| e.to_string())?;

    // Convert to 8-bit color format (this is not true indexed color, but for the sake of example)
    let img = img.into_luma8();

    // Save the "converted" image to a vector
    let mut result = Cursor::new(Vec::new());
    // Since we're defaulting to PNG, use the PNG encoder
    let encoder = image::codecs::png::PngEncoder::new(&mut result);
    encoder.write_image(&img, img.width(), img.height(), image::ColorType::L8)
        .map_err(|e| e.to_string())?;

    Ok(result.into_inner())
}


// Function to compress an image
#[wasm_bindgen]
pub fn compress_image(data: &[u8], compression_percentage: u8) -> Result<Vec<u8>, JsValue> {
    // Load the image from bytes
    let img = image::load_from_memory(data).map_err(|e| e.to_string())?;

    // Determine the image format
    let image_format = image::guess_format(data).map_err(|e| e.to_string())?;

    // Create a Vec<u8> to hold the output data
    let mut output_data = Vec::new();

    // Wrap the output_data in a Cursor to get a writer that implements `Write` and `Seek`
    {
        let mut cursor = Cursor::new(&mut output_data);

        match image_format {
            ImageFormat::Png => {
                // Encode as PNG with default options (consider any compression settings if available)
                let encoder = image::codecs::png::PngEncoder::new(&mut cursor);
                encoder.write_image(img.as_bytes(), img.width(), img.height(), img.color())
                    .map_err(|e| e.to_string())?;
            },
            ImageFormat::Jpeg => {
                // Encode as JPEG, adjusting the quality setting
                let quality = u8::max(1, compression_percentage);
                let encoder = image::codecs::jpeg::JpegEncoder::new_with_quality(&mut cursor, quality);
                encoder.write_image(img.as_bytes(), img.width(), img.height(), img.color())
                    .map_err(|e| e.to_string())?;
            },
            // Add cases for other formats if needed
            _ => {
                // For other formats or if you want to use default encoding for unsupported formats
                img.write_to(&mut cursor, ImageOutputFormat::Png).map_err(|e| e.to_string())?;
            }
        }
    } // Cursor goes out of scope here, releasing the borrow on `output_data`

    // `output_data` is now filled with the encoded image data
    Ok(output_data)
}
