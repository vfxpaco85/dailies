# Troubleshooting

If you're encountering issues with the **Dailies Tool**, refer to the following common problems and solutions. If you're unable to resolve the issue, consider checking the logs or console output for more detailed information.

## 1. **Issue: "Command not found" for FFmpeg, Nuke, or RV**

### Solution:
This error usually occurs when the required external software (FFmpeg, Nuke, or RV) is not correctly added to your system's `PATH`.

To fix this:

- **FFmpeg**:
  - Ensure that FFmpeg is installed and that the `ffmpeg` executable is in your system's `PATH`.
  - You can verify this by running:

```bash
  # Run this command to check if FFmpeg is accessible from the terminal
  ffmpeg -version
```

  If the command is not recognized, add FFmpeg to your `PATH` or provide the full path to the executable in the Dailies Tool’s configuration.

- **Nuke**:
  - Make sure that the `nuke` executable and its Python bindings are available in your environment.
  - You can check if Nuke is accessible by running:

```bash
  # Run this command to check if Nuke is accessible from the terminal
  nuke --version
```

- **RV**:
  - Ensure that the `rv` executable is accessible from your terminal.
  - Test it by running:

```bash
  # Run this command to check if RV is accessible from the terminal
  rv --version
```

### Additional Notes:
If you installed the software but it's still not recognized, check the installation paths and update the system's `PATH` variable to include the directories where the executables are located.

## 2. **Issue: Missing or Incorrect Configuration in `constants.py`**

### Solution:
The **Dailies Tool** relies on correct configurations in the `constants.py` file. Missing or incorrect API URLs, authentication tokens, or other paths can cause errors during execution.

Make sure the following are configured properly:
- **API URLs**: Ensure any URL or endpoint paths are correct.
- **Authentication tokens**: Make sure you’ve added any required tokens for authentication with services, if applicable.
- **Paths**: Ensure the paths to software like FFmpeg, Nuke, or RV are correct in `constants.py`.

You can find the configuration section in `constants.py` and update the following values:

```python
# Example of config section in constants.py
FFMPEG_PATH = "/path/to/ffmpeg"  # Update this to the correct FFmpeg path
NUKE_PATH = "/path/to/nuke"      # Update this to the correct Nuke path
RV_PATH = "/path/to/rv"          # Update this to the correct RV path
```

If the tool isn’t working as expected, double-check this file and ensure all the necessary paths and tokens are filled out properly.

## 3. **Issue: Missing Python Dependencies**

### Solution:
If you're encountering an error related to missing Python packages or dependencies, ensure you’ve installed all required libraries by running:

```bash
# Install all the required Python packages from the requirements.txt file
pip install -r requirements.txt
```

If you’re still facing issues, it may help to:
- Verify your Python version by running:

```bash
  # Check your Python version to make sure you're using Python 3.x
  python --version
```

Ensure you’re using Python 3.x, as Python 2.x might not work with the dependencies required by the tool.

- Check that `pip` is up to date by running:

```bash
  # Upgrade pip to the latest version
  pip install --upgrade pip
```

## 4. **Issue: Image Sequence Not Found or Not Loaded**

### Solution:
If the tool cannot find or load your image sequence, it could be due to an incorrect file path or missing files.

- Ensure that the input path to the image sequence is correct and that all the files exist.
- Check that the sequence is named correctly, and that the frame range is continuous (e.g., `frame_001.exr`, `frame_002.exr`, etc.).
- If the sequence is on a network drive or an external disk, make sure the drive is connected and accessible.

Verify your input path by using the following command:

```bash
# Check if your image sequence files are in the correct directory
ls /path/to/image_sequence
```

If the files are listed correctly, try loading the sequence again.

## 5. **Issue: Tool Crashes or Freezes During Processing**

### Solution:
If the tool crashes or freezes, check the following:

- **Memory Usage**: If you're working with high-resolution image sequences (e.g., EXR files), the tool might run out of memory. Try reducing the resolution or converting to a lighter format (like JPG) before processing.
- **Output Path**: Ensure that the output path where you want to save the result exists and is writable. You may need to create the output folder manually.
- **Logs**: Check the logs or console output to identify any specific errors related to the crash. This could provide more information about what went wrong.

You can try running the tool with reduced settings to check if the problem persists:

```bash
# Run the tool with a smaller resolution and JPG output to reduce load
python dailies_tool.py --resolution 1280x720 --format jpg
```

This command will generate a smaller output and might avoid memory or performance issues.

## 6. **Issue: Permissions Issues**

### Solution:
If you're running into permission errors (e.g., "Permission denied" when accessing files or folders), try the following:

- **Check Folder Permissions**: Ensure that the user running the tool has appropriate read/write permissions for the input and output folders.
- **Run as Administrator**: On Windows, try running the terminal or command prompt as an Administrator. On macOS or Linux, you can use `sudo` to run the tool with elevated privileges.

```bash
# Use sudo to run the tool with elevated privileges if needed
sudo python dailies_tool.py
```

Make sure to only use `sudo` if you understand the implications of running commands with elevated privileges.

---

If none of these solutions resolve your issue, feel free to open an issue in the project's GitHub repository or contact me for further assistance.
