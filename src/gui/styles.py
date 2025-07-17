# =====================
# styles.py
# =====================
def get_dynamic_styles(dark_mode=True, element=None):
    """Return stylesheet based on theme and element"""
    base_styles = """
        QWidget {{
            font-family: 'Segoe UI', Arial, sans-serif;
        }}
        QSlider::groove:horizontal {{
            background: {slider_groove};
            height: 14px;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal {{
            background: {slider_handle};
            width: 24px;
            height: 24px;
            margin: -5px 0;
            border-radius: 12px;
            border: 2px solid {slider_handle_border};
        }}
        QLabel {{
            color: {text_color};
            font-size: 11pt;
        }}
        QCheckBox {{
            color: {text_color};
            font-size: 11pt;
        }}
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
        }}
        QPushButton {{
            background-color: {button_bg};
            color: {text_color};
            border: 1px solid {button_border};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 11pt;
            min-height: 30px;
        }}
        QPushButton:hover {{
            background-color: {button_hover};
        }}
        QPushButton:pressed {{
            background-color: {button_pressed};
        }}
    """
    
    # Define theme colors
    if dark_mode:
        theme = {
            "bg": "#2b2b2b",
            "text": "#e0e0e0",
            "slider_groove": "#3a3a3a",
            "slider_handle": "#61afef",
            "slider_handle_border": "#3a6a9e",
            "button_bg": "#3a3a3a",
            "button_hover": "#4a4a4a",
            "button_pressed": "#2a2a2a",
            "button_border": "#555555",
            "button_play": "#4CAF50",  # Green
            "button_pause": "#FFC107",  # Amber
            "button_stop": "#F44336",   # Red
            "button_continuous": "#2196F3",  # Blue
        }
    else:
        theme = {
            "bg": "#f0f0f0",
            "text": "#000000",
            "slider_groove": "#d0d0d0",
            "slider_handle": "#0078d7",
            "slider_handle_border": "#005a9e",
            "button_bg": "#e0e0e0",
            "button_hover": "#d0d0d0",
            "button_pressed": "#c0c0c0",
            "button_border": "#aaaaaa",
            "button_play": "#388E3C",  # Dark Green
            "button_pause": "#FFA000",  # Dark Amber
            "button_stop": "#D32F2F",   # Dark Red
            "button_continuous": "#1976D2",  # Dark Blue
        }
    
    # Animation button styles
    animation_button_styles = f"""
        QPushButton#play {{
            background-color: {theme['button_play']};
        }}
        QPushButton#pause {{
            background-color: {theme['button_pause']};
        }}
        QPushButton#stop {{
            background-color: {theme['button_stop']};
        }}
        QPushButton#continuous {{
            background-color: {theme['button_continuous']};
        }}
    """
    
    # Format base styles
    base_styles_formatted = base_styles.format(
        text_color=theme['text'],
        slider_groove=theme['slider_groove'],
        slider_handle=theme['slider_handle'],
        slider_handle_border=theme['slider_handle_border'],
        button_bg=theme['button_bg'],
        button_hover=theme['button_hover'],
        button_pressed=theme['button_pressed'],
        button_border=theme['button_border']
    )
    
    # Combine styles
    full_styles = base_styles_formatted + animation_button_styles
    
    # Return specific element style if requested
    if element == "button":
        return full_styles.split("QPushButton {")[1].split("}")[0] + "}"
    elif element == "slider":
        return full_styles.split("QSlider::groove:horizontal {")[1].split("}")[0] + "}"
    
    return full_styles