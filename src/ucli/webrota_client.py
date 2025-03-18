#!/usr/bin/env python3
"""
Send a JSON payload to the WebRotas server.
"""

import sys
import os
import logging
import coloredlogs
import json
import argparse

import server_interface as si
import json_validate as jv

# ----------------------------------------------------------------------------------------------
# Constants
HELP_TITLE = " TIP "
LINE_STYLE = "-"
DEMO_PAYLOAD_FILE = "demo_payload.json"

# ----------------------------------------------------------------------------------------------
# Configure logging
coloredlogs.install(
    level='INFO',
    fmt=' %(asctime)s | %(levelname)8s |  %(message)s',
    field_styles={'asctime': {'color': 'green'}},
    level_styles={
        'info': {'color': 'blue'},
        'warning': {'color': 'yellow'},
        'error': {'color': 'red'},
        'critical': {'color': 'red', 'bold': True}
    }
)

# ----------------------------------------------------------------------------------------------
class uiShow:
    
    def __init__(self):
        
        self.terminal_width: str = os.get_terminal_size().columns
        """ Terminal width. """
        self.help_title: str = self.draw_title(HELP_TITLE)
        """ Title to be shown in the help message. """
        self.line: str = LINE_STYLE * self.terminal_width
        """ Line to be shown in the help message. """
        
    # ------------------------------------------------------------------------------------------
    def draw_title(self, title: str) -> str:
        """
        Draw a title centered in the terminal.
        
        :param title: Title to be drawn.
        :return: Title drawn.
        """
        
        title_side_bar_length = (self.terminal_width - len(title)) // 2
        side_bar = LINE_STYLE * title_side_bar_length
        title_line = f"{side_bar}{title}{side_bar}"
        if len(title_line) < self.terminal_width:
            title_line += LINE_STYLE
            
        return title_line
    
    # ------------------------------------------------------------------------------------------
    def print_help(self, parser: argparse.ArgumentParser) -> None:
        """
        Print help message.

        :param parser: Argument parser.
        """
        
        print(f"\033[90m\n{self.help_title}")
        parser.print_help()
        print(f"{self.line}\n\033[0m")
    
    # ------------------------------------------------------------------------------------------
    def print_log_header(self) -> None:
        """
        Print log header.
        """
        print(f"\033[90m\n{self.line}\033[0m")
        print("\033[92mTIMESTAMP\033[0m            | LEVEL    | \033[94mMESSAGE\033[0m")

# ----------------------------------------------------------------------------------------------
def main() -> int:

    # Display initial information to the user
    ui = uiShow()
    ui.print_log_header()
    logging.info("Starting WebRotas CLI.")
    
    # Parse arguments received
    parser = argparse.ArgumentParser(description="Send a JSON payload to the WebRotas server.")
    parser.add_argument("payload", nargs="?", default=None, help="Name of the JSON file containing the payload to be sent.")
    args = parser.parse_args()

    # act on arguments
    if args.payload is None:
        logging.warning("Using default payload example.")
        ui.print_help(parser)
        payload_file = os.path.normpath(os.path.join(os.path.dirname(__file__), DEMO_PAYLOAD_FILE))
    else:
        payload_file = args.payload
    
    # get payload data
    try:
        with open(payload_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
        logging.info(f"Payload loaded from {payload_file}.")
    except FileNotFoundError:
        logging.error(f"File {payload_file} not found.\n")
        ui.print_help(parser)
        return 1    
    
    # validate payload
    try:
        payload = jv.validate_and_apply_defaults(payload)
    except jv.PayloadError:
        logging.error("Exiting due to payload validation error.")
        return 1
    
    # send payload to server
    server = si.ServerData()
    if server.is_running():
        try:
            server.send_payload(payload=payload)
        except si.ServerError as e:
            logging.error(f"Error sending payload: {e}")
            return 1

    logging.info("Happy end of the script.\n")

if __name__ == "__main__":
    sys.exit(main())
