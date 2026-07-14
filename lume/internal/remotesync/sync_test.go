package remotesync

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

// Bất biến của sync local → remote (frame-n07).
func TestPush(t *testing.T) {
	var posts, patches int
	var gotAuth string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotAuth = r.Header.Get("Authorization")
		switch r.Method {
		case http.MethodPost:
			posts++
			_ = json.NewEncoder(w).Encode(map[string]any{"name": "memos/remote1"})
		case http.MethodPatch:
			patches++
			_ = json.NewEncoder(w).Encode(map[string]any{"name": "memos/remote1"})
		default:
			w.WriteHeader(http.StatusMethodNotAllowed)
		}
	}))
	defer srv.Close()

	dir := t.TempDir()
	c := New(srv.URL, "tok123", dir)
	memos := []Memo{{UID: "local-1", Content: "ghi chú A", Visibility: "PRIVATE"}}

	// ① Lần đầu → TẠO trên remote, có gửi token.
	res, err := c.Push(memos, false)
	if err != nil {
		t.Fatal(err)
	}
	if res.Created != 1 || posts != 1 {
		t.Fatalf("lần đầu phải tạo 1: %+v (posts=%d)", res, posts)
	}
	if gotAuth != "Bearer tok123" {
		t.Fatalf("không gửi token: %q", gotAuth)
	}

	// ② IDEMPOTENT: chạy lại, nội dung không đổi → KHÔNG đẩy lại, KHÔNG đẻ bản trùng.
	res, _ = c.Push(memos, false)
	if res.Skipped != 1 || res.Created != 0 || posts != 1 {
		t.Fatalf("chạy lại phải BỎ QUA, không tạo thêm: %+v (posts=%d)", res, posts)
	}

	// ③ Sửa nội dung → PATCH đúng memo cũ (không tạo bản thứ hai).
	memos[0].Content = "ghi chú A (đã sửa)"
	res, _ = c.Push(memos, false)
	if res.Updated != 1 || patches != 1 || posts != 1 {
		t.Fatalf("sửa nội dung phải PATCH, không POST: %+v (posts=%d patches=%d)", res, posts, patches)
	}

	// ④ dry-run → nói sẽ làm gì, KHÔNG gọi mạng.
	memos[0].Content = "lại sửa"
	before := posts + patches
	res, _ = c.Push(memos, true)
	if res.Updated != 1 || posts+patches != before {
		t.Fatalf("dry-run không được gọi mạng: %+v", res)
	}

	// ⑤ ĐỔI REMOTE → sổ cũ bị bỏ (id của server kia không dùng cho server này —
	//    dùng nhầm là GHI ĐÈ lên memo của người khác).
	c2 := New(srv.URL+"/khac", "tok123", dir)
	st, err := c2.load()
	if err != nil {
		t.Fatal(err)
	}
	if len(st.Entries) != 0 {
		t.Fatalf("đổi remote mà vẫn dùng sổ cũ ⇒ nguy cơ ghi đè memo người khác: %+v", st.Entries)
	}

	// ⑥ Remote lỗi → báo FAILED, KHÔNG ghi sổ (lần sau còn thử lại được).
	bad := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusInternalServerError)
	}))
	defer bad.Close()
	c3 := New(bad.URL, "t", t.TempDir())
	res, _ = c3.Push([]Memo{{UID: "x", Content: "y"}}, false)
	if len(res.Failed) != 1 || res.Created != 0 {
		t.Fatalf("remote lỗi phải báo failed: %+v", res)
	}
	st3, _ := c3.load()
	if len(st3.Entries) != 0 {
		t.Fatal("đẩy hỏng mà vẫn ghi sổ ⇒ lần sau tưởng đã đẩy rồi, memo mất luôn")
	}
}
