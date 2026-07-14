package mount

import (
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/Rheinmir/lume/internal/profile"
)

// 7 bất biến AN TOÀN của API duyệt thư mục (frame-n08).
// Đây là API đọc filesystem của máy user — đỏ một cái là mở toang ổ cứng cho mọi tab trình duyệt.
func TestGuards(t *testing.T) {
	home, _ := filepath.EvalSymlinks(t.TempDir()) // macOS: /var → /private/var
	inside := filepath.Join(home, "notes")
	if err := os.MkdirAll(inside, 0o755); err != nil {
		t.Fatal(err)
	}
	outside, _ := filepath.EvalSymlinks(t.TempDir()) // ngoài whitelist

	s := &Service{Profile: &profile.Profile{Data: filepath.Join(home, "data")}, BrowseRoots: []string{home}}

	// ① Trong whitelist → OK.
	if got, err := s.resolveInsideRoot(inside); err != nil || got != inside {
		t.Fatalf("đường dẫn hợp lệ bị chặn: %v %v", got, err)
	}

	// ② Ngoài whitelist → CHẶN (dù là path tuyệt đối hợp lệ).
	if _, err := s.resolveInsideRoot(outside); err == nil {
		t.Fatal("đường dẫn NGOÀI $HOME phải bị chặn — không thì client duyệt được cả ổ")
	}
	if _, err := s.resolveInsideRoot("/etc"); err == nil {
		t.Fatal("/etc phải bị chặn")
	}

	// ③ Path tương đối → chặn (chống ../../ và mọi trò đoán vị trí).
	if _, err := s.resolveInsideRoot("../../etc"); err == nil {
		t.Fatal("path tương đối phải bị chặn")
	}

	// ④ SYMLINK trỏ RA NGOÀI whitelist → chặn (resolve TRƯỚC khi so; đây là cách kinh điển
	//    để lách whitelist: tạo ~/link → /).
	link := filepath.Join(home, "escape")
	if err := os.Symlink(outside, link); err != nil {
		t.Skip("hệ thống không tạo được symlink")
	}
	if _, err := s.resolveInsideRoot(link); err == nil {
		t.Fatal("symlink trỏ ra ngoài whitelist phải bị chặn")
	}

	// ⑤ PHANH LOOPBACK: bind ra ngoài ⇒ API duyệt thư mục TẮT.
	s.Profile.Addr = "0.0.0.0"
	if err := s.loopbackOnly(); err == nil {
		t.Fatal("bind 0.0.0.0 mà vẫn cho duyệt thư mục ⇒ người cùng wifi đọc được ổ cứng")
	}
	s.Profile.Addr = "127.0.0.1"
	if err := s.loopbackOnly(); err != nil {
		t.Fatalf("loopback phải cho phép: %v", err)
	}
	s.Profile.Addr = ""
	if err := s.loopbackOnly(); err != nil {
		t.Fatalf("mặc định (localhost) phải cho phép: %v", err)
	}

	// ⑥ hasMarkdown — chống chọn nhầm thư mục không có .md.
	if hasMarkdown(inside) {
		t.Fatal("thư mục rỗng mà báo có .md")
	}
	if err := os.WriteFile(filepath.Join(inside, "a.md"), []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	if !hasMarkdown(inside) {
		t.Fatal("có .md mà không nhận ra")
	}

	// ⑦ Tên mount: chỉ a-z 0-9 và dấu - (nó thành tag gốc + prefix uid).
	for _, bad := range []string{"", "Có Dấu", "a/b", strings.Repeat("x", 40)} {
		if nameOK.MatchString(bad) {
			t.Fatalf("tên xấu %q phải bị từ chối", bad)
		}
	}
	if !nameOK.MatchString("wiki-2") {
		t.Fatal("tên hợp lệ bị từ chối")
	}
}
