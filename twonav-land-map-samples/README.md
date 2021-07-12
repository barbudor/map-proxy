# TwoNav Land map samples

This folder contains some sample "cosm" map files for TwoNav Land which will call the map-proxy web server.

It shows how you can customize such files. Generally you will have to provide 2 elements:
- URL to map-proxy (here I'm running map-proxy locally on the same PC but you could run it on a separate server, in a docker, in the cloud, ...)
- Width and Height (in `PIXWIDTH`, `PIXHEIGHT`, `BitmapWidth`, `BitmapHeight`, `Calibration` section `P1` and `P2` ) needs to be adapted depending on the `MAXZOOMLEVEL` following this table:

| MAXZOOMLEVEL | Width/Height |
|-|-|
| 14 | 4194304 |
| 15 | 8388608 |
| 16 | 16777216 |
| 17 | 33554432 |
| 18 | 67108864 |
| 19 | 134217728 |
| 20 | 268435456 |
