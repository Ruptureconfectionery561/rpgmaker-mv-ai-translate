import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

from rpgmv_translator.cli import main

@pytest.fixture
def dummy_cli_env(tmp_path: Path):
    input_dir = tmp_path / "game_in"
    input_dir.mkdir()
    (input_dir / "www/data").mkdir(parents=True)
    
    output_dir = tmp_path / "game_out"
    return str(input_dir), str(output_dir), str(tmp_path)

def test_cli_missing_input():
    with patch.object(sys, "argv", ["rpgmv_translator"]):
        with pytest.raises(SystemExit) as exc:
            main()
        # argparse error usually exists with 2
        assert exc.value.code == 2

def test_cli_generate_config(dummy_cli_env):
    _, _, tmp_dir = dummy_cli_env
    config_path = Path("gpt-config.json")
    if config_path.exists():
        config_path.unlink()
        
    with patch.object(sys, "argv", ["rpgmv_translator", "--generate-config"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        
    assert config_path.exists()
    config_path.unlink() # Cleanup

def test_cli_missing_output(dummy_cli_env):
    input_dir, _, _ = dummy_cli_env
    with patch.object(sys, "argv", ["rpgmv_translator", "--input", input_dir]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2

@patch("rpgmv_translator.cli.Extractor")
@patch("rpgmv_translator.cli.Reinjector")
@patch("rpgmv_translator.cli.get_translator")
def test_cli_dry_run(mock_get_translator, mock_reinjector, mock_extractor, dummy_cli_env, capsys):
    input_dir, output_dir, _ = dummy_cli_env
    
    mock_extractor_inst = mock_extractor.return_value
    mock_extractor_inst.extract_all.return_value = []
    
    with patch.object(sys, "argv", ["rpgmv_translator", "--input", input_dir, "--output", output_dir, "--dry-run"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        
    # Extractor should be called, but translator should not
    mock_extractor_inst.extract_all.assert_called_once()
    mock_get_translator.assert_not_called()

@patch("rpgmv_translator.cli.Extractor")
@patch("rpgmv_translator.cli.Reinjector")
def test_cli_inplace(mock_reinjector, mock_extractor, dummy_cli_env):
    input_dir, _, _ = dummy_cli_env
    
    mock_extractor_inst = mock_extractor.return_value
    mock_extractor_inst.extract_all.return_value = []
    
    mock_reinjector_inst = mock_reinjector.return_value
    
    with patch.object(sys, "argv", ["rpgmv_translator", "--input", input_dir, "--inplace"]):
        # We mock internal translation loops so it completes cleanly on empty entries
        main()
        
    # Reinjector should be instantiated with input_dir for both input and output
    mock_reinjector.assert_called_once_with(Path(input_dir), Path(input_dir))
    # It shouldn't copy assets if inplace
    mock_reinjector_inst.copy_unmodified_assets.assert_not_called()

@patch("rpgmv_translator.cli.TranslationConfig")
@patch("rpgmv_translator.cli.Extractor")
@patch("rpgmv_translator.cli.Reinjector")
def test_cli_overrides(mock_reinjector, mock_extractor, mock_config, dummy_cli_env):
    input_dir, output_dir, _ = dummy_cli_env
    
    mock_config_inst = mock_config.load.return_value
    mock_config_inst.provider = "ollama"
    mock_config_inst.model = "default-model"
    mock_config_inst.batch_size = 10
    
    mock_extractor_inst = mock_extractor.return_value
    mock_extractor_inst.extract_all.return_value = []
    
    with patch.object(sys, "argv", ["rpgmv_translator", "--input", input_dir, "--output", output_dir, 
                                    "--provider", "openai", "--model", "gpt-4", "--batch-size", "50", "--debug"]):
        main()
        
    assert mock_config_inst.provider == "openai"
    assert mock_config_inst.model == "gpt-4"
    assert mock_config_inst.batch_size == 50
