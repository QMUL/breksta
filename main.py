"""Entry point for Breksta"""

import sys
from PySide6.QtWidgets import QApplication
import hydra
from hydra.core.config_store import ConfigStore
from dotenv import load_dotenv
from app.config import Config
from app.breksta import MainWindow


@hydra.main(version_base="1.3", config_path="app/conf", config_name="config")
def main(cfg: Config) -> None:
    """Start Breksta."""
    # Load environment variables from .env file
    load_dotenv()
    # Hydra: store the configuration
    cs = ConfigStore.instance()
    cs.store(name="breksta_config", node=Config)
    print(cfg)

    # Start Qt application and instantiate the entry point window
    app = QApplication()
    window = MainWindow()
    window.start_web()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
