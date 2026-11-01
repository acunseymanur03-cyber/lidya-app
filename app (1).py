import os
import streamlit as st

# Lidya AI - yükleyici. Uygulama 2 küçük parçaya bölünmüştür (lidya_part1.py ... lidya_part2.py).
_PARTS = 2
_dir = os.path.dirname(os.path.abspath(__file__))
_chunks = []
_missing = []
for _i in range(1, _PARTS + 1):
    _path = os.path.join(_dir, f"lidya_part{_i}.py")
    try:
        with open(_path, encoding="utf-8") as _f:
            _text = _f.read()
    except FileNotFoundError:
        _missing.append(f"lidya_part{_i}.py bulunamadı")
        continue
    if not _text.rstrip().endswith(f"# --- END PART {_i} ---"):
        _missing.append(f"lidya_part{_i}.py eksik yüklenmiş (son satırı kesilmiş)")
    _chunks.append(_text)

if _missing:
    st.error("Lidya başlatılamadı: " + "; ".join(_missing) + ". Bu dosyaları GitHub'a yeniden yükle.")
    st.stop()

exec(compile("".join(_chunks), "lidya_app", "exec"), globals())
