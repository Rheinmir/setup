// Package file — LƯU TRỮ FILE-FIRST cho Lume (frame-n04).
//
// NGUỒN CHÂN LÝ của NỘI DUNG memo là file `.md` trên đĩa (YAML frontmatter + body),
// người đọc/sửa/grep/backup/đưa vào git được. SQL chỉ còn là **INDEX** (id, uid, thời gian,
// visibility, quan hệ) để truy vấn/lọc nhanh.
//
// VÌ SAO KHÔNG viết hẳn một store.Driver file:
//   `store.Driver` là interface KHỔNG LỒ và khoá cứng vào SQL (`GetDB() *sql.DB` + migrator SQL).
//   Viết driver file = rewrite cả tầng store + bỏ toàn bộ filter SQL đang chạy → rủi ro rất lớn,
//   đổi lại rất ít giá trị (lọc/tìm kiếm phải tự cài lại từ đầu).
//   ⇒ Chọn: NỘI DUNG ra file (thứ người dùng thật sự sở hữu), METADATA giữ trong SQL làm index.
//   Mất DB vẫn dựng lại được từ .md; mất .md thì mất nội dung → nên .md mới là chân lý.
//
// Bất biến: ghi memo ⇒ PHẢI có file .md. Đọc memo ⇒ nội dung LẤY TỪ FILE (file thắng DB).
package file

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

// Store ghi/đọc nội dung memo dưới dạng .md trong một thư mục.
// `mounts` = các thư mục NGOÀI (vd llmwiki/wiki) gắn vào để ĐỌC — read-only, xem mount.go.
type Store struct {
	Dir    string
	mounts []*Mount
}

func New(dir string) (*Store, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, fmt.Errorf("tạo thư mục memo .md: %w", err)
	}
	return &Store{Dir: dir}, nil
}

var uidSafe = regexp.MustCompile(`[^a-zA-Z0-9_-]`)

// path — tên file suy ra TẤT ĐỊNH từ uid (không đoán, không tra DB).
func (s *Store) path(uid string) string {
	return filepath.Join(s.Dir, uidSafe.ReplaceAllString(uid, "_")+".md")
}

// Meta = phần frontmatter: đủ để DỰNG LẠI index nếu mất DB.
type Meta struct {
	ID         int32
	UID        string
	CreatorID  int32
	CreatedTs  int64
	UpdatedTs  int64
	Visibility string
	RowStatus  string
}

// Write ghi 1 memo thành .md (frontmatter + body). Ghi ATOMIC: viết file tạm rồi rename,
// để tiến trình chết giữa chừng không để lại file cụt.
func (s *Store) Write(m Meta, content string) error {
	// CHẶN CỨNG: uid thuộc mount (llmwiki) ⇒ KHÔNG BAO GIỜ ghi. Kho tri thức là git repo có
	// harness/rule/ledger — app note không có quyền ghi vào đó. Chặn ở TẦNG STORE, vì ẩn nút
	// trên UI là vô nghĩa: API/gRPC gọi thẳng store được.
	if s.Mounted(m.UID) {
		return ErrReadOnly
	}
	var b strings.Builder
	b.WriteString("---\n")
	fmt.Fprintf(&b, "id: %d\n", m.ID)
	fmt.Fprintf(&b, "uid: %s\n", m.UID)
	fmt.Fprintf(&b, "creator_id: %d\n", m.CreatorID)
	fmt.Fprintf(&b, "created_ts: %d\n", m.CreatedTs)
	fmt.Fprintf(&b, "updated_ts: %d\n", m.UpdatedTs)
	fmt.Fprintf(&b, "visibility: %s\n", m.Visibility)
	fmt.Fprintf(&b, "row_status: %s\n", m.RowStatus)
	fmt.Fprintf(&b, "# ĐỌC ĐƯỢC: file này là NGUỒN CHÂN LÝ của memo. Sửa tay được. DB chỉ là index.\n")
	b.WriteString("---\n")
	b.WriteString(content)

	tmp := s.path(m.UID) + ".tmp"
	if err := os.WriteFile(tmp, []byte(b.String()), 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, s.path(m.UID))
}

// Read đọc nội dung (phần sau frontmatter). Không có file → (", false, nil) — người gọi
// tự quyết fallback về DB (memo cũ tạo trước khi bật file-first).
func (s *Store) Read(uid string) (string, bool, error) {
	// MOUNT TRƯỚC: uid thuộc thư mục gắn ngoài (llmwiki) → đọc thẳng file gốc tại chỗ.
	for _, m := range s.mounts {
		if body, ok, err := m.Read(uid); err != nil || ok {
			return body, ok, err
		}
	}
	raw, err := os.ReadFile(s.path(uid))
	if os.IsNotExist(err) {
		return "", false, nil
	}
	if err != nil {
		return "", false, err
	}
	_, body := split(string(raw))
	return body, true, nil
}

// ReadMeta đọc frontmatter — dùng để DỰNG LẠI index từ .md khi mất DB.
func (s *Store) ReadMeta(uid string) (Meta, string, bool, error) {
	raw, err := os.ReadFile(s.path(uid))
	if os.IsNotExist(err) {
		return Meta{}, "", false, nil
	}
	if err != nil {
		return Meta{}, "", false, err
	}
	head, body := split(string(raw))
	m := Meta{}
	for _, line := range strings.Split(head, "\n") {
		k, v, ok := strings.Cut(line, ":")
		if !ok || strings.HasPrefix(strings.TrimSpace(k), "#") {
			continue
		}
		k, v = strings.TrimSpace(k), strings.TrimSpace(v)
		switch k {
		case "id":
			n, _ := strconv.Atoi(v)
			m.ID = int32(n)
		case "uid":
			m.UID = v
		case "creator_id":
			n, _ := strconv.Atoi(v)
			m.CreatorID = int32(n)
		case "created_ts":
			m.CreatedTs, _ = strconv.ParseInt(v, 10, 64)
		case "updated_ts":
			m.UpdatedTs, _ = strconv.ParseInt(v, 10, 64)
		case "visibility":
			m.Visibility = v
		case "row_status":
			m.RowStatus = v
		}
	}
	return m, body, true, nil
}

// Delete xoá file memo. Không có file cũng coi là thành công (idempotent).
func (s *Store) Delete(uid string) error {
	if s.Mounted(uid) {
		return ErrReadOnly // xoá memo wiki trong UI KHÔNG được xoá file thật ngoài đĩa
	}
	err := os.Remove(s.path(uid))
	if os.IsNotExist(err) {
		return nil
	}
	return err
}

// List liệt kê uid của mọi memo có trên đĩa (nguồn chân lý), không hỏi DB.
func (s *Store) List() ([]string, error) {
	entries, err := os.ReadDir(s.Dir)
	if err != nil {
		return nil, err
	}
	var uids []string
	for _, e := range entries {
		if e.IsDir() || !strings.HasSuffix(e.Name(), ".md") {
			continue
		}
		if _, body, ok, err := s.ReadMeta(strings.TrimSuffix(e.Name(), ".md")); err == nil && ok && body != "" {
			uids = append(uids, strings.TrimSuffix(e.Name(), ".md"))
		}
	}
	return uids, nil
}

// split tách frontmatter khỏi body. Không có frontmatter → toàn bộ là body (file người dùng
// tự tạo tay vẫn đọc được — file-first nghĩa là con người được quyền sửa tay).
func split(raw string) (head, body string) {
	if !strings.HasPrefix(raw, "---\n") {
		return "", raw
	}
	rest := raw[4:]
	i := strings.Index(rest, "\n---\n")
	if i < 0 {
		return "", raw
	}
	return rest[:i], rest[i+5:]
}

// Now — tiện cho caller khi cần dấu thời gian nhất quán.
func Now() int64 { return time.Now().Unix() }
