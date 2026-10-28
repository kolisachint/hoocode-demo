//! `toolbox`: small text tools. Std only.

use std::env;
use std::fs;
use std::process;

/// Line and word counts for a piece of text.
#[derive(Debug, PartialEq, Eq)]
pub struct Counts {
    pub lines: usize,
    pub words: usize,
}

/// Counts the lines and whitespace-separated words in `text`.
pub fn count(text: &str) -> Counts {
    Counts {
        lines: text.lines().count(),
        words: text.split_whitespace().count(),
    }
}

fn usage() -> ! {
    eprintln!("usage: toolbox stats <file>");
    process::exit(2);
}

fn run_stats(path: &str) {
    let text = match fs::read_to_string(path) {
        Ok(text) => text,
        Err(err) => {
            eprintln!("toolbox: cannot read {path}: {err}");
            process::exit(1);
        }
    };
    let counts = count(&text);
    println!("lines: {}", counts.lines);
    println!("words: {}", counts.words);
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() == 2 && args[0] == "stats" {
        run_stats(&args[1]);
    } else {
        usage();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn counts_lines_and_words() {
        assert_eq!(count("one two\nthree\n"), Counts { lines: 2, words: 3 });
    }
}
