import re
from typing import Tuple, Dict

# Regex to match RPG Maker MV control codes.
# This matches:
# - \\ followed by letters with an optional index, e.g., \\N[1], \\C[4], \\V[3], \\PX
# - \\ followed by specific symbols, e.g., \\!, \\., \\>, \\<, \\^, \\|
# Note: Since the JSON files store single backslashes as '\\', in Python strings loaded from JSON
# they will be literal backslashes '\\'. 
# When compiling the regex, we match a literal backslash using r'\\'.
CONTROL_CODE_PATTERN = re.compile(r'\\[A-Za-z]+(?:\[\d+\])?|\\[.!><^|{}]')

class ControlCodeManager:
    """
    Manages the extraction and restoration of control codes to prevent LLMs from corrupting them.
    Each unique control code within a string is mapped to a placeholder like __CTRL0__.
    """
    
    @staticmethod
    def extract_and_replace(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Finds control codes in the given text, replaces them with placeholders, 
        and returns the modified text plus a mapping to restore them.
        """
        mapping = {}
        counter = 0
        
        # We need a predictable replacement logic. We'll find all unique matches.
        # However, order might matter. Let's just find all matches.
        
        def repl(match: re.Match) -> str:
            nonlocal counter
            original = match.group(0)
            
            # If we already have this exact control code in mapping, we can reuse its placeholder.
            # But the mapping dict is conventionally placeholder -> original.
            # So we map original -> placeholder in a temp dict or just iterate.
            placeholder = None
            for p, o in mapping.items():
                if o == original:
                    placeholder = p
                    break
            
            if placeholder is None:
                placeholder = f"__CTRL{counter}__"
                mapping[placeholder] = original
                counter += 1
                
            return placeholder

        masked_text = CONTROL_CODE_PATTERN.sub(repl, text)
        return masked_text, mapping

    @staticmethod
    def restore(text: str, mapping: Dict[str, str]) -> str:
        """
        Restores control codes in the text using the provided mapping.
        """
        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
