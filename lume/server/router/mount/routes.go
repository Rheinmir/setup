package mount

// Đăng ký route + PHANH 4: BẮT BUỘC ĐĂNG NHẬP (admin) + CHỐT CSRF.
//
// Vì sao cần chốt CSRF riêng: bất kỳ trang web nào đang mở trong trình duyệt cũng
// `fetch("http://localhost:5230/api/v1/filesystem:list")` được, và trình duyệt TỰ ĐÍNH KÈM cookie
// ⇒ một tab quảng cáo cũng liệt kê được ổ cứng của bạn.
//
// Cấm cookie hoàn toàn thì SPA của chính Lume cũng chết (token là httpOnly, JS không đọc được).
// ⇒ Cho phép cookie, NHƯNG bắt buộc header tuỳ biến `X-Lume-Mount: 1`:
// trình duyệt KHÔNG cho trang khác origin gửi header tuỳ biến nếu không qua CORS preflight,
// mà CORS của ta không cho origin lạ ⇒ request từ trang lạ chết ở preflight. SPA cùng origin thì gửi bình thường.

import (
	"context"
	"net/http"

	"github.com/labstack/echo/v5"

	"github.com/Rheinmir/lume/server/auth"
	"github.com/Rheinmir/lume/store"
)

// CSRFHeader — header mà chỉ code cùng origin mới gửi được.
const CSRFHeader = "X-Lume-Mount"

// Authenticator — đúng một việc: (Authorization, Cookie) → user.
type Authenticator interface {
	AuthenticateToUser(ctx context.Context, authHeader, cookieHeader string) (*store.User, error)
}

func (s *Service) RegisterRoutes(g *echo.Group, a Authenticator) {
	s.auth = a
	g.GET("/api/v1/filesystem:list", s.listDir)
	g.GET("/api/v1/mounts", s.listMounts)
	g.POST("/api/v1/mounts", s.createMount)
	g.DELETE("/api/v1/mounts/:name", s.deleteMount)
	g.POST("/api/v1/mounts/:name:sync", s.syncMount)
}

var _ = auth.AuthResult{} // giữ import auth cho rõ nguồn gốc kiểu

// adminID — PHANH 4. Chặn: thiếu chốt CSRF · chưa đăng nhập · không phải admin.
func (s *Service) adminID(c *echo.Context) (int32, error) {
	if s.auth == nil {
		return 0, echo.NewHTTPError(http.StatusInternalServerError, "authenticator chưa gắn")
	}
	if c.Request().Header.Get(CSRFHeader) == "" {
		return 0, echo.NewHTTPError(http.StatusForbidden,
			"thiếu header "+CSRFHeader+" — chống trang lạ trong trình duyệt gọi API đọc thư mục của bạn")
	}
	u, err := s.auth.AuthenticateToUser(c.Request().Context(),
		c.Request().Header.Get(echo.HeaderAuthorization),
		c.Request().Header.Get("Cookie"))
	if err != nil || u == nil {
		return 0, echo.NewHTTPError(http.StatusUnauthorized, "chưa đăng nhập")
	}
	if u.Role != store.RoleAdmin {
		return 0, echo.NewHTTPError(http.StatusForbidden, "chỉ ADMIN được gắn thư mục vào app")
	}
	return u.ID, nil
}
