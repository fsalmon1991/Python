# Metadata

## Primary title
A Game Boy Color Is Running a Transformer — One Token Every 2m49s

## Alternate titles
1. A Transformer on a Stock Game Boy Color? It Actually Runs
2. 8 KB WRAM, 16 Tokens, One Tiny Transformer
3. The Slowest Local AI Demo You’ll See Today

## Hook text
**A TRANSFORMER. ON A GAME BOY COLOR.**

## Description
A proof-of-concept TinyStories-260K transformer is running locally on stock Game Boy Color hardware. The documented hardware run uses 16 transformer forward passes, takes about 45 minutes, and produces recognizable text at roughly 0.0059 tokens/second. The implementation uses quantization, fixed-point inference, bank-switched cartridge data, and cartridge SRAM for the KV cache.

Source project: https://github.com/maddiedreese/gbc-transformer

Package author: @fsalmon1991  
AI-assisted production; technical claims manually checked against the pinned upstream source.

## Tags
`gameboycolor`, `retrocomputing`, `transformer`, `tinyml`, `localai`, `quantization`, `ai`, `retroai`

## Suggested thumbnail/cover text
**LOCAL AI ON A GAME BOY COLOR**

Small corner text: `~0.0059 tok/s`

## Safety / accuracy notes
Do not describe the ~45-minute duration as independently measured by this package author. The upstream README labels it an estimated elapsed time. Do not imply a commercial product, practical chatbot, guaranteed speed, RustChain mining performance, or token earnings.
