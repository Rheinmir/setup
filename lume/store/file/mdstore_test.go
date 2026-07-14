package file

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// Bất biến file-first — nếu một trong các test này đỏ thì "nguồn chân lý" không còn là file.
func TestMdStore(t *testing.T) {
	dir := t.TempDir()
	s, err := New(filepath.Join(dir, "memos-md"))
	if err != nil {
		t.Fatal(err)
	}
	meta := Meta{ID: 7, UID: "abc123", CreatorID: 1, CreatedTs: 100, UpdatedTs: 200,
		Visibility: "PRIVATE", RowStatus: "NORMAL"}

	// ① GHI ⇒ có file .md thật trên đĩa, người đọc được.
	if err := s.Write(meta, "nội dung **markdown**\ndòng 2"); err != nil {
		t.Fatal(err)
	}
	raw, err := os.ReadFile(filepath.Join(dir, "memos-md", "abc123.md"))
	if err != nil {
		t.Fatalf("ghi memo mà KHÔNG có file .md — file-first hỏng: %v", err)
	}
	if !strings.Contains(string(raw), "uid: abc123") || !strings.Contains(string(raw), "dòng 2") {
		t.Fatalf("file thiếu frontmatter hoặc body:\n%s", raw)
	}

	// ② ĐỌC round-trip lossless (nội dung ra đúng như vào).
	body, ok, err := s.Read("abc123")
	if err != nil || !ok {
		t.Fatalf("đọc lại không được: ok=%v err=%v", ok, err)
	}
	if body != "nội dung **markdown**\ndòng 2" {
		t.Fatalf("round-trip MẤT DỮ LIỆU: %q", body)
	}

	// ③ Frontmatter dựng lại được index nếu mất DB.
	m2, _, ok, err := s.ReadMeta("abc123")
	if err != nil || !ok {
		t.Fatal(err)
	}
	if m2.ID != 7 || m2.UID != "abc123" || m2.CreatedTs != 100 || m2.Visibility != "PRIVATE" {
		t.Fatalf("frontmatter không dựng lại được record: %+v", m2)
	}

	// ④ SỬA TAY file → đọc phải thấy bản sửa tay (cốt lõi của file-first).
	if err := os.WriteFile(filepath.Join(dir, "memos-md", "abc123.md"), []byte("người sửa tay"), 0o644); err != nil {
		t.Fatal(err)
	}
	body, ok, _ = s.Read("abc123")
	if !ok || body != "người sửa tay" {
		t.Fatalf("sửa tay file mà đọc không ra — file KHÔNG phải nguồn chân lý: %q", body)
	}

	// ⑤ List = liệt kê từ ĐĨA, không hỏi DB.
	if uids, err := s.List(); err != nil || len(uids) != 1 || uids[0] != "abc123" {
		t.Fatalf("List() từ đĩa sai: %v %v", uids, err)
	}

	// ⑥ Xoá ⇒ file biến mất; xoá lần 2 vẫn OK (idempotent).
	if err := s.Delete("abc123"); err != nil {
		t.Fatal(err)
	}
	if _, ok, _ := s.Read("abc123"); ok {
		t.Fatal("xoá memo mà file .md còn — file mồ côi")
	}
	if err := s.Delete("abc123"); err != nil {
		t.Fatalf("xoá 2 lần phải idempotent: %v", err)
	}

	// ⑦ uid độc hại không được thoát khỏi thư mục.
	if got := s.path("../../etc/passwd"); strings.Contains(got, "..") {
		t.Fatalf("path traversal: %s", got)
	}
}
