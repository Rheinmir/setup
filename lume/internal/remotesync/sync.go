// Package remotesync — đẩy memo LOCAL của Lume lên một instance Lume ở XA. Thủ công (frame-n07).
//
// RANH GIỚI (quan trọng, đừng phá):
//   - CHỈ đẩy memo NẰM TRONG KHO CỦA LUME (<data>/memos-md/*.md — thứ người dùng gõ trong app).
//   - KHÔNG đẩy memo từ MOUNT (llmwiki): llmwiki là NGUỒN CHÂN LÝ ở máy local, không phải nội dung
//     của Lume. Đẩy nó lên remote = nhân bản kho tri thức ra một nơi không ai quản.
//     Lọc bằng chính sự tồn tại của file trong memos-md — mount không có file ở đó.
//
// IDEMPOTENT: giữ sổ `<data>/sync-state.json` (localUID → {remote name, hash nội dung}).
//   - chưa có trong sổ  → POST tạo mới trên remote, ghi sổ.
//   - có, hash không đổi → BỎ QUA (chạy 10 lần vẫn không đẻ bản trùng).
//   - có, hash đổi      → PATCH cập nhật đúng memo đó.
// Không dựa vào remote để dò trùng: remote có thể không cho set uid, và hỏi remote mỗi memo thì chậm.
package remotesync

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"time"
)

type entry struct {
	RemoteName string `json:"remote_name"` // vd "memos/abc123" — id trên remote
	Hash       string `json:"hash"`        // sha256 nội dung đã đẩy
}

type state struct {
	Remote  string           `json:"remote"`
	Entries map[string]entry `json:"entries"` // localUID → entry
}

type Client struct {
	Remote string // https://lume.example.com
	Token  string
	HTTP   *http.Client
	Path   string // đường dẫn sổ sync-state.json
}

func New(remote, token, dataDir string) *Client {
	return &Client{
		Remote: remote, Token: token,
		HTTP: &http.Client{Timeout: 20 * time.Second},
		Path: filepath.Join(dataDir, "sync-state.json"),
	}
}

func hashOf(s string) string {
	h := sha256.Sum256([]byte(s))
	return hex.EncodeToString(h[:])
}

func (c *Client) load() (*state, error) {
	st := &state{Remote: c.Remote, Entries: map[string]entry{}}
	raw, err := os.ReadFile(c.Path)
	if os.IsNotExist(err) {
		return st, nil
	}
	if err != nil {
		return nil, err
	}
	if err := json.Unmarshal(raw, st); err != nil {
		return nil, err
	}
	if st.Entries == nil {
		st.Entries = map[string]entry{}
	}
	// Đổi remote ⇒ sổ cũ vô nghĩa (id bên kia không tồn tại ở bên này). Bắt đầu lại,
	// KHÔNG dùng nhầm id của server khác — đó là cách ghi đè bừa lên memo của người ta.
	if st.Remote != c.Remote {
		return &state{Remote: c.Remote, Entries: map[string]entry{}}, nil
	}
	return st, nil
}

func (c *Client) save(st *state) error {
	raw, err := json.MarshalIndent(st, "", "  ")
	if err != nil {
		return err
	}
	tmp := c.Path + ".tmp"
	if err := os.WriteFile(tmp, raw, 0o600); err != nil { // 0600: chứa dấu vết remote
		return err
	}
	return os.Rename(tmp, c.Path)
}

func (c *Client) do(method, path string, body any) (map[string]any, error) {
	var rdr io.Reader
	if body != nil {
		b, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		rdr = bytes.NewReader(b)
	}
	req, err := http.NewRequest(method, c.Remote+path, rdr)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	if c.Token != "" {
		req.Header.Set("Authorization", "Bearer "+c.Token)
	}
	resp, err := c.HTTP.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	raw, _ := io.ReadAll(resp.Body)
	if resp.StatusCode >= 300 {
		return nil, fmt.Errorf("remote %s %s → %d: %s", method, path, resp.StatusCode, truncate(string(raw), 200))
	}
	out := map[string]any{}
	_ = json.Unmarshal(raw, &out)
	return out, nil
}

func truncate(s string, n int) string {
	if len(s) <= n {
		return s
	}
	return s[:n] + "…"
}

// Memo — đơn vị đẩy lên (đọc từ kho local).
type Memo struct {
	UID        string
	Content    string
	Visibility string
}

// Result — báo cáo trung thực: đẩy được bao nhiêu, bỏ qua bao nhiêu, hỏng cái nào.
type Result struct {
	Created, Updated, Skipped int
	Failed                    []string
}

// Push đẩy danh sách memo local lên remote. dryRun = chỉ nói sẽ làm gì, không gọi mạng.
func (c *Client) Push(memos []Memo, dryRun bool) (Result, error) {
	res := Result{}
	st, err := c.load()
	if err != nil {
		return res, err
	}

	for _, m := range memos {
		h := hashOf(m.Content)
		prev, seen := st.Entries[m.UID]

		if seen && prev.Hash == h {
			res.Skipped++ // không đổi → không đẩy lại (idempotent)
			continue
		}
		if dryRun {
			if seen {
				res.Updated++
			} else {
				res.Created++
			}
			continue
		}

		vis := m.Visibility
		if vis == "" {
			vis = "PRIVATE"
		}

		if !seen {
			out, err := c.do(http.MethodPost, "/api/v1/memos", map[string]any{
				"content": m.Content, "visibility": vis,
			})
			if err != nil {
				res.Failed = append(res.Failed, m.UID+": "+err.Error())
				continue
			}
			name, _ := out["name"].(string)
			if name == "" {
				res.Failed = append(res.Failed, m.UID+": remote không trả về `name` — không ghi sổ được")
				continue
			}
			st.Entries[m.UID] = entry{RemoteName: name, Hash: h}
			res.Created++
			continue
		}

		// đã có trên remote → cập nhật ĐÚNG memo đó
		if _, err := c.do(http.MethodPatch, "/api/v1/"+prev.RemoteName+"?updateMask=content", map[string]any{
			"content": m.Content,
		}); err != nil {
			res.Failed = append(res.Failed, m.UID+": "+err.Error())
			continue
		}
		st.Entries[m.UID] = entry{RemoteName: prev.RemoteName, Hash: h}
		res.Updated++
	}

	if !dryRun {
		if err := c.save(st); err != nil {
			return res, err
		}
	}
	return res, nil
}
