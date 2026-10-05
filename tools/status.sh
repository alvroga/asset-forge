#!/usr/bin/env bash
# Show what the overnight run is doing right now. Usage: tools/status.sh [date]   (default: newest runs/<date>)
cd "$(dirname "$0")/.."
D="${1:-$(ls -t runs | grep -v '\.' | head -1)}"
echo "== runs/$D  ($(date '+%H:%M:%S')) =="
for p in runs/"$D"/*/; do
  [ -d "$p" ] || continue
  n=$(basename "$p"); s=""
  for f in source.png matted.png raw.glb final.glb; do [ -f "$p$f" ] && s="$s$f " ; done
  if [ -f "$p/result.json" ]; then st=$(python3 -c "import json,sys;r=json.load(open('$p/result.json'));print('DONE ok' if r['ok'] else 'DONE FAILED: '+r.get('error',''))")
  else st="running/pending"; fi
  echo "$n: $st | outputs: ${s:-none} | log updated $(stat -f '%Sm' -t %H:%M:%S "$p/run.log" 2>/dev/null)"
  [ -f "$p/run.log" ] && tail -c 300 "$p/run.log" | tr '\r' '\n' | tail -1 | cut -c1-120
done
echo "-- active processes --"
ps -axo etime,rss,command | grep -E "sd-cli|hunyuan_mlx|retopo_repaint|matte.py|Blender" | grep -v grep | awk '{printf "%s  %.1fGB  ", $1, $2/1048576; for(i=3;i<=NF&&i<6;i++) printf "%s ", $i; print ""}' | sed "s#$PWD/##g"
