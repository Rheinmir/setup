package file

// MOUNT — gắn một thư mục CÓ SẴN trên máy (vd llmwiki/wiki/) làm NGUỒN ĐỌC của Lume (frame-n06).
//
// Khác `Store` (kho memo của Lume, đọc-ghi): mount là **READ-ONLY**. DB chỉ giữ INDEX
// (uid/thời gian/tag) — **không lưu nội dung, không lưu đường dẫn**. Nội dung đọc THẲNG từ file gốc
// tại chỗ mỗi lần cần ⇒ **không có bản thứ hai để lệch**, và Lume **không bao giờ ghi** vào kho
// tri thức (nơi có git + harness + rule).
//
// Bản đồ uid↔relpath sống trong RAM, dựng lại bằng một lần Scan lúc boot (201 file ≈ vài ms).

import (
	"crypto/sha1"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"sync"
)

// ErrReadOnly — mọi ý đồ ghi/xoá vào file thuộc mount đều bị chặn TẠI TẦNG STORE.
// Ẩn nút trên UI là chưa đủ: API/gRPC vẫn gọi thẳng store được.
var ErrReadOnly = fmt.Errorf("nguồn mount là READ-ONLY: Lume không ghi vào kho tri thức (sửa file gốc bằng editor)")

type Mount struct {
	Name string // tên logic, vd "wiki" → tag gốc
	Root string // thư mục thật trên máy

	mu     sync.RWMutex
	byUID  map[string]string // uid → relpath
	byPath map[string]string // relpath → uid (bắt va chạm uid)
}

func NewMount(name, root string) *Mount {
	return &Mount{Name: name, Root: root,
		byUID: map[string]string{}, byPath: map[string]string{}}
}

// UIDFor — uid TẤT ĐỊNH theo relpath: chạy lại bao nhiêu lần cũng ra một uid.
// Không dùng inode/hash-nội-dung: sửa nội dung KHÔNG được đẻ ra memo mới.
// Dạng: <name>-<12 hex của sha1(relpath)> — ngắn, khớp UIDMatcher, và **không thể va chạm âm thầm**
// theo kiểu slug (`a/b.md` vs `a-b.md` slug ra cùng chuỗi — lỗi im lặng nuốt mất một file).
func (m *Mount) UIDFor(rel string) string {
	sum := sha1.Sum([]byte(rel))
	return m.Name + "-" + hex.EncodeToString(sum[:])[:12]
}

// TagsFor — ĐƯỜNG DẪN THƯ MỤC = TAG. `concepts/okf.md` → ["wiki","concepts"].
// Lọc theo tag trong app = duyệt cây thư mục ngoài đĩa.
func (m *Mount) TagsFor(rel string) []string {
	tags := []string{m.Name}
	for _, seg := range strings.Split(filepath.Dir(rel), string(os.PathSeparator)) {
		if seg != "" && seg != "." {
			tags = append(tags, seg)
		}
	}
	return tags
}

// ScanResult — kết quả một lần quét. `Collisions` không được im lặng: uid đụng nhau = MẤT FILE.
type ScanResult struct {
	UIDs       []string
	Collisions []string
}

// Scan quét cây thư mục, dựng lại bản đồ uid↔relpath.
// Bỏ qua: file ẩn, thư mục .git, file không phải .md.
func (m *Mount) Scan() (ScanResult, error) {
	res := ScanResult{}
	byUID := map[string]string{}
	byPath := map[string]string{}

	err := filepath.WalkDir(m.Root, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		name := d.Name()
		if d.IsDir() {
			if strings.HasPrefix(name, ".") && p != m.Root {
				return filepath.SkipDir
			}
			return nil
		}
		if strings.HasPrefix(name, ".") || !strings.HasSuffix(name, ".md") {
			return nil
		}
		rel, err := filepath.Rel(m.Root, p)
		if err != nil {
			return err
		}
		uid := m.UIDFor(rel)
		if other, dup := byUID[uid]; dup && other != rel {
			res.Collisions = append(res.Collisions, rel+" ⇄ "+other)
			return nil
		}
		byUID[uid] = rel
		byPath[rel] = uid
		res.UIDs = append(res.UIDs, uid)
		return nil
	})
	if err != nil {
		return res, err
	}

	// PHANH (ghép từ PA-A): quét ra 0 file KHÔNG có nghĩa "mọi thứ đã bị xoá" — nhiều khả năng
	// hơn là mount chưa gắn / trỏ sai / ổ chưa sẵn sàng. Giữ nguyên bản đồ cũ, để người gọi biết.
	if len(res.UIDs) == 0 && len(m.byUID) > 0 {
		return res, fmt.Errorf("mount %q quét ra 0 file trong khi trước đó có %d — nghi mount chưa gắn/trỏ sai, KHÔNG dọn index", m.Name, len(m.byUID))
	}

	m.mu.Lock()
	m.byUID, m.byPath = byUID, byPath
	m.mu.Unlock()
	return res, nil
}

// Has — uid này có thuộc mount không (dùng để chặn ghi).
func (m *Mount) Has(uid string) bool {
	m.mu.RLock()
	defer m.mu.RUnlock()
	_, ok := m.byUID[uid]
	return ok
}

func (m *Mount) RelPath(uid string) (string, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	rel, ok := m.byUID[uid]
	return rel, ok
}

// UIDForPath — tra ngược, cho watcher (file đổi → uid nào).
func (m *Mount) UIDForPath(rel string) (string, bool) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	uid, ok := m.byPath[rel]
	return uid, ok
}

// Read — ĐỌC THẲNG TỪ FILE GỐC, ngay lúc gọi. Đây là chỗ "stream" thật sự: không cache, không copy
// ⇒ sửa file bằng vim thì lần đọc kế tiếp đã ra bản mới.
// Frontmatter (OKF của wiki) bị cắt bằng `split()` — UI chỉ thấy body sạch, không phơi YAML.
func (m *Mount) Read(uid string) (string, bool, error) {
	rel, ok := m.RelPath(uid)
	if !ok {
		return "", false, nil
	}
	raw, err := os.ReadFile(filepath.Join(m.Root, rel))
	if os.IsNotExist(err) {
		return "", false, nil
	}
	if err != nil {
		return "", false, err
	}
	_, body := split(string(raw))
	return body, true, nil
}

// ModTime — mtime file, dùng làm created/updated cho index (file wiki không có ts của memos).
func (m *Mount) ModTime(uid string) (int64, bool) {
	rel, ok := m.RelPath(uid)
	if !ok {
		return 0, false
	}
	st, err := os.Stat(filepath.Join(m.Root, rel))
	if err != nil {
		return 0, false
	}
	return st.ModTime().Unix(), true
}

// Attach cho Store biết có mount — Read của Store sẽ hỏi mount trước.
func (s *Store) Attach(m *Mount) {
	s.mounts = append(s.mounts, m)
}

// Mounted — uid thuộc mount nào không (Store dùng để chặn ghi/xoá).
func (s *Store) Mounted(uid string) bool {
	for _, m := range s.mounts {
		if m.Has(uid) {
			return true
		}
	}
	return false
}

// Mounts trả các mount đang gắn (runner cần để quét/watch).
func (s *Store) Mounts() []*Mount { return s.mounts }
