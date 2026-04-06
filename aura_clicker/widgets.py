from __future__ import annotations

import customtkinter as ctk


class CTkListbox(ctk.CTkFrame):
    def __init__(self, master, height: int = 220, **kwargs):
        super().__init__(master, **kwargs)
        self._items: list[str] = []
        self._buttons: list[ctk.CTkButton] = []
        self._selected_index: int | None = None

        self._scrollable = ctk.CTkScrollableFrame(self, width=340, height=height)
        self._scrollable.pack(fill="both", expand=True, padx=6, pady=6)

    def insert(self, value: str) -> None:
        idx = len(self._items)
        self._items.append(value)

        button = ctk.CTkButton(
            self._scrollable,
            text=value,
            anchor="w",
            fg_color="transparent",
            text_color=("#1A2238", "#E5E7EB"),
            hover_color=("#E8EEFF", "#27334D"),
            command=lambda i=idx: self.select(i),
        )
        button.pack(fill="x", padx=4, pady=2)
        self._buttons.append(button)

    def select(self, index: int) -> None:
        self._selected_index = index
        for i, button in enumerate(self._buttons):
            active = i == index
            button.configure(
                fg_color=("#5B5CE2", "#4F46E5") if active else "transparent",
                text_color=("#FFFFFF", "#FFFFFF") if active else ("#1A2238", "#E5E7EB"),
            )

    def get_selected_index(self) -> int | None:
        return self._selected_index

    def delete_selected(self) -> int | None:
        if self._selected_index is None:
            return None

        index = self._selected_index
        self._items.pop(index)
        self._selected_index = None
        self._render_items()
        return index

    def clear(self) -> None:
        self._items.clear()
        self._selected_index = None
        self._render_items()

    def set_items(self, values: list[str]) -> None:
        self._items = list(values)
        self._selected_index = None
        self._render_items()

    def _render_items(self) -> None:
        for button in self._buttons:
            button.destroy()
        self._buttons.clear()

        for idx, value in enumerate(self._items):
            button = ctk.CTkButton(
                self._scrollable,
                text=value,
                anchor="w",
                fg_color="transparent",
                text_color=("#1A2238", "#E5E7EB"),
                hover_color=("#E8EEFF", "#27334D"),
                command=lambda i=idx: self.select(i),
            )
            button.pack(fill="x", padx=4, pady=2)
            self._buttons.append(button)
