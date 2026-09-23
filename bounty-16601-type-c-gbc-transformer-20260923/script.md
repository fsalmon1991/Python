# Final narration — ~52 seconds

**Hook (0:00–0:05)**  
A stock Game Boy Color is running a transformer locally. Not streaming it. Running it.

**0:05–0:14**  
The proof-of-concept packs a quantized TinyStories-260K model into bank-switched cartridge data and performs integer, fixed-point inference on the handheld.

**0:14–0:24**  
The current hardware run takes about forty-five minutes for sixteen transformer forward passes — roughly 0.0059 tokens per second, or one token every two minutes forty-nine seconds.

**0:24–0:35**  
It is painfully slow, but the result is recognizable text: “Ares was a big, farmer. He was very happy.”

**0:35–0:46**  
The context is capped at sixteen tokens, greedy decoding only, and the KV cache lives in cartridge SRAM so base WRAM stays below eight kilobytes.

**Close (0:46–0:53)**  
This is not a practical chatbot. It is a real transformer squeezed onto a stock Game Boy Color — and that is the point.

---

Word count: ~105 words.  
All numbers and technical details are mapped in `SOURCES.md`.  
AI-assisted drafting was manually source-checked before submission.
