package file

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func writeFile(t *testing.T, path, content string) {
	t.Helper()
	if err := os.MkdirAll(filepath.Dir(path), 0o755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(content), 0o644); err != nil {
		t.Fatal(err)
	}
}

// 7 bất biến của mount (frame-n06). Đỏ một cái = "stream llmwiki" không còn đúng.
func TestMount(t *testing.T) {
	wiki := t.TempDir()
	writeFile(t, filepath.Join(wiki, "concepts", "okf.md"),
		"---\ntype: concept\nname: okf\n---\nNội dung OKF thật.\n")
	writeFile(t, filepath.Join(wiki, "sources", "draft", "note.md"), "Ghi chú nháp.")
	writeFile(t, filepath.Join(wiki, ".git", "config"), "không được quét")
	writeFile(t, filepath.Join(wiki, "ledger.jsonl"), "không phải .md")

	m := NewMount("wiki", wiki)
	res, err := m.Scan()
	if err != nil {
		t.Fatal(err)
	}

	// ① Quét đúng số file .md (bỏ .git, bỏ file không .md).
	if len(res.UIDs) != 2 {
		t.Fatalf("quét sai số file: %d (phải 2) — %v", len(res.UIDs), res.UIDs)
	}
	uid, ok := m.UIDForPath(filepath.Join("concepts", "okf.md"))
	if !ok {
		t.Fatal("không tra được uid theo relpath")
	}

	// ② uid TẤT ĐỊNH: quét lại ra đúng uid cũ (không đẻ memo mới mỗi lần boot).
	if _, err := m.Scan(); err != nil {
		t.Fatal(err)
	}
	if uid2, _ := m.UIDForPath(filepath.Join("concepts", "okf.md")); uid2 != uid {
		t.Fatalf("uid KHÔNG tất định: %s ≠ %s", uid2, uid)
	}

	// ③ THƯ MỤC = TAG.
	tags := m.TagsFor(filepath.Join("sources", "draft", "note.md"))
	if strings.Join(tags, "/") != "wiki/sources/draft" {
		t.Fatalf("tag không theo cây thư mục: %v", tags)
	}

	// ④ ĐỌC THẲNG FILE GỐC + frontmatter OKF bị cắt (UI không phơi YAML).
	body, ok, err := m.Read(uid)
	if err != nil || !ok {
		t.Fatalf("đọc mount lỗi: %v", err)
	}
	if strings.Contains(body, "type: concept") {
		t.Fatalf("frontmatter OKF lọt vào body: %q", body)
	}
	if !strings.Contains(body, "Nội dung OKF thật.") {
		t.Fatalf("body sai: %q", body)
	}

	// ⑤ STREAM THẬT: sửa file ngoài đĩa → đọc lại ra bản mới (không cache, không copy).
	writeFile(t, filepath.Join(wiki, "concepts", "okf.md"),
		"---\ntype: concept\n---\nTÔI VỪA SỬA BẰNG VIM.\n")
	body, _, _ = m.Read(uid)
	if !strings.Contains(body, "TÔI VỪA SỬA BẰNG VIM.") {
		t.Fatalf("sửa file gốc mà app không thấy ⇒ KHÔNG phải stream: %q", body)
	}

	// ⑥ READ-ONLY: Store KHÔNG được ghi/xoá vào lãnh thổ wiki.
	st, err := New(filepath.Join(t.TempDir(), "memos-md"))
	if err != nil {
		t.Fatal(err)
	}
	st.Attach(m)
	if err := st.Write(Meta{UID: uid}, "app cố ghi đè file wiki"); err != ErrReadOnly {
		t.Fatalf("GHI vào mount phải bị chặn, nhận: %v", err)
	}
	if err := st.Delete(uid); err != ErrReadOnly {
		t.Fatalf("XOÁ file wiki phải bị chặn, nhận: %v", err)
	}
	// và Store.Read phải lấy được nội dung từ mount
	if b, ok, _ := st.Read(uid); !ok || !strings.Contains(b, "TÔI VỪA SỬA BẰNG VIM.") {
		t.Fatalf("Store.Read không đọc được qua mount: %q", b)
	}

	// ⑦ PHANH: quét ra 0 file (mount trỏ sai / chưa gắn) ⇒ LỖI, KHÔNG dọn sạch index.
	m.Root = filepath.Join(t.TempDir(), "khong-ton-tai-nhung-rong")
	_ = os.MkdirAll(m.Root, 0o755)
	if _, err := m.Scan(); err == nil {
		t.Fatal("quét ra 0 file mà không báo lỗi ⇒ sẽ xoá sạch index của 201 memo")
	}
	if _, ok := m.RelPath(uid); !ok {
		t.Fatal("index đã bị dọn dù quét lỗi — mất phanh")
	}
}
