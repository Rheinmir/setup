"""Bật app payroll: python3 _run_app.py → http://localhost:8770/"""
from app.ui import build_server

srv = build_server(8770)
print("payroll đang chạy tại http://localhost:8770/", flush=True)
srv.serve_forever()
