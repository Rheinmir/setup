// MountFolders — "bấm nút, chọn folder, thêm vào danh sách view" (frame-n08).
//
// Vì sao có hộp thoại duyệt thư mục của riêng mình mà không dùng file-picker của trình duyệt:
// trình duyệt CỐ TÌNH không cho JS biết đường dẫn tuyệt đối. Nhưng server Lume chạy NGAY TRÊN
// máy này, nên nó duyệt hộ (API chỉ trả THƯ MỤC, chỉ trong $HOME, chỉ loopback, chỉ admin).
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronRight, CornerLeftUp, FolderPlus, FolderOpen, RefreshCw, X } from "lucide-react";

type Entry = { name: string; path: string; hasMarkdown: boolean };
type Mount = { name: string; root: string; files: number };

const api = async (path: string, init?: RequestInit) => {
  const res = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Lume-Mount": "1", ...(init?.headers || {}) },
    credentials: "include",
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body?.message || `HTTP ${res.status}`);
  return body;
};

const MountFolders = () => {
  const [mounts, setMounts] = useState<Mount[]>([]);
  const [picking, setPicking] = useState(false);
  const [dir, setDir] = useState<{ path: string; parent: string; entries: Entry[] }>();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const reload = () => api("/api/v1/mounts").then(setMounts).catch(() => {});
  useEffect(() => { reload(); }, []);

  const browse = async (path?: string) => {
    setErr("");
    try {
      setDir(await api(`/api/v1/filesystem:list${path ? `?path=${encodeURIComponent(path)}` : ""}`));
    } catch (e: any) { setErr(e.message); }
  };

  const openPicker = () => { setPicking(true); browse(); };

  const addCurrent = async () => {
    if (!dir) return;
    setBusy(true); setErr("");
    try {
      await api("/api/v1/mounts", { method: "POST", body: JSON.stringify({ root: dir.path }) });
      setPicking(false);
      await reload();
      // memo của folder vừa thêm đã nằm trong index → nạp lại feed
      window.location.reload();
    } catch (e: any) { setErr(e.message); } finally { setBusy(false); }
  };

  const sync = async (name: string) => {
    const remote = window.prompt("Đẩy NGUYÊN CỤM folder này lên remote nào?\n(vd http://localhost:5231)");
    if (!remote) return;
    const token = window.prompt("Access token của remote:");
    if (!token) return;
    setBusy(true);
    try {
      const r = await api(`/api/v1/mounts/${name}:sync`, {
        method: "POST", body: JSON.stringify({ remote, token }),
      });
      window.alert(`Đã đẩy lên ${remote}\n\n${r.total} memo · tạo ${r.created} · cập nhật ${r.updated} · bỏ qua ${r.skipped}` +
        (r.failed?.length ? `\nHỎNG ${r.failed.length}:\n${r.failed.join("\n")}` : ""));
    } catch (e: any) { window.alert("Sync lỗi: " + e.message); } finally { setBusy(false); }
  };

  const remove = async (name: string) => {
    // Nói rõ: bỏ khỏi app KHÔNG xoá file trên đĩa (nếu không user sẽ sợ không dám bấm).
    if (!window.confirm(`Bỏ «${name}» khỏi danh sách xem?\n\nFile trên đĩa KHÔNG bị xoá.`)) return;
    await api(`/api/v1/mounts/${name}`, { method: "DELETE" }).catch(() => {});
    reload();
  };

  return (
    <div className="w-full flex flex-col gap-1 mt-3">
      <div className="flex items-center justify-between px-1">
        <span className="text-sm text-muted-foreground">Thư mục</span>
        <button onClick={openPicker} title="Thêm thư mục" className="p-1 rounded-lg hover:bg-accent">
          <FolderPlus className="w-4 h-4" />
        </button>
      </div>

      {mounts.map((m) => (
        <div key={m.name} className="group flex items-center gap-2 px-2 py-1.5 rounded-xl hover:bg-accent">
          <FolderOpen className="w-4 h-4 shrink-0 opacity-70" />
          <span className="text-sm truncate" title={m.root}>{m.name}</span>
          <span className="text-xs text-muted-foreground">({m.files})</span>
          <span className="grow" />
          <button onClick={() => sync(m.name)} disabled={busy} title={`Đẩy cả cụm «${m.name}» lên remote`}
            className="opacity-0 group-hover:opacity-100 p-1 rounded-lg hover:bg-background">
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
          <button onClick={() => remove(m.name)} title="Bỏ khỏi danh sách (không xoá file)"
            className="opacity-0 group-hover:opacity-100 p-1 rounded-lg hover:bg-background">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      ))}

      {/* PORTAL ra body: hộp thoại nằm trong sidebar thì sidebar (có overflow/transform)
          tạo stacking context riêng ⇒ z-index bên trong VÔ NGHĨA ⇒ memo card đè lên. */}
      {picking && createPortal(

        <div className="fixed inset-0 z-[100] grid place-items-center bg-black/40" onClick={() => setPicking(false)}>
          <div onClick={(e) => e.stopPropagation()}
            className="relative z-[101] w-[620px] max-h-[72vh] flex flex-col gap-2 p-4 rounded-2xl bg-card shadow-2xl">
            <div className="text-sm font-medium">Chọn thư mục</div>
            <div className="text-xs text-muted-foreground break-all">{dir?.path || "…"}</div>

            <div className="flex-1 overflow-auto rounded-xl bg-background">
              {dir?.parent ? (
                <button onClick={() => browse(dir.parent)}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent">
                  <CornerLeftUp className="w-4 h-4" /> ..
                </button>
              ) : null}
              {dir?.entries.map((e) => (
                <button key={e.path} onClick={() => browse(e.path)}
                  className="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-accent">
                  <ChevronRight className="w-4 h-4 opacity-50" />
                  <span className="truncate">{e.name}</span>
                  {/* chấm = có .md ngay trong thư mục này → chỗ đáng chọn */}
                  {e.hasMarkdown && <span className="ml-1 w-1.5 h-1.5 rounded-full bg-primary" title="có file .md" />}
                </button>
              ))}
              {dir && dir.entries.length === 0 && (
                <div className="px-3 py-4 text-sm text-muted-foreground">(không có thư mục con)</div>
              )}
            </div>

            {err && <div className="text-sm text-destructive">{err}</div>}

            <div className="flex justify-end gap-2">
              <button onClick={() => setPicking(false)} className="px-3 py-1.5 text-sm rounded-xl hover:bg-accent">Huỷ</button>
              <button onClick={addCurrent} disabled={busy || !dir}
                className="px-3 py-1.5 text-sm rounded-xl bg-primary text-primary-foreground disabled:opacity-50">
                Chọn thư mục này
              </button>
            </div>
          </div>
        </div>
      , document.body)}
    </div>
  );
};

export default MountFolders;
