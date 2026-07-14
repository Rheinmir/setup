package mount

// CRUD mount + nút SYNC (đẩy NGUYÊN CỤM folder lên remote).
//
// Danh sách mount lưu ở FILE `<data>/mounts.json` — không phải bảng SQL:
// nó là cấu hình local của MÁY NÀY (đường dẫn máy A vô nghĩa với máy B), và file-first thì
// người dùng đọc/sửa/xoá tay được. Cộng dồn: mỗi lần thêm là APPEND, không thay thế.

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	"github.com/labstack/echo/v5"

	"github.com/Rheinmir/lume/internal/remotesync"
	"github.com/Rheinmir/lume/store/file"
)

type mountCfg struct {
	Name string `json:"name"`
	Root string `json:"root"`
}

type mountView struct {
	Name  string `json:"name"`
	Root  string `json:"root"`
	Files int    `json:"files"`
}

var nameOK = regexp.MustCompile(`^[a-z0-9][a-z0-9-]{0,31}$`)

func (s *Service) cfgPath() string { return filepath.Join(s.Profile.Data, "mounts.json") }

func (s *Service) loadCfg() ([]mountCfg, error) {
	raw, err := os.ReadFile(s.cfgPath())
	if os.IsNotExist(err) {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	var out []mountCfg
	return out, json.Unmarshal(raw, &out)
}

func (s *Service) saveCfg(list []mountCfg) error {
	raw, err := json.MarshalIndent(list, "", "  ")
	if err != nil {
		return err
	}
	tmp := s.cfgPath() + ".tmp"
	if err := os.WriteFile(tmp, raw, 0o644); err != nil {
		return err
	}
	return os.Rename(tmp, s.cfgPath())
}

// GET /api/v1/mounts — danh sách folder đang xem (cộng dồn).
func (s *Service) listMounts(c *echo.Context) error {
	if _, err := s.adminID(c); err != nil { // PHANH 4
		return err
	}
	out := []mountView{}
	for _, m := range s.Store.Mounts() {
		out = append(out, mountView{Name: m.Name, Root: m.Root, Files: len(m.UIDs())})
	}
	return c.JSON(http.StatusOK, out)
}

// POST /api/v1/mounts {name, root} — THÊM một folder vào danh sách view (append, không thay thế).
func (s *Service) createMount(c *echo.Context) error {
	if err := s.loopbackOnly(); err != nil {
		return err
	}
	var req mountCfg
	if err := c.Bind(&req); err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "body sai")
	}
	root, err := s.resolveInsideRoot(req.Root) // phanh 2: whitelist + symlink
	if err != nil {
		return err
	}
	if req.Name == "" {
		req.Name = strings.ToLower(filepath.Base(root))
	}
	if !nameOK.MatchString(req.Name) {
		return echo.NewHTTPError(http.StatusBadRequest, "tên chỉ gồm a-z 0-9 và dấu -")
	}

	for _, m := range s.Store.Mounts() {
		if m.Name == req.Name {
			return echo.NewHTTPError(http.StatusConflict, "đã có folder tên «"+req.Name+"»")
		}
		// Lồng nhau ⇒ CÙNG MỘT FILE nằm trong 2 mount ⇒ 2 uid khác nhau cho một file ⇒ memo trùng.
		if root == m.Root || strings.HasPrefix(root, m.Root+string(os.PathSeparator)) ||
			strings.HasPrefix(m.Root, root+string(os.PathSeparator)) {
			return echo.NewHTTPError(http.StatusConflict,
				"folder này lồng với «"+m.Name+"» ("+m.Root+") → cùng một file sẽ thành 2 memo")
		}
	}
	// Mount kho của CHÍNH MÌNH vào mình = vòng lặp (memo đẻ file, file đẻ memo).
	if dataReal, err := filepath.EvalSymlinks(s.Profile.Data); err == nil {
		if root == dataReal || strings.HasPrefix(root, dataReal+string(os.PathSeparator)) {
			return echo.NewHTTPError(http.StatusBadRequest, "không thể mount thư mục dữ liệu của chính Lume")
		}
	}

	m := file.NewMount(req.Name, root)
	res, err := m.Scan()
	if err != nil {
		return echo.NewHTTPError(http.StatusBadRequest, "quét thư mục lỗi: "+err.Error())
	}
	if len(res.UIDs) == 0 {
		// Chống chọn nhầm chỗ một cách tự nhiên: không có .md thì thêm vào cũng vô nghĩa.
		return echo.NewHTTPError(http.StatusBadRequest, "thư mục này không có file .md nào")
	}

	userID, err := s.adminID(c)
	if err != nil {
		return err
	}
	s.Store.AttachMount(m)
	if _, _, err := s.Store.SyncMount(c.Request().Context(), m, userID); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "gắn folder lỗi: "+err.Error())
	}
	if err := s.Store.WatchMount(c.Request().Context(), m, userID); err != nil {
		// Không chết: memo vẫn hiện, chỉ là file đổi sẽ không tự cập nhật. Nói thật cho user biết.
		c.Logger().Warn("watcher không bật được: " + err.Error())
	}

	cfg, _ := s.loadCfg()
	cfg = append(cfg, mountCfg{Name: req.Name, Root: root}) // APPEND — cộng dồn
	if err := s.saveCfg(cfg); err != nil {
		return echo.NewHTTPError(http.StatusInternalServerError, "lưu danh sách folder lỗi: "+err.Error())
	}
	return c.JSON(http.StatusOK, mountView{Name: req.Name, Root: root, Files: len(res.UIDs)})
}

// DELETE /api/v1/mounts/:name — bỏ folder khỏi danh sách view. KHÔNG đụng file trên đĩa.
func (s *Service) deleteMount(c *echo.Context) error {
	if _, err := s.adminID(c); err != nil { // PHANH 4
		return err
	}
	name := c.Param("name")
	if !s.Store.DetachMount(name) {
		return echo.NewHTTPError(http.StatusNotFound, "không có folder tên «"+name+"»")
	}
	cfg, _ := s.loadCfg()
	out := cfg[:0]
	for _, m := range cfg {
		if m.Name != name {
			out = append(out, m)
		}
	}
	_ = s.saveCfg(out)
	return c.JSON(http.StatusOK, map[string]string{"removed": name})
}

type syncReq struct {
	Remote string `json:"remote"`
	Token  string `json:"token"`
	DryRun bool   `json:"dryRun"`
}

// POST /api/v1/mounts/:name:sync — NÚT SYNC: đẩy NGUYÊN CỤM folder này lên remote.
// Thủ công (người bấm), idempotent (bấm 2 lần không đẻ bản trùng — sổ sync-state.json).
func (s *Service) syncMount(c *echo.Context) error {
	if _, err := s.adminID(c); err != nil { // PHANH 4
		return err
	}
	name := c.Param("name")
	m := s.Store.MountByName(name)
	if m == nil {
		return echo.NewHTTPError(http.StatusNotFound, "không có folder tên «"+name+"»")
	}
	var req syncReq
	if err := c.Bind(&req); err != nil || req.Remote == "" {
		return echo.NewHTTPError(http.StatusBadRequest, "thiếu `remote`")
	}
	if req.Token == "" {
		req.Token = os.Getenv("LUME_TOKEN")
	}
	if req.Token == "" && !req.DryRun {
		return echo.NewHTTPError(http.StatusBadRequest, "thiếu token của remote")
	}

	var memos []remotesync.Memo
	for _, mm := range s.Store.MemosOfMount(m) {
		memos = append(memos, remotesync.Memo{UID: mm.UID, Content: mm.Content, Visibility: "PRIVATE"})
	}
	cli := remotesync.New(req.Remote, req.Token, s.Profile.Data)
	res, err := cli.Push(memos, req.DryRun)
	if err != nil {
		return echo.NewHTTPError(http.StatusBadGateway, "sync lỗi: "+err.Error())
	}
	return c.JSON(http.StatusOK, map[string]any{
		"total": len(memos), "created": res.Created, "updated": res.Updated,
		"skipped": res.Skipped, "failed": res.Failed, "dryRun": req.DryRun,
	})
}
