# Libethenite Loom

Full-colour Python 3 neon warp-weft arcade for [ElbowOS](https://x.com/ElbowOS).

A copper shuttle flies across eight glowing warp threads. Choose a column and beat when the weft hue matches that thread. Stitches lock into the cloth. A wrong hue snags a reed.

This is an original loom beater. It is not a commercial emulator and it does not use trademarked characters.

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 libethenite_loom.py --play
```

A / D or Left / Right choose the column. Space beats. R restarts.

## Record a 9:16 reel

```bash
python3 libethenite_loom.py --record
```

Headless autoplay writes a 15-second 1080x1920 H.264 MP4 (SDL dummy driver, ffmpeg libx264 yuv420p, CRF 20, +faststart).

## Links

- Featured account: https://x.com/ElbowOS
- Drive reel: https://drive.google.com/file/d/12CJ6CiLxE3_mG2qB4vPL3aGtHJmQO8Vu/view
