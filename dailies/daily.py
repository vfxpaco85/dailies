import argparse
import json
import logging

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH
from dailies.factory import VideoEngineFactory, TrackingSoftwareFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set the default logging level to INFO
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler(LOG_FILE_PATH),  # Log to a file for persistence
    ],
)


# Main workflow: Create Video and Update Tracking
def main():
    # Step 1: Set up argument parser
    parser = argparse.ArgumentParser(description="Create media and update tracking.")

    # Video creation parameters
    parser.add_argument(
        "--video-engine",
        type=str,
        required=True,
        choices=["ffmpeg", "rvio", "nuke", "nuke-template"],
        help="Video engine to use (ffmpeg, rvio, nuke, nuke-template).",
    )
    parser.add_argument(
        "--input-path",
        type=str,
        required=True,
        help="Path to the input image sequence folder.",
    )
    parser.add_argument(
        "--output-path",
        type=str,
        required=True,
        help="Path where the output (image/video) will be saved.",
    )

    # Extension, Resolution and FPS flags
    parser.add_argument(
        "--extension",
        type=str,
        default="mov",
        help="Output file extension (e.g., mov, mp4, avi). Default is 'mov'.",
    )
    parser.add_argument(
        "--resolution",
        type=str,
        default="1920x1080",
        help="Resolution for the output (widthxheight). Default is 1920x1080.",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        help="Frame rate for the video (default is 30).",
    )

    # Nuke template flag
    parser.add_argument(
        "--template-name",
        type=str,
        default="default_template",
        help="The name of the Nuke template to use.",
    )

    # Slate flag
    parser.add_argument(
        "--slate-data",
        type=str,
        help="JSON string or comma-separated key-value pairs (e.g., 'artist=foo,project=bar').",
    )

    # Options flag for additional settings
    parser.add_argument(
        "--options",
        type=str,
        help="Comma-separated string or JSON string containing additional options for the video creation (e.g., option1,option2 or {'option1': true, 'option2': true}).",
    )

    # Tracking software parameters
    parser.add_argument(
        "--tracking-software",
        type=str,
        default="shotgun",
        choices=["shotgun", "ftrack", "kitsu", "flow"],
        help="Tracking software to use (shotgun, ftrack, kitsu, or flow).",
    )
    parser.add_argument(
        "--project-id",
        type=int,
        required=True,
        help="Project ID to insert the version into the tracking system.",
    )
    parser.add_argument(
        "--version-number",
        type=int,
        default=1,
        help="Version number to insert into the tracking system.",
    )

    # Parse arguments
    args = parser.parse_args()

    try:
        # Step 2: Create video using chosen video engine
        video_engine = VideoEngineFactory.get_video_engine(args.video_engine.lower())

        logging.info(f"Creating output using {args.video_engine} engine.")

        # Step 3: Handle slate data (if provided)
        slate_data = {}

        if args.slate_data:
            try:
                # Try parsing as JSON first
                slate_data = json.loads(args.slate_data)
                logging.info(f"Slate data parsed as JSON: {slate_data}")
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as comma-separated key-value pairs
                slate_data = dict(
                    (key.strip(), value.strip())
                    for key, value in (item.split("=") for item in args.slate_data.split(","))
                )
                logging.info(f"Slate data parsed as comma-separated key-value pairs: {slate_data}")

            # Provide default values if keys are missing
            slate_data.setdefault("artist", "Unknown Artist")
            slate_data.setdefault("project", "Unnamed Project")
            slate_data.setdefault("fps", "24 FPS")
            slate_data.setdefault("version", "v001")

            logging.info(f"Creating slate with data: {slate_data}")

        # Step 4: Parse resolution (widthxheight format)
        try:
            resolution = tuple(map(int, args.resolution.split("x")))
            if len(resolution) != 2:
                raise ValueError(
                    "Resolution must be in the format widthxheight (e.g., 1920x1080)."
                )
            logging.info(f"Resolution set to {resolution[0]}x{resolution[1]}")
        except ValueError:
            raise ValueError(
                "Invalid resolution format. It should be 'widthxheight' (e.g., 1920x1080)."
            )

        # Step 5: Parse options (comma-separated or JSON format)
        options = {}
        if args.options:
            try:
                # Try parsing as JSON first
                options = json.loads(args.options)
                logging.info(f"Options parsed as JSON: {options}")
            except json.JSONDecodeError:
                # If JSON parsing fails, treat as comma-separated list
                options = {opt.strip(): True for opt in args.options.split(",")}
                logging.info(f"Options parsed as comma-separated list: {options}")

        # Step 6: Call the appropriate create_media method based on video engine
        if args.video_engine == "nuke-template":
            # For NukeTemplateEngine, we only need input, output, and template
            video_engine.create_media(
                input_path=args.input_path,
                output_path=args.output_path,
                template=args.template_name,
            )
        else:
            # For other engines, we pass additional parameters (extension, resolution, etc.)
            video_engine.create_media(
                input_path=args.input_path,
                output_path=args.output_path,
                extension=args.extension,
                resolution=resolution,  # Pass the resolution as a tuple (width, height)
                fps=args.fps,
                options=options,  # Pass options (comma-separated or JSON)
            )

        # Step 7: Insert version into tracking software
        tracking_software = TrackingSoftwareFactory.get_tracking_software(
            args.tracking_software
        )

        tracking_software.insert_version(
            args.project_id, args.version_number, args.output_path
        )

        logging.info(
            f"Version {args.version_number} inserted into {args.tracking_software}."
        )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise


# Run the workflow
if __name__ == "__main__":
    main()
