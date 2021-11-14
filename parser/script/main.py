"""
Copyright 2021 Andrey Plugin (9keepa@gmail.com)
Licensed under the Apache License v2.0
http://www.apache.org/licenses/LICENSE-2.0
"""
from tool import log as _log
from parser_snapshot import main
log = _log("MAIN")


log.info("Started the script")

try:
    main()
except KeyboardInterrupt:
    log.info("=== Stopped the script ===")