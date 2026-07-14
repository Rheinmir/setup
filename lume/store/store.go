package store

import (
	"path/filepath"
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

	return store
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
