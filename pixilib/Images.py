from os import path
from pygame import image, transform


class ToolAssets:
    def __init__(self):
        project_root = path.abspath(".")
        tool_normal = path.join(project_root, "Assets", "icons", "normal")
        tool_clicked = path.join(project_root, "Assets", "icons", "clicked")

        icon_size = (32, 32)

        self.paintbrush = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "paint.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(
                    path.join(tool_clicked, "paint_clicked.png")
                ).convert_alpha(),
                icon_size,
            ),
        )

        self.eraser = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "eraser.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(
                    path.join(tool_clicked, "eraser_clicked.png")
                ).convert_alpha(),
                icon_size,
            ),
        )

        self.line = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "line.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(path.join(tool_clicked, "line_clicked.png")).convert_alpha(),
                icon_size,
            ),
        )

        self.fill = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "fill.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(path.join(tool_clicked, "fill_clicked.png")).convert_alpha(),
                icon_size,
            ),
        )

        self.clear = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "clear.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(
                    path.join(tool_clicked, "clear_clicked.png")
                ).convert_alpha(),
                icon_size,
            ),
        )

        self.pan = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "move.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(path.join(tool_clicked, "move_clicked.png")).convert_alpha(),
                icon_size,
            ),
        )

        self.eyedropper = ToggledImage(
            transform.scale(
                image.load(path.join(tool_normal, "eyedropper.png")).convert_alpha(),
                icon_size,
            ),
            transform.scale(
                image.load(
                    path.join(tool_clicked, "eyedropper_clicked.png")
                ).convert_alpha(),
                icon_size,
            ),
        )

    def select_tool(self, tool_name: str):
        tool = {
            "paintbrush": self.paintbrush,
            "eraser": self.eraser,
            "line": self.line,
            "fill": self.fill,
            "clear": self.clear,
            "pan": self.pan,
            "eyedropper": self.eyedropper,
        }
        if tool_name in tool:
            for t in tool.values():
                t.set_state(False)
            tool[tool_name].set_state(True)
        else:
            raise ValueError(f"Tool '{tool_name}' not found.")


class CursorAssets:
    def __init__(self):
        project_root = path.abspath(".")
        cursor_image_path = path.join(project_root, "Assets", "icons", "cursor")

        self.paint_cursor = image.load(
            path.join(cursor_image_path, "paint_cursor.png")
        ).convert_alpha()

        self.eraser_cursor = image.load(
            path.join(cursor_image_path, "eraser_cursor.png")
        ).convert_alpha()

        self.line_cursor = image.load(
            path.join(cursor_image_path, "line_cursor.png")
        ).convert_alpha()

        self.fill_cursor = image.load(
            path.join(cursor_image_path, "fill_cursor.png")
        ).convert_alpha()

        self.clear_cursor = image.load(
            path.join(cursor_image_path, "clear_cursor.png")
        ).convert_alpha()

        self.move_cursor = image.load(
            path.join(cursor_image_path, "move_cursor.png")
        ).convert_alpha()

        self.eyedropper_cursor = image.load(
            path.join(cursor_image_path, "eyedropper_cursor.png")
        ).convert_alpha()

    def select_tool(self, tool_name: str):
        tool = {
            "paintbrush": self.paint_cursor,
            "eraser": self.eraser_cursor,
            "line": self.line_cursor,
            "fill": self.fill_cursor,
            "clear": self.clear_cursor,
            "pan": self.move_cursor,
            "eyedropper": self.eyedropper_cursor,
        }

        tool_image_offset = {
            "paintbrush": (4, 4),
            "eraser": (4, 4),
            "line": (4, 4),
            "fill": (8, 24),
            "clear": (16, 16),
            "pan": (16, 16),
            "eyedropper": (8, 24),
        }

        if tool_name in tool:
            for t in tool.values():
                if isinstance(t, ToggledImage):
                    t.set_state(False)
            return tool[tool_name], tool_image_offset[tool_name]
        else:
            return None, (0, 0)


class ToggledImage:
    def __init__(self, normal_image: image, clicked_image: image):
        self.normal_image = normal_image
        self.clicked_image = clicked_image
        self.is_clicked = False

    def toggle(self):
        self.is_clicked = not self.is_clicked

    def set_state(self, state: bool):
        """Set the clicked state of the image."""
        self.is_clicked = state

    def get_image(self):
        if self.is_clicked:
            return self.clicked_image
        else:
            return self.normal_image
