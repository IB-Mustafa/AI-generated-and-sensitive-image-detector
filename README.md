# DeepScanAI

A desktop application that analyzes images for signs of AI generation and sensitive content. Built with Python and CustomTkinter.

---

## What It Does

**AI Generation Detection**
Runs five forensic signals on an image and combines them into a suspicion score (0–100):

- **EXIF Metadata** — real cameras leave rich metadata; AI images often don't
- **FFT Frequency** — natural images follow a 1/f power spectrum; AI images often deviate
- **ELA (Error Level Analysis)** — checks compression history; AI images saved cleanly show near-zero ELA
- **Sensor Noise** — real sensors produce characteristic noise; AI images are often too smooth or show synthetic patterns
- **Chromatic Aberration** — real lenses cause color fringing at edges; AI images typically lack this

**Sensitive Content Detection**
Six detection layers using a combination of OpenCV, YOLOv8, and OCR:

- Restricted items (weapons held in hand)
- Environmental hazards (fire, smoke)
- Blood / injury patterns
- Scene threats (extreme low visibility, looming shadows)
- Adult content (NudeNet — configurable)
- Harmful text in images (pytesseract OCR)

**Deepfake Score**
Face presence is checked via MTCNN. If a face is detected and the AI score is above 50, the deepfake score is elevated.

---

## Project Structure

```
main.py              — entry point, tab navigation
dashboard.py         — dashboard tab (stats, recent scans)
analyze.py           — analyze tab (file picker, results UI)
history.py           — history tab (past scans list)
history_manager.py   — read/write scan history to history.json
analyzer.py          — orchestrator (calls ai_detector + content_detector)
ai_detector.py       — five forensic signals for AI detection
content_detector.py  — sensitive content detection layers
_flagged_labels.py   — content classifier label config
```

---

## Requirements

Python 3.11 recommended — some libraries have compatibility issues on newer versions.

```
pip install -r requirements.txt
```

Key dependencies:
- `customtkinter` — UI
- `torch`, `torchvision` — deep learning backend
- `ultralytics` — YOLOv8 object detection
- `facenet-pytorch` — MTCNN face detection
- `nudenet` — content classification
- `opencv-python` — image processing
- `pytesseract` — OCR (requires Tesseract installed separately)
- `Pillow`, `numpy`, `scipy` — image processing and math

---

## Running

```bash
python main.py
```

Place `yolov8n.pt` in the project root before running.

---

## Known Limitations

- Face detection currently skips weapon/distress checks entirely — should exclude only the face region
- NudeNet label mapping is configurable; by default it is empty
- Threshold values are manually tuned — accuracy varies across different cameras and lighting conditions
- OCR does not reliably handle blurry, handwritten, or non-English text
- No video support — images only
- All processing is local; no cloud sync or report export

---

## Built With

Python · CustomTkinter · PyTorch · YOLOv8 · OpenCV · FaceNet · NudeNet · pytesseract