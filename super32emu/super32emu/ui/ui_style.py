from PySide2.QtGui import QFont, QFontDatabase


class UiStyle:

    @staticmethod
    def get_font(point_size: int = 10) -> QFont:
        """ Returns fixed font that the system recommends with medium weight """
        fixed_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        fixed_font.setPointSize(point_size)
        fixed_font.setWeight(QFont.Bold)

        return fixed_font

    @staticmethod
    def set_font_weight(font):
        font.setFontWeight(QFont.Bold)
