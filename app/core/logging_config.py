import logging

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)

logger = logging.getLogger("iot_simulation")
