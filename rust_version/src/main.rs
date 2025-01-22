use std::{env, process};
use knit_portrait::{compute_string_order, Config};
fn main() {

    let config = Config::build(env::args()).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {err}");
        process::exit(1);
    });

    let _ = compute_string_order(&config);
}
