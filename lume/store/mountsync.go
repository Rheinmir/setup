package store

// MOUNTSYNC — đồng bộ INDEX cho các thư mục gắn ngoài (llmwiki), và WATCH để stream thay đổi.
//
// Nhớ ranh giới: ở đây CHỈ đụng INDEX (row trong SQL: uid/ts/tag). Nội dung KHÔNG copy vào DB,
// KHÔNG copy vào memos-md — nó được đọc thẳng từ file gốc mỗi lần list (xem store/file/mount.go).
// ⇒ Không có bản thứ hai để lệch, và Lume không bao giờ ghi vào kho tri thức.

import (
	"context"
	"log/slog"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/fsnotify/fsnotify"
	"github.com/pkg/errors"

	storepb "github.com/Rheinmir/lume/proto/gen/store"
	"github.com/Rheinmir/lume/store/file"
)

// SyncMount quét mount rồi upsert INDEX. Trả về (đã tạo, đã cập nhật).
func (s *Store) SyncMount(ctx context.Context, m *file.Mount, creatorID int32) (int, int, error) {
	res, err := m.Scan()
	if err != nil {
		// PHANH: quét lỗi / ra 0 file (mount trỏ sai, ổ chưa gắn) ⇒ KHÔNG dọn index.
		// Xoá sạch 201 memo vì một cái flag sai là hỏng không cứu được.
		return 0, 0, errors.Wrap(err, "mount scan")
	}
	for _, c := range res.Collisions {
		// Không im lặng nuốt file: uid đụng nhau = một file biến mất khỏi app mà không ai biết.
		slog.Warn("mount: VA CHẠM UID — file bị bỏ qua", slog.String("mount", m.Name), slog.String("pair", c))
	}

	created, updated := 0, 0
	for _, uid := range res.UIDs {
		rel, _ := m.RelPath(uid)
		ts, _ := m.ModTime(uid)
		tags := m.TagsFor(rel)

		existing, err := s.driver.ListMemos(ctx, &FindMemo{UID: &uid})
		if err != nil {
			return created, updated, err
		}
		if len(existing) == 0 {
			// Content rỗng trong DB LÀ CỐ Ý: nội dung sống ở file gốc, ListMemos đọc từ đó.
			if _, err := s.driver.CreateMemo(ctx, &Memo{
				UID: uid, CreatorID: creatorID, RowStatus: Normal,
				CreatedTs: ts, UpdatedTs: ts,
				Content: "", Visibility: Private,
				Payload: &storepb.MemoPayload{Tags: tags},
			}); err != nil {
				return created, updated, err
			}
			created++
			continue
		}
		memo := existing[0]
		if memo.UpdatedTs != ts {
			if err := s.driver.UpdateMemo(ctx, &UpdateMemo{
				ID: memo.ID, UpdatedTs: &ts,
				Payload: &storepb.MemoPayload{Tags: tags},
			}); err != nil {
				return created, updated, err
			}
			updated++
		}
	}
	return created, updated, nil
}

// WatchMount — STREAM: file đổi ngoài đĩa → index cập nhật ngay (nội dung thì luôn đọc thẳng file,
// nên UI thấy bản mới ở lần list kế tiếp). Chặn tại đây các bẫy đã biết:
//   - fsnotify KHÔNG đệ quy → phải add từng thư mục con, và add thư mục MỚI sinh ra.
//   - editor ghi kiểu tmp+rename → một lần lưu đẻ nhiều event → DEBOUNCE gom lại.
//   - `git checkout` nhánh khác → ~200 event một lúc → debounce phải gom theo BATCH, không per-file.
func (s *Store) WatchMount(ctx context.Context, m *file.Mount, creatorID int32) error {
	w, err := fsnotify.NewWatcher()
	if err != nil {
		return err
	}
	// add đệ quy mọi thư mục hiện có (fsnotify không tự đệ quy)
	if err := addRecursive(w, m.Root); err != nil {
		return err
	}

	go func() {
		defer w.Close()
		var timer *time.Timer
		fire := make(chan struct{}, 1)
		for {
			select {
			case <-ctx.Done():
				return
			case ev, ok := <-w.Events:
				if !ok {
					return
				}
				if strings.HasSuffix(ev.Name, ".md") || ev.Op&fsnotify.Create != 0 {
					if ev.Op&fsnotify.Create != 0 {
						if st, err := osStat(ev.Name); err == nil && st {
							_ = addRecursive(w, ev.Name) // thư mục mới → watch luôn
						}
					}
					if timer != nil {
						timer.Stop()
					}
					timer = time.AfterFunc(300*time.Millisecond, func() {
						select {
						case fire <- struct{}{}:
						default:
						}
					})
				}
			case <-fire:
				if c, u, err := s.SyncMount(ctx, m, creatorID); err != nil {
					slog.Warn("mount sync lỗi", slog.String("mount", m.Name), slog.Any("err", err))
				} else if c+u > 0 {
					slog.Info("mount stream", slog.String("mount", m.Name),
						slog.Int("created", c), slog.Int("updated", u))
				}
			case err, ok := <-w.Errors:
				if !ok {
					return
				}
				slog.Warn("mount watcher lỗi", slog.Any("err", err))
			}
		}
	}()
	return nil
}

// addRecursive — fsnotify chỉ watch ĐÚNG thư mục được add, không đệ quy. Thư mục con không add =
// sửa file trong đó KHÔNG sinh event = "stream" chết âm thầm.
func addRecursive(w *fsnotify.Watcher, root string) error {
	return filepath.WalkDir(root, func(p string, d os.DirEntry, err error) error {
		if err != nil {
			return nil // thư mục biến mất giữa chừng → bỏ qua, đừng làm chết watcher
		}
		if !d.IsDir() {
			return nil
		}
		if strings.HasPrefix(d.Name(), ".") && p != root {
			return filepath.SkipDir // bỏ .git — nó đẻ hàng ngàn event vô nghĩa
		}
		return w.Add(p)
	})
}

// osStat — true nếu path là thư mục (dùng khi có event Create để watch thư mục mới).
func osStat(p string) (bool, error) {
	st, err := os.Stat(p)
	if err != nil {
		return false, err
	}
	return st.IsDir(), nil
}
