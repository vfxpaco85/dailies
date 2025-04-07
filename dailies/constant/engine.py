# Engine classes
ENGINE_CLASSES = {
    "ffmpeg": "dailies.engine.ffmpeg_engine.FFmpegEngine",
    "rvio": "dailies.engine.rvio_engine.RVIOEngine",
    "nuke": "dailies.engine.nuke_engine.NukeEngine",
    "nuke-template": "dailies.engine.nuke_template_engine.NukeTemplateEngine",
}

# Nuke Template Node Names
NUKE_READ_NODE = "Read1"  # Name of the Read node in the Nuke template
NUKE_WRITE_NODE = "Write1"  # Name of the Write node in the Nuke template
# Nuke image sequence padding format
NUKE_FRAME_PADDING_FORMAT = "###"

# Slate settings
FFMPEG_FONT_SIZE = 18
FFMPEG_SPACING_SIZE = 8
FFMPEG_FONT_PATH = "/Windows/Fonts/arial.ttf"

# Supported file types by engine
SUPPORTED_FILE_TYPES = {
    "nuke": [
        "cin",
        "dpx",
        "exr",
        "gif",
        "hdr",
        "jpeg",
        "mov",
        "mxf",
        "pic",
        "png",
        "sgi",
        "targa",
        "tiff",
        "xpm",
        "yuv",
    ],
    "ffmpeg": [
        "dpx",
        "exr",
        "gif",
        "hdr",
        "jpg",
        "jpeg",
        "mov",
        "mp4",
        "mxf",
        "png",
        "sgi",
        "targa",
        "tiff",
        "xpm",
        "yuv",
    ],
    "rvio": ["cin", "dpx", "exr", "tiff", "mov", "jpeg2000", "png", "targa"],
}

# Format and codec mappings
FORMAT_CODECS = {
    "ffmpeg": {
        "dpx": ("dpx", "rawvideo"),
        "exr": ("exr", "rawvideo"),
        "gif": ("gif", "gif"),
        "hdr": ("hdr", "rawvideo"),
        "jpg": ("mjpeg", "mjpeg"),
        "jpeg": ("mjpeg", "mjpeg"),
        "jpeg2000": ("jpeg2000", "jpeg2000"),
        "mov": ("libx264", "yuv420p"),
        "mp4": ("libx264", "yuv420p"),
        "mxf": ("dnxhd", "yuv422p"),
        "png": ("png", "png"),
        "sgi": ("sgi", "rawvideo"),
        "targa": ("tga", "rawvideo"),
        "tiff": ("tiff", "tiff"),
        "xpm": ("xpm", "rawvideo"),
        "yuv": ("yuv", "rawvideo"),
        "cin": ("cin", "rawvideo"),
    },
    "rvio": {
        "cin": "cin",
        "dpx": "dpx",
        "exr": "exr",
        "tiff": "tiff",
        "mov": "mov",
        "jpeg2000": "jpeg2000",
        "png": "png",
        "targa": "tga",
    },
}

# List of supported image sequence formats for detection
IMAGE_SEQUENCES_FILE_TYPES = [
    "dpx",
    "exr",
    "gif",
    "hdr",
    "jpg",
    "jpeg",
    "mxf",
    "png",
    "sgi",
    "targa",
    "tiff",
    "xpm",
    "yuv",
]

# List of supported video formats
VIDEO_FILE_TYPES = [
    "mov",
    "mp4",
    "mxf",
    "jpeg2000",
]
