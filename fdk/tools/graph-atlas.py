#!/usr/bin/env python3
"""SHIM — graph-atlas.py đã tách sang repo riêng https://github.com/Rheinmir/orca-graph (engine + test + eval VT).

MUỐN SỬA LOGIC GRAPH → KHÔNG sửa ở đây. Sửa ở repo engine (bản dev thường ở ../orca-graph hoặc clone mới), đọc AGENTS.md
của repo đó: nó liệt kê cái gì thuộc engine, cái gì thuộc overstack, và quy trình re-pin provenance sau khi sửa.

File này giữ ĐÚNG đường dẫn cũ để skill, hook, control-room và máy khách không phải đổi gì: nó tìm engine thật rồi chạy
engine đó TRONG globals của chính nó. `__file__` vì thế vẫn là đường shim → mọi lookup quanh `__file__` của engine
(overstack_paths, build-control-room, graph-viz cạnh graph-atlas) giải theo layout overstack như trước; import bằng
importlib (control-room, test) vẫn thấy đủ hàm của engine.

Thứ tự tìm: $ORCA_GRAPH_ENGINE_DIR → $ORCA_GRAPH_INSTALL_DIR/engine (cùng biến với install.sh của engine) →
~/.orca-graph/repo/engine. Chưa cài → in một lệnh cài, rc 3.
"""
import os, sys
from pathlib import Path

_NAME = "graph-atlas.py"
_dirs = ([Path(os.environ["ORCA_GRAPH_ENGINE_DIR"])] if os.environ.get("ORCA_GRAPH_ENGINE_DIR") else []) \
    + ([Path(os.environ["ORCA_GRAPH_INSTALL_DIR"]) / "engine"] if os.environ.get("ORCA_GRAPH_INSTALL_DIR") else []) \
    + [Path.home() / ".orca-graph" / "repo" / "engine"]
_real = next((d / _NAME for d in _dirs if (d / _NAME).is_file()), None)
if _real is None:
    sys.stderr.write("orca-graph: chưa cài engine (tìm ở: " + ", ".join(str(d) for d in _dirs) + ")\n"
                     "  cài: curl -fsSL https://raw.githubusercontent.com/Rheinmir/orca-graph/main/install.sh | bash\n")
    raise SystemExit(3)
__engine_dir__ = str(_real.parent)
exec(compile(_real.read_text(encoding="utf-8"), str(_real), "exec"), globals())
