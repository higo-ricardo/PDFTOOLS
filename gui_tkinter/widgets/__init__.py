"""
Widgets customizados para CustomTkinter.

Módulos:
- modern_widgets: Botões, cards, drop zones e outros elementos estéticos
- widgets: Widgets reutilizáveis para interface (W01-W12)
"""

from gui_tkinter.widgets.modern_widgets import (
    ModernButton,
    ShadowFrame,
    PreviewCard,
    ProgressCard,
    DropZoneFrame,
)

from gui_tkinter.widgets.widgets import (
    NumericEntryPair,      # W01
    TooltipCheckbox,       # W02
    FormatSelector,        # W03
    FilePickerButton,      # W04
    SectionSeparator,      # W05
    DynamicStatusArea,     # W06
    MetadataGrid,          # W07
    ValueSlider,           # W08
    ClearListButton,       # W09
    ProcessingIndicator,   # W10
    SummaryCard,           # W11
    SmartIntervalInput,    # W12
)

__all__ = [
    # Modern widgets
    "ModernButton",
    "ShadowFrame",
    "PreviewCard",
    "ProgressCard",
    "DropZoneFrame",
    # Reusable widgets (W01-W12)
    "NumericEntryPair",
    "TooltipCheckbox",
    "FormatSelector",
    "FilePickerButton",
    "SectionSeparator",
    "DynamicStatusArea",
    "MetadataGrid",
    "ValueSlider",
    "ClearListButton",
    "ProcessingIndicator",
    "SummaryCard",
    "SmartIntervalInput",
]
