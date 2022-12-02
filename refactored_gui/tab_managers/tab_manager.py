from PyQt5.QtWidgets import QFrame, QLineEdit, QPushButton, QLabel, QWidget


class TabManager:

    def __init__(self, tab_frame) -> None:

        self.tab_frame = tab_frame

        self.btns = self.get_elements_by_Qtype(QPushButton)
        self.line_edits = self.get_elements_by_Qtype(QLineEdit)
        self.labels = self.get_elements_by_Qtype(QLabel)

    def get_elements_by_Qtype(self, widget_type) -> list[dict[str, QWidget]]:
        # Get top level frames
        top_level_frames = [wid for wid in self.tab_frame.children() if isinstance(wid, QFrame)]

        # Get widgets of type QType
        wids = []
        for frame in top_level_frames:
            for w in frame.children():
                if isinstance(w, widget_type):
                    wids.append({'name': w.objectName(), 'handle': w})

        return wids





