# Assembly map

Target 16:9, 1920×1080, 30 fps. Voiceover files are MP3. Each visual is original and contains no third-party stock media.

| Time | Audio | Visual | Edit notes |
|---|---|---|---|
| 0:00–0:34 | `voiceover/01_hook.mp3` | `visuals/01_hook.svg` | Start on browser-versus-API comparison; slow 3% push-in. |
| 0:34–1:18 | `voiceover/02_register_and_authenticate.mp3` | `visuals/02_register.svg` → `03_terms.svg` | Cut on “API key”; highlight X-API-Key and then terms acceptance. |
| 1:18–2:11 | `voiceover/03_upload_without_a_browser.mp3` | `visuals/04_upload.svg` → `05_limits.svg` | Pan through multipart fields, then category limit diagram. |
| 2:11–2:56 | `voiceover/04_the_response_is_machine-usable.mp3` | `visuals/06_response.svg` → `07_describe.svg` | Animate response fields one at a time; switch to text-only agent panel. |
| 2:56–3:30 | `voiceover/05_it_is_more_than_upload.mp3` | `visuals/08_social.svg` → `09_webhooks.svg` | Social/API grid followed by webhook event flow. |
| 3:30–4:29 | `voiceover/06_why_this_matters.mp3` | `visuals/10_loop.svg` → `11_endcard.svg` | Close the loop diagram; hold end card for 3 seconds. |

## Audio
Generated reproducibly with the open-source eSpeak speech engine (`en-us`, 150 wpm target) and encoded to MP3 with ffmpeg. No cloned voice, impersonation, music, or third-party audio.

## Transitions
Use simple 6-frame cross dissolves between diagrams. No rapid flashing. Keep all terminal/API text on screen for at least 2.5 seconds. Add captions from `script.md` for accessibility.
