# Python 3.11 Installation Guide for D Drive

## Step 1: Download Python 3.11

Download Python 3.11.9 (latest stable 3.11 version) from:

**Direct Download Link:**
https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe

Or visit: https://www.python.org/downloads/release/python-3119/

## Step 2: Install Python 3.11 to D Drive

1. Run the downloaded `python-3.11.9-amd64.exe`
2. **IMPORTANT**: Click "Customize installation" (NOT "Install Now")
3. Check all optional features:
   - [x] Documentation
   - [x] pip
   - [x] tcl/tk and IDLE
   - [x] Python test suite
   - [x] py launcher
4. Click "Next"
5. In "Advanced Options":
   - [x] Install for all users
   - [x] Add Python to environment variables
   - **Change install location to:** `D:\Python311`
6. Click "Install"

## Step 3: Verify Installation

Open a NEW command prompt and run:
```bash
D:\Python311\python.exe --version
```

Should show: `Python 3.11.9`

## Step 4: Create Virtual Environment with Python 3.11

Navigate to your project:
```bash
cd C:\Users\Admin\Desktop\Control
```

Create venv with Python 3.11:
```bash
D:\Python311\python.exe -m venv venv311
```

## Step 5: Activate and Install Dependencies

Activate the new virtual environment:
```bash
venv311\Scripts\activate
```

Install dependencies:
```bash
pip install opencv-python mediapipe pygame numpy
```

This should work perfectly with Python 3.11!

## Step 6: Run the Application

```bash
python main.py
```

## Alternative: Quick Command Sequence

Copy and paste these commands one by one:

```bash
cd C:\Users\Admin\Desktop\Control
D:\Python311\python.exe -m venv venv311
venv311\Scripts\activate
pip install opencv-python mediapipe pygame numpy
python main.py
```

## Troubleshooting

If you get "python.exe not found":
- Make sure you installed to `D:\Python311`
- Use the full path: `D:\Python311\python.exe`

If pip install fails:
- Update pip first: `python -m pip install --upgrade pip`
- Then retry: `pip install opencv-python mediapipe pygame numpy`
