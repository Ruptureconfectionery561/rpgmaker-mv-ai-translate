import textwrap
import re

def wrap_text(text: str, width: int = 54) -> str:
    """
    Wraps text to the specified width, preserving existing newlines 
    and handling RPG Maker control codes gracefully so they don't break mid-code.
    
    Default width is 54 characters, which is a safe maximum for standard 
    RPG Maker MV dialogue boxes at default resolutions.
    """
    lines = text.split('\n')
    wrapped_lines = []
    
    for line in lines:
        if not line:
            wrapped_lines.append("")
            continue
            
        # We use a custom wrap that tries to respect words.
        # textwrap.wrap does not know about control codes perfectly,
        # but since control codes are usually short (e.g. \\C[4]), 
        # treating them as part of a word is usually fine.
        wrapped = textwrap.wrap(
            line, 
            width=width, 
            break_long_words=False, 
            break_on_hyphens=False
        )
        if not wrapped:
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(wrapped)
            
    return '\n'.join(wrapped_lines)
