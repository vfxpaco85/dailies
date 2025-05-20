import logging

from abc import ABC, abstractmethod

from dailies.constant.main import LOG_FORMAT, LOG_FILE_PATH

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,  # Set the default logger level to INFO
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),  # Log to the console
        logging.FileHandler(LOG_FILE_PATH),
    ],
)


class WriteNodeConfigurator(ABC):
    """
    Base class for configuring write nodes for different file types.
    """

    @abstractmethod
    def configure(self, write_node, frame_rate=None, **kwargs):
        """
        Configure the write node with the given parameters and any additional options in kwargs.

        :param write_node: The write node to be configured.
        :param frame_rate: The frame rate for the video (if applicable).
        :param kwargs: Additional parameters for the write node.
        """
        pass

    def apply_kwargs(self, write_node, kwargs):
        """
        Helper method to apply kwargs values to the write node.

        :param write_node: The write node to be configured.
        :param kwargs: The keyword arguments to apply as knobs on the write node.
        """
        for key, value in kwargs.items():
            if key in write_node.knobs():
                # Log the type of the value before setting
                logging.info(f"Setting knob: {key} with value: {value}")
                print(f"Setting knob: {key} with value: {value}")

                # If the value is a string and contains a number, convert it to an integer
                if isinstance(value, str):
                    # Try to convert to integer if it's a valid number string
                    if value.isdigit():  # checks if the string contains only digits
                        value = int(value)

                # Try to set the value to the write node
                try:
                    knob = write_node[key]
                    knob.setValue(value)
                except Exception as e:
                    logging.error(
                        f"Error applying '{key}' with value '{value}' to write node: {e}"
                    )
                    continue  # Continue processing other kwargs even if one fails

            else:
                logging.warning(
                    f"Unknown key '{key}' for {write_node['file_type'].getValue()} write node configuration."
                )


class MOVConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("mov")
        if frame_rate:
            write_node["mov64_fps"].setValue(frame_rate)

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class EXRConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("exr")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class DNXConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("dnxhd")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class JPEGConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("jpeg")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class GIFConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("gif")
        if frame_rate:
            write_node["fps"].setValue(frame_rate)

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class MXFConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("mxf")
        if frame_rate:
            write_node["fps"].setValue(frame_rate)

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class PNGConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("png")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class TargaConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("targa")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class TIFFConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("tiff")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class XPMConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("xpm")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)


class YUVConfigurator(WriteNodeConfigurator):
    def configure(self, write_node, frame_rate=None, **kwargs):
        write_node["file_type"].setValue("yuv")

        # Apply any additional parameters from kwargs dynamically
        self.apply_kwargs(write_node, kwargs)
