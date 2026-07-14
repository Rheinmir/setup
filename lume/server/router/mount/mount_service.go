// Package mount — API cho tính năng "bấm nút, chọn folder, thêm vào danh sách view" (frame-n08).
//
// ⚠️ ĐÂY LÀ API ĐỌC FILESYSTEM CỦA MÁY NGƯỜI DÙNG. Nó tồn tại được CHỈ VÌ 4 phanh dưới đây.
// Thiếu MỘT trong 4 ⇒ đây là máy quét ổ cứng miễn phí cho mọi tab trình duyệt đang mở
// (bất kỳ trang web nào cũng fetch được http://localhost:5230).
//
//  1. CHỈ LOOPBACK: server bind ra ngoài (0.0.0.0 / LAN) ⇒ TỪ CHỐI thẳng. Không có cờ mở.
//  2. WHITELIST GỐC: chỉ duyệt/mount trong $HOME (mở thêm bằng --browse-root). Ngoài ⇒ từ chối,
//     kể cả khi client gửi đường dẫn tuyệt đối. Resolve symlink TRƯỚC khi so (symlink là cách
//     kinh điển để trỏ ra khỏi whitelist).
//  3. CHỈ TRẢ THƯ MỤC, không trả nội dung file, không trả size/mtime (tên thư mục thôi đã lộ
//     nhiều: ~/Projects/acme-acquisition).
//  4. CẦN ĐĂNG NHẬP (admin). Không chấp nhận request ẩn danh.
package mount

import (
	"net"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"github.com/labstack/echo/v5"

	"github.com/Rheinmir/lume/internal/profile"
	"github.com/Rheinmir/lume/store"
)

type Service struct {
	Profile *profile.Profile
	Store   *store.Store
	auth    Authenticator
	// BrowseRoots — các gốc được phép duyệt/mount. Mặc định [$HOME].
	BrowseRoots []string
}

func NewService(p *profile.Profile, s *store.Store) *Service {
	roots := []string{}
	if home, err := os.UserHomeDir(); err == nil {
		roots = append(roots, home)
	}
	return &Service{Profile: p, Store: s, BrowseRoots: roots}
}

// PHANH 1 — chỉ chạy khi server nghe ở loopback. Bind ra LAN mà vẫn cho duyệt ổ cứng
// = người cùng wifi đọc được cây thư mục của user. Không đánh đổi cái này lấy tiện lợi.
func (s *Service) loopbackOnly() error {
	addr := s.Profile.Addr
	if addr == "" || addr == "localhost" {
		return nil // memos mặc định bind localhost
	}
	ip := net.ParseIP(addr)
	if ip != nil && ip.IsLoopback() {
		return nil
	}
	return echo.NewHTTPError(http.StatusForbidden,
		"API duyệt thư mục BỊ TẮT khi server bind ra ngoài loopback (--addr="+addr+"): "+
			"người cùng mạng sẽ đọc được cây thư mục của bạn")
}

// PHANH 2 — resolve symlink rồi ép nằm trong whitelist.
func (s *Service) resolveInsideRoot(p string) (string, error) {
	if p == "" {
		if len(s.BrowseRoots) == 0 {
			return "", echo.NewHTTPError(http.StatusForbidden, "không có gốc nào được phép duyệt")
		}
		return s.BrowseRoots[0], nil
	}
	if !filepath.IsAbs(p) {
		return "", echo.NewHTTPError(http.StatusBadRequest, "đường dẫn phải tuyệt đối")
	}
	clean := filepath.Clean(p)
	real, err := filepath.EvalSymlinks(clean) // symlink có thể trỏ RA NGOÀI whitelist
	if err != nil {
		return "", echo.NewHTTPError(http.StatusBadRequest, "đường dẫn không tồn tại: "+clean)
	}
	for _, root := range s.BrowseRoots {
		rootReal, err := filepath.EvalSymlinks(root)
		if err != nil {
			continue
		}
		if real == rootReal || strings.HasPrefix(real, rootReal+string(os.PathSeparator)) {
			return real, nil
		}
	}
	// Cẩn thận: cả HAI vế phải resolve symlink rồi mới so. macOS có /var → /private/var, /tmp →
	// /private/tmp: so chuỗi thô là chặn nhầm chính thư mục hợp lệ (hoặc tệ hơn — cho lọt cái sai).
	return "", echo.NewHTTPError(http.StatusForbidden,
		"ngoài phạm vi cho phép (chỉ được duyệt trong "+strings.Join(s.BrowseRoots, ", ")+")")
}

type dirEntry struct {
	Name        string `json:"name"`
	Path        string `json:"path"`
	HasMarkdown bool   `json:"hasMarkdown"` // để user biết thư mục nào đáng chọn
}

type listResp struct {
	Path      string     `json:"path"`
	Parent    string     `json:"parent"`
	Entries   []dirEntry `json:"entries"`
	Truncated bool       `json:"truncated"`
}

const maxEntries = 500 // thư mục 100k entry → đừng bốc hết vào RAM rồi nhồi xuống browser

// GET /api/v1/filesystem:list?path=... — CHỈ trả THƯ MỤC (phanh 3).
func (s *Service) listDir(c *echo.Context) error {
	if err := s.loopbackOnly(); err != nil {
		return err
	}
	if _, err := s.adminID(c); err != nil { // PHANH 4
		return err
	}
	dir, err := s.resolveInsideRoot(c.QueryParam("path"))
	if err != nil {
		return err
	}
	st, err := os.Stat(dir)
	if err != nil || !st.IsDir() {
		return echo.NewHTTPError(http.StatusBadRequest, "không phải thư mục")
	}

	items, err := os.ReadDir(dir)
	if err != nil {
		return echo.NewHTTPError(http.StatusForbidden, "không đọc được thư mục (thiếu quyền?)")
	}
	resp := listResp{Path: dir}
	if p, err := s.resolveInsideRoot(filepath.Dir(dir)); err == nil && p != dir {
		resp.Parent = p // rỗng khi đã ở gốc whitelist → UI không cho đi lên nữa
	}
	for _, it := range items {
		if len(resp.Entries) >= maxEntries {
			resp.Truncated = true
			break
		}
		if !it.IsDir() || strings.HasPrefix(it.Name(), ".") {
			continue // chỉ thư mục, bỏ dotfile (phanh 3)
		}
		full := filepath.Join(dir, it.Name())
		resp.Entries = append(resp.Entries, dirEntry{
			Name: it.Name(), Path: full, HasMarkdown: hasMarkdown(full),
		})
	}
	sort.Slice(resp.Entries, func(i, j int) bool { return resp.Entries[i].Name < resp.Entries[j].Name })
	return c.JSON(http.StatusOK, resp)
}

// hasMarkdown — có .md ngay trong 1 tầng không (không đệ quy: chỉ để gợi ý, đừng quét cả ổ).
func hasMarkdown(dir string) bool {
	items, err := os.ReadDir(dir)
	if err != nil {
		return false
	}
	for _, it := range items {
		if !it.IsDir() && strings.HasSuffix(it.Name(), ".md") {
			return true
		}
	}
	return false
}
