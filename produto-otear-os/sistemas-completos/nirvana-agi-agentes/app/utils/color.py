def hex_to_ass(hex_color: str) -> str:
    """
    Converts HEX color (e.g. #FF5733 or #333) to ASS format (&HBBGGRR&).
    ASS format is Blue-Green-Red in hex, reversed from Web RGB.
    """
    hex_color = hex_color.lstrip('#')
    
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
        
    if len(hex_color) != 6:
        # Fallback to white if invalid
        return "&HFFFFFF&"
        
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    
    # ASS uses BGR order
    return f"&H{b}{g}{r}&"
