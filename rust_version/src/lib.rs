//! # String Art Generator
//!
//! This module generates a string art pattern based on the brightness of pixels in a grayscale image.
//! The output is saved as a sequence of connections in a CSV file.
//!
//! ## Overview
//! The program processes a grayscale image to compute string connections that form a "string art"
//! design. Hooks are evenly spaced along a circular boundary, and strings connect these hooks based
//! on image brightness along their paths.
//!
//! ### Program Arguments
//! 1. **`input_image`**: Path to the input image file (e.g., PNG or JPG).
//! 2. **`output_csv`**: Path to the output CSV file where the string connections will be stored.
//! 3. **`hooks`**: Number of hooks (points) along the circle (default: 201).
//! 4. **`strings`**: Number of strings to compute (default: 5000).
//! 5. **`contrast_multiplier`**: Factor to adjust string brightness (default: 0.3).
//! 6. **`neighbour_dist`**: Minimum distance between two hooks (default: 15).
//!
//! ## Functions
//! - **`Config`**: Handles program configuration and argument parsing.
//! - **`compute_string_order`**: Core function to generate the string pattern based on input settings.
//!
//! ## Output
//! The output CSV contains the string connections in the following format:
//! ```csv
//! index, from, to
//! 0, 1, 42
//! 1, 42, 7
//! ...
//! ```
//!
//! ## Example Usage
//! ```rust
//! use knit_portrait::{compute_string_order, Config};
//!
//! let config = Config {
//!     filename: "tommy.jpg".to_string(),
//!     output: "tommy.csv".to_string(),
//!     hooks: 201,
//!     strings: 5000,
//!     contrast_change: 0.3,
//!     neighbour_dist: 15,
//! };
//!
//! let _ = compute_string_order(&config);
//! ```
//!
//! ## Display Results
//! The easiest would be to display results using **Python**:
//!
//! ```python
//! import numpy as np
//! import matplotlib.pyplot as plt
//!
//! num_hooks = 201  # must be equal to what has been set before
//! num_display_strings = 3000  # smaller or equal to the strings computed
//!
//! # Compute circle coordinates
//! theta = np.linspace(0, 2 * np.pi, num_hooks)
//! circle = np.asarray([np.cos(theta), np.sin(theta)]).T
//!
//! # load data
//! data = np.genfromtxt('tommy.csv', delimiter=',', dtype=int)
//!
//! # Use data to index circle coordinates
//! for (_, d_from, d_to) in data[:num_display_strings]:
//!     plt.plot([circle[d_from, 0], circle[d_to, 0]],
//!              [circle[d_from, 1], circle[d_to, 1]], color="k", linewidth=0.1)
//!
//! # Cosmetics
//! plt.axis('equal')
//! plt.axis('off')
//! plt.tight_layout()
//! plt.gca().invert_yaxis()
//! plt.show()
//! ```

use csv::Writer;
use image::{GrayImage, Luma};
use serde::ser::Serialize;
use std::error::Error;
use std::f64::consts::PI;

/// Configuration structure for stringing algorithm
///
/// Fields:
/// - **filename**: The image file.
/// - **output**: The file to write the output to.
/// - **hooks**: Number of hooks used for stringing.
/// - **strings**: Number of strings to compute.
/// - **contrast_change**: Discount factor to change contrast after drawing
///   string.
/// - **neighbour_dist**: Minimum distance between two hooks to be considered a
///   valid line.
pub struct Config {
    /// The file path to the input image
    pub filename: String,

    /// The file path to the output csv
    pub output: String,

    /// The number of hooks
    pub hooks: usize,

    /// The number of strings to compute
    pub strings: usize,

    /// Contrast change
    pub contrast_change: f64,

    pub neighbour_dist: usize,
}

impl Config {
    pub fn build(mut args: impl Iterator<Item = String>) -> Result<Config, &'static str> {
        args.next();

        // get filename string from command line arguments
        let filename = match args.next() {
            Some(arg) => arg,
            None => return Err("Didn't get a filename."),
        };

        let output = match args.next() {
            Some(arg) => arg,
            None => return Err("Output file not writable."),
        };

        // get configs from command line arguments or set defaults
        let hooks = args
            .next()
            .unwrap_or_else(|| "201".parse().unwrap())
            .parse::<usize>()
            .unwrap();

        let strings = args
            .next()
            .unwrap_or_else(|| "5000".parse().unwrap())
            .parse::<usize>()
            .unwrap();

        let contrast_change = args
            .next()
            .unwrap_or_else(|| "0.3".parse().unwrap())
            .parse::<f64>()
            .unwrap();

        let neighbour_dist = args
            .next()
            .unwrap_or_else(|| "15".parse().unwrap())
            .parse::<usize>()
            .unwrap();

        println!(
            "Used settings:\nFile: {filename}\nNumber of Hooks: {hooks}\n\
        Number of Strings: {strings}\nContrast change: {contrast_change}\n\
        Minimum hook distance: {neighbour_dist}"
        );

        // output
        Ok(Config {
            filename,
            output,
            hooks,
            strings,
            contrast_change,
            neighbour_dist,
        })
    }
}

pub fn data2csv<T: Serialize>(filename: &str, data: Vec<T>) -> Result<Vec<T>, Box<dyn Error>> {
    let mut writer = Writer::from_path(filename)?;

    for item in &data {
        writer.serialize(item)?;
    }

    writer.flush()?;
    Ok(data)
}
/// Function to compute the string order
///
/// Takes [`Config`] as input.
pub fn compute_string_order(config: &Config) -> Result<Vec<(i32, i32, i32)>, Box<dyn Error>> {
    let filename = &config.filename;
    let hooks = config.hooks;
    let strings = config.strings;
    let contrast_change = config.contrast_change;

    let mut gray = image::open(filename).unwrap().to_luma8();
    flip_gray_image(&mut gray);

    let width = gray.width() as i32;
    let height = gray.height() as i32;
    let coords = generate_circle_coordinates(width, height, hooks);

    let mut start: (i32, i32, usize) = coords[0];

    let result: Vec<(i32, i32, i32)> = (0..=strings)
        .map(|_| {
            let other: Vec<(i32, i32, usize)> = coords
                .clone()
                .into_iter()
                .filter(|c| c != &start && c.2.abs_diff(start.2) > config.neighbour_dist)
                .collect();

            // Extract coordinates
            let other_coords = other.iter().map(|v| (v.0, v.1)).collect();

            // Compute all combinations of possible values
            let res = compute_line_vals(&gray, (start.0, start.1), other_coords);

            // Get line with the lowest brightness (i.e. "best" line)
            let new_start = other[find_max_index(&res)];

            // Compute pixel indices of "best" line
            let line = bresenham_line((start.0, start.1), (new_start.0, new_start.1));

            // Make "best" line brighter
            scale_pixels(&mut gray, line, contrast_change);
            start = new_start;
            start
        })
        .collect::<Vec<_>>()
        // prepare output vector
        .windows(2)
        .enumerate()
        .map(|(i, window)| (i as i32, window[0].2 as i32, window[1].2 as i32))
        .collect();

    data2csv(&config.output, result)
}
#[inline]
fn scale_pixels<I>(img: &mut GrayImage, coords: I, multiplier: f64)
where
    I: Iterator<Item = (i32, i32)>,
{
    // Iterate over coordinates and modify the pixels
    for (x, y) in coords {
        // Make sure the coordinates are within bounds
        if x >= 0 && y >= 0 && x < img.width() as i32 && y < img.height() as i32 {
            // Get the current pixel value
            let pixel = img.get_pixel(x as u32, y as u32);
            let current_value = pixel[0] as f64;

            // Multiply by the multiplier, clip to 255, and convert to int
            let new_value = (current_value * multiplier).round() as u8;

            // Set the new pixel value
            img.put_pixel(x as u32, y as u32, Luma([new_value]));
        }
    }
}

#[inline]
fn generate_circle_coordinates(
    image_width: i32,
    image_height: i32,
    n: usize,
) -> Vec<(i32, i32, usize)> {
    let cx = image_width as f64 / 2.0; // X center of the image
    let cy = image_height as f64 / 2.0; // Y center of the image

    let radius = cx.min(cy) - 1.0;

    (0..n)
        .map(|i| {
            let angle = 2.0 * PI * i as f64 / n as f64;
            // Calculate the (x, y) coordinates
            let x = (cx + radius * angle.cos()).round() as i32;
            let y = (cy + radius * angle.sin()).round() as i32;
            (x, y, i)
        })
        .collect()
}

#[inline]
fn compute_line_vals(
    img: &GrayImage,
    start: (i32, i32),
    edges: Vec<(i32, i32)>,
) -> Vec<((i32, i32), f64)> {
    edges
        .iter()
        .filter_map(move |&end| {
            let avg = line_average(&img, start, end);
            Some((end, avg))
        })
        .collect()
}
#[inline]
fn find_max_index(line_data: &Vec<((i32, i32), f64)>) -> usize {
    line_data
        .iter()
        .enumerate()
        .max_by(|(_, a), (_, b)| a.1.partial_cmp(&b.1).unwrap_or(std::cmp::Ordering::Equal))
        .map(|(index, _)| index)
        .unwrap()
}
#[inline]
fn line_average(img: &GrayImage, start: (i32, i32), end: (i32, i32)) -> f64 {
    let mut count = 0.0;
    bresenham_line(start, end)
        .map(|(x, y)| {
            count += 1.0;
            img.get_pixel(x as u32, y as u32).0[0] as f64
        })
        .sum::<f64>()
        / count
}
#[inline]
fn bresenham_line(start: (i32, i32), end: (i32, i32)) -> impl Iterator<Item = (i32, i32)> {
    // Extract coordinates
    let (x0, y0) = start;
    let (x1, y1) = end;

    // Calculate deltas and steps
    let dx = (x1 - x0).abs();
    let dy = (y1 - y0).abs();
    let sx = if x0 < x1 { 1 } else { -1 };
    let sy = if y0 < y1 { 1 } else { -1 };

    // Initialize state for the iterator
    let mut x = x0;
    let mut y = y0;
    let mut error = dx - dy;
    let mut done = false;

    std::iter::from_fn(move || {
        if done {
            return None;
        }

        // Store current point
        let current = (x, y);

        // Check if we've reached the end point
        if x == x1 && y == y1 {
            done = true;
            return Some(current);
        }

        // Calculate next position
        let error2 = 2 * error;

        if error2 > -dy {
            error -= dy;
            x += sx;
        }

        if error2 < dx {
            error += dx;
            y += sy;
        }

        Some(current)
    })
}

fn flip_gray_image(image: &mut GrayImage) {
    for pixel in image.pixels_mut() {
        // Flip the pixel value: 255 - pixel_value
        pixel.0[0] = 255 - pixel.0[0];
    }
}
