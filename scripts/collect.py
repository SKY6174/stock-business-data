"""Collect only the public official KRX issuer table; no credentials or portfolios."""
import base64
import datetime
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen

SOURCE = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"


def collect(output):
    request = Request(SOURCE, headers={"User-Agent": "KYSONG-StockStudio/1.0 (+https://kysong.org)"})
    with urlopen(request, timeout=15) as response:
        if response.url != SOURCE or response.status != 200:
            raise ValueError("Official source unavailable")
        raw = response.read(3 * 1024 * 1024 + 1)
    if len(raw) > 3 * 1024 * 1024:
        raise ValueError("Official source too large")
    charset = "utf-8" if re.search(rb"charset\s*=\s*[\"']?utf-8", raw[:4096], re.I) else "cp949"
    text = raw.decode(charset)
    if not all(term in text for term in ["회사명", "시장구분", "종목코드", "업종", "주요제품"]):
        raise ValueError("Official table format unavailable")
    rows = len(re.findall(r"<tr\b", text, re.I))
    if rows < 1000 or rows > 5001 or "</html>" not in text.lower():
        raise ValueError("Official table incomplete")
    fetched_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    Path(output).write_text(json.dumps({"source": SOURCE, "fetchedAt": fetched_at, "html": base64.b64encode(raw).decode("ascii")}), encoding="utf-8")
    print(f"Official KRX table collected: {rows - 1} rows")


if __name__ == "__main__":
    collect(sys.argv[1])
