package store

import (
	"context"
	"log/slog"
	"path/filepath"
	"strings"
	"sync"
	"time"

	"github.com/Rheinmir/lume/internal/profile"
	"github.com/Rheinmir/lume/store/cache"
	"github.com/Rheinmir/lume/store/file"
)

// Store provides database access to all raw objects.
type Store struct {
	profile *profile.Profile
	driver  Driver

	userCreateMu sync.Mutex

	// Cache settings
	cacheConfig cache.Config

	// Caches
	instanceSettingCache *cache.Cache // cache for instance settings
	userCache            *cache.Cache // cache for users
	userSettingCache     *cache.Cache // cache for user settings

	// FILE-FIRST (frame-n04): nội dung memo là file .md trên đĩa — NGUỒN CHÂN LÝ.
	// SQL chỉ còn là INDEX (id/uid/thời gian/visibility) để lọc nhanh. Đọc memo thì
	// FILE THẮNG DB. nil = tắt file-first (ví dụ trong unit-test không có thư mục data).
	mdStore *file.Store
}

// New creates a new instance of Store.
func New(driver Driver, profile *profile.Profile) *Store {
	// Default cache settings
	cacheConfig := cache.Config{
		DefaultTTL:      10 * time.Minute,
		CleanupInterval: 5 * time.Minute,
		MaxItems:        1000,
		OnEviction:      nil,
	}

	store := &Store{
		driver:               driver,
		profile:              profile,
		cacheConfig:          cacheConfig,
		instanceSettingCache: cache.New(cacheConfig),
		userCache:            cache.New(cacheConfig),
		userSettingCache:     cache.New(cacheConfig),
	}

	// file-first: memo .md nằm cạnh dữ liệu, trong <data>/memos-md/.
	// Không dựng được (không có Data dir, đĩa chỉ-đọc…) → chạy tiếp bằng DB, KHÔNG chết —
	// nhưng bất biến "ghi memo phải ra file" chỉ áp dụng khi mdStore != nil.
	if profile != nil && profile.Data != "" {
		if md, err := file.New(filepath.Join(profile.Data, "memos-md")); err == nil {
			store.mdStore = md
		}
	}

	// MOUNT (frame-n06): gắn thư mục ngoài (llmwiki) để ĐỌC. Chỉ gắn ở đây — việc quét index +
	// watch do StartMounts() làm (cần ctx + user, không có ở đây).
	if profile != nil && store.mdStore != nil {
		for _, spec := range profile.Mounts {
			name, root, ok := strings.Cut(spec, "=")
			if !ok || name == "" || root == "" {
				slog.Warn("bỏ qua --mount sai dạng (cần name=path)", slog.String("spec", spec))
				continue
			}
			store.mdStore.Attach(file.NewMount(name, root))
		}
	}

	return store
}

// StartMounts — quét index + bật watcher cho mọi mount. Gọi lúc server khởi động.
// creatorID: memo wiki thuộc về ai (thường là host user).
func (s *Store) StartMounts(ctx context.Context, creatorID int32) {
	if s.mdStore == nil {
		return
	}
	for _, m := range s.mdStore.Mounts() {
		c, u, err := s.SyncMount(ctx, m, creatorID)
		if err != nil {
			// KHÔNG chết server vì một mount hỏng — nhưng phải kêu to, đừng im lặng chạy tiếp
			// rồi để user tưởng wiki đã lên app.
			slog.Error("mount KHÔNG gắn được — wiki sẽ KHÔNG hiện trong app",
				slog.String("mount", m.Name), slog.String("root", m.Root), slog.Any("err", err))
			continue
		}
		slog.Info("mount đã gắn (read-only)", slog.String("mount", m.Name), slog.String("root", m.Root),
			slog.Int("memo mới", c), slog.Int("cập nhật", u))
		if err := s.WatchMount(ctx, m, creatorID); err != nil {
			slog.Warn("watcher không bật được — file đổi sẽ KHÔNG tự hiện", slog.Any("err", err))
		}
	}
}

func (s *Store) GetDriver() Driver {
	return s.driver
}

// GetDataDir returns the store data directory.
func (s *Store) GetDataDir() string {
	return s.profile.Data
}

func (s *Store) Close() error {
	// Stop all cache cleanup goroutines
	s.instanceSettingCache.Close()
	s.userCache.Close()
	s.userSettingCache.Close()

	return s.driver.Close()
}
