"""Capture main-interface.webp - docs section 2 (Main Interface).

The original shot sits on a white canvas: 34px above the title bar leave room
for the "repo details" label, 4px left / 4px right / 5px bottom trim the window
to the original 1507x985 image. Every red box, white label plate and label
position below was measured off the original screenshot.

Run it through main.py; it prepares the clone, settings and publishing.
"""
from capture_lib import Tool, capture, repo

# rect: red frame (outer pixel bounds of its 2px bands), label: red serif text,
# label_at: text center, plate: white rect behind the label (used where the
# original plates hide frame edges). The settings frame's bottom sits below
# the canvas - like in the original, only its sides and top are visible.
BOXES = [
    {"rect": (359, 38, 906, 60),
     "label": "repo details", "label_at": (489, 21), "plate": (436, 8, 732, 42)},
    {"rect": (9, 102, 899, 725)},            # commit list
    {"rect": (912, 250, 1497, 296)},         # search-in-diff row
    {"rect": (906, 102, 1497, 726),
     "label": "diff pane", "label_at": (1084, 569), "plate": (1042, 559, 1123, 583)},
    {"rect": (4, 744, 137, 800),
     "label": "Theme selection", "label_at": (204, 778), "plate": (141, 767, 270, 790)},
    {"rect": (7, 950, 175, 981), "bottom_h": 3,
     "label": "zoom", "label_at": (53, 941), "plate": (29, 929, 130, 953)},
    {"rect": (918, 947, 1049, 986), "top_h": 3,
     "label": "settings", "label_at": (956, 938), "plate": (923, 928, 1032, 950)},
    {"rect": (1046, 943, 1490, 980), "bottom_h": 3,
     "label": "Num of commits", "label_at": (1225, 938), "plate": (1152, 929, 1366, 947)},
]


def main():
    # 1. put the reference clone back to the pinned commit
    repo.reset_to_base()

    # 2. open the tool: the original shot was taken with "Showing: 101"
    #    (the commit list is exclusive of its base commit, so HEAD~101)
    tool = Tool(args=["HEAD~101"], log_name="main-interface.log")
    tool.wait_for_window()
    tool.set_size(1497, 946)  # window size of the original shot, title bar included
    tool.sleep(4)  # commit list, diff pane and status labels have settled

    # 3. take the picture with the original shot's white margin
    capture(
        tool,
        name="main-interface.webp",
        description="main window: commit list, search, diff pane, status bar counts",
        boxes=BOXES,
        size=(1507, 985),
        pads=(6, 4, 34, 5),
    )

    # 4. close the tool again
    tool.close()


if __name__ == "__main__":
    main()
