import argparse
import asyncio
import importlib
import json
import logging
import os
from tig_benchmarker.event_bus import process_events, emit

logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
logging.basicConfig(
    format='%(levelname)s - [%(name)s] - %(message)s',
    level=logging.INFO
)

async def main(
    player_id: str,
    api_key: str,
    config: dict,
    backup_folder: str, 
    api_url: str,
    port: int
):
    extensions = {}
    for ext_name in config["extensions"]:
        logger.info(f"loading extension {ext_name}")
        module = importlib.import_module(f"tig_benchmarker.extensions.{ext_name}")
        extensions[ext_name] = module.Extension(
            player_id=player_id,
            api_key=api_key,
            api_url=api_url,
            backup_folder=backup_folder,
            port=port,
            **config["config"]
        )

    asyncio.create_task(process_events())

    while True:
        await emit('update')
        await asyncio.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TIG Benchmarker")
    parser.add_argument("player_id", help="Player ID")
    parser.add_argument("api_key", help="API Key")
    parser.add_argument("config_path", help="Path to the configuration JSON file")
    parser.add_argument("--api", default="https://mainnet-api.tig.foundation", help="API URL (default: https://mainnet-api.tig.foundation)")
    parser.add_argument("--backup", default="backup", help="Folder to save pending submissions and other data")
    parser.add_argument("--port", type=int, default=5115, help="Port to run the server on (default: 5115)")
    
    args = parser.parse_args()

    if not os.path.exists(args.config_path):
        logger.error(f"config file not found at path: {args.config_path}")
        sys.exit(1)
    with open(args.config_path, "r") as f:
        config = json.load(f)
    if not os.path.exists(args.backup):
        logger.info(f"creating backup folder at {args.backup}")
        os.makedirs(args.backup, exist_ok=True)

    asyncio.run(main(args.player_id, args.api_key, config, args.backup, args.api, args.port))