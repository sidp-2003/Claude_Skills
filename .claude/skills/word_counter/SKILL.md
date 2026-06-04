- - -
name: word-counter
description: Count the number of words in any text the user provides, or in a file. Use this skill whenever the user wants to count words, check word count, measure text length in words, or needs to know how many words are in a passage, document excerpt, sentence, file, or any block of text — even if they don't use the phrase "word counter" explicitly.
- - -

# Word Counter

Count the total number of words in a given text and display the result clearly.

## What counts as a word

A word is any sequence of characters separated by whitespace (spaces, tabs, newlines). Hyphenated words like "well-being" count as one word. Numbers and symbols that appear inline with text count as words if they're separated by whitespace.

## Workflow

1. **Get the text** — if the user provides a file path, read the file contents first; otherwise use the text they pasted directly
2. **Count the words** — split the text on whitespace and count the resulting tokens, ignoring empty strings from multiple spaces or newlines
3. **Display the total** — report the word count in a clear, direct way

## Output format

Keep the output simple and direct:

```
Word count: 42
```

If the input is empty or contains only whitespace, report `Word count: 0`.

## Example

**Input:** "The quick brown fox jumps over the lazy dog"
**Output:** `Word count: 9`

**Input:** "Hello   world\nThis is a test"
**Output:** `Word count: 6`
