import sqlite3, json; from pathlib import Path
DB_PATH = Path("pybackend/dreamfly.db"); TARGET_MIND_ID = "183a3e21-b402-4c2e-9409-8e02d3cf7bfc"
conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
print("==== minds 列表 ====")
for row in cur.execute("SELECT id, name, voice_id FROM minds"):
    print("id:", row[0], "\nname:", row[1], "\nvoice_id:", row[2], "\n" + "-"*40)
print("\n==== 目标 mind 的 voice_prompt 情况 ====")
cur.execute("SELECT content FROM minds WHERE id = ?", (TARGET_MIND_ID,)); row = cur.fetchone()
if not row: print("找不到这个 mind_id:", TARGET_MIND_ID)
else:
    content = row[0]
    if not content: print("content 为空")
    else:
        data = json.loads(content.replace("export default ", "").strip())
        meta = data.get("metadata", {}) or {}
        vp, vrt = meta.get("voice_prompt"), meta.get("voice_reference_text")
        print("voice_prompt 长度:", len(vp) if vp else 0)
        print("voice_reference_text 长度:", len(vrt) if vrt else 0)
conn.close()