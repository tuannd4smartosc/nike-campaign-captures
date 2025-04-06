import streamlit as st
import logging
import io

class StreamlitLogger:
    _instance = None  # Singleton instance
    
    def __new__(cls, *args, **kwargs):
        """Implement Singleton pattern."""
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, log_widget_name="Log Output"):
        if not hasattr(self, '_initialized'):  # Prevent reinitializing the logger
            self._initialized = True
            # Set up the logger
            self.logger = logging.getLogger("StreamlitLogger")
            self.logger.setLevel(logging.DEBUG)
            
            # Streamlit widget for displaying logs
            self.log_widget_name = log_widget_name
            
            # Use StringIO to capture logs in memory
            self.log_stream = io.StringIO()
            self.log_handler = logging.StreamHandler(self.log_stream)
            self.log_handler.setLevel(logging.DEBUG)
            
            # Use a custom formatter for clean logs
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            self.log_handler.setFormatter(formatter)
            
            # Add the handler to the logger
            self.logger.addHandler(self.log_handler)
            
            # Display log output area in Streamlit
            self.log_output = st.empty()  # Streamlit widget placeholder for logs
    
    def log(self, message, level="INFO"):
        """Log a message with the specified level and display in Streamlit."""
        if level == "INFO":
            self.logger.info(message)
        elif level == "DEBUG":
            self.logger.debug(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)

        # Display the latest log message on Streamlit
        self.display_log_output()

    def display_log_output(self):
        """Display the latest logs in Streamlit's log widget."""
        log_content = self.get_log_output()
        self.log_output.text_area(self.log_widget_name, log_content, height=300)

    def get_log_output(self):
        """Get the current log content as a string."""
        # Retrieve the logs from the StringIO stream
        log_content = self.log_stream.getvalue()
        # Clear the log stream after retrieving its content
        self.log_stream.truncate(0)
        self.log_stream.seek(0)
        return log_content
