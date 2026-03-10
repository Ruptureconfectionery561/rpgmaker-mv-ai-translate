import pytest
from rpgmv_translator.utils.control_codes import ControlCodeManager

def test_extract_and_replace_simple():
    text = r"Hello \N[1], welcome to \C[4]town\C[0]!"
    masked, mapping = ControlCodeManager.extract_and_replace(text)
    
    assert r"\N[1]" in mapping.values()
    assert r"\C[4]" in mapping.values()
    assert r"\C[0]" in mapping.values()
    
    # Placeholders should be sequentially named __CTRL0__, __CTRL1__, etc.
    assert "__CTRL0__" in masked
    assert "__CTRL1__" in masked
    assert "__CTRL2__" in masked

def test_extract_and_replace_duplicates():
    text = r"Wait! \! \! What is that?"
    masked, mapping = ControlCodeManager.extract_and_replace(text)
    
    # The identical duplicate should reuse the placeholder
    assert r"\!" in mapping.values()
    assert len(mapping) == 1
    assert masked == r"Wait! __CTRL0__ __CTRL0__ What is that?"

def test_restore_control_codes():
    text = "Hello __CTRL0__, welcome to __CTRL1__town__CTRL2__!"
    mapping = {
        "__CTRL0__": r"\N[1]",
        "__CTRL1__": r"\C[4]",
        "__CTRL2__": r"\C[0]",
    }
    restored = ControlCodeManager.restore(text, mapping)
    assert restored == r"Hello \N[1], welcome to \C[4]town\C[0]!"

def test_different_slashes():
    # Example control codes parsed out of standard MV game
    text = r"\{BIG NAME\} \> is \^ speaking \|\w \."
    masked, mapping = ControlCodeManager.extract_and_replace(text)
    
    # We should match \{, \}, \>, \^, \|, \. if they exist in the pattern
    # Note: our regex currently supports \\[.!><^|{}]
    assert r"\{" in mapping.values()
    assert r"\}" in mapping.values()
    assert r"\>" in mapping.values()
    assert r"\^" in mapping.values()
    assert r"\|" in mapping.values()
    assert r"\." in mapping.values()
