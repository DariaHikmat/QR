"""QR code generator API.

Endpoints:
  GET  /healthz        -> liveness probe (used by Azure + the pipeline)
  GET  /api/qr?data=.. -> PNG image of the QR code for `data`
  GET  /               -> static frontend (served from ../frontend/dist)
"""

import io

import qrcode
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="QR Code Generator", version="1.0.0")

MAX_LEN = 2048  # QR codes top out well before this; keeps payloads sane.


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Cheap health check so Azure and CI can confirm the app is alive."""
    return {"status": "ok"}


@app.get("/api/qr")
def make_qr(
    data: str = Query(..., min_length=1, max_length=MAX_LEN, description="Text or URL to encode"),
    box_size: int = Query(10, ge=1, le=40, description="Pixel size of each QR module"),
    border: int = Query(4, ge=0, le=20, description="Quiet-zone width in modules"),
) -> Response:
    """Return a PNG image of the QR code encoding `data`."""
    try:
        qr = qrcode.QRCode(box_size=box_size, border=border)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
    except Exception as exc:  # noqa: BLE001 - surface any encoding failure cleanly
        raise HTTPException(status_code=500, detail=f"Could not generate QR code: {exc}")

    return Response(content=buf.getvalue(), media_type="image/png")

_frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if _frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="static")
