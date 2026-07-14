package store

import (
	"context"

	"github.com/pkg/errors"

	"github.com/Rheinmir/lume/internal/base"
	"github.com/Rheinmir/lume/store/file"

	storepb "github.com/Rheinmir/lume/proto/gen/store"
)

// Visibility is the type of a visibility.
type Visibility string

const (
	// Public is the PUBLIC visibility.
	Public Visibility = "PUBLIC"
	// Protected is the PROTECTED visibility.
	Protected Visibility = "PROTECTED"
	// Private is the PRIVATE visibility.
	Private Visibility = "PRIVATE"
)

func (v Visibility) String() string {
	switch v {
	case Public:
		return "PUBLIC"
	case Protected:
		return "PROTECTED"
	default:
		return "PRIVATE"
	}
}

type Memo struct {
	// ID is the system generated unique identifier for the memo.
	ID int32
	// UID is the user defined unique identifier for the memo.
	UID string

	// Standard fields
	RowStatus RowStatus
	CreatorID int32
	CreatedTs int64
	UpdatedTs int64

	// Domain specific fields
	Content    string
	Visibility Visibility
	Pinned     bool
	Payload    *storepb.MemoPayload

	// Composed fields
	ParentUID *string
}

type FindMemo struct {
	ID  *int32
	UID *string

	IDList  []int32
	UIDList []string

	// Standard fields
	RowStatus *RowStatus
	CreatorID *int32

	// Domain specific fields
	VisibilityList  []Visibility
	ExcludeContent  bool
	ExcludeComments bool
	Filters         []string

	// Pagination
	Limit  *int
	Offset *int

	// Ordering
	OrderByPinned    bool
	OrderByUpdatedTs bool
	OrderByTimeAsc   bool
}

type FindMemoPayload struct {
	Raw                *string
	TagSearch          []string
	HasLink            bool
	HasTaskList        bool
	HasCode            bool
	HasIncompleteTasks bool
}

type UpdateMemo struct {
	ID         int32
	UID        *string
	CreatedTs  *int64
	UpdatedTs  *int64
	RowStatus  *RowStatus
	Content    *string
	Visibility *Visibility
	Pinned     *bool
	Payload    *storepb.MemoPayload
}

type DeleteMemo struct {
	ID int32
}

// ── FILE-FIRST (frame-n04) ────────────────────────────────────────────────────────────────
// Nội dung memo là file `.md` trên đĩa = NGUỒN CHÂN LÝ (người đọc/sửa/grep/git được).
// SQL còn lại làm INDEX (lọc/tìm kiếm). Luật: GHI ⇒ phải ra file. ĐỌC ⇒ FILE THẮNG DB.
// Memo cũ (tạo trước khi bật file-first) chưa có file → đọc rơi về DB, không vỡ.

// mdMeta dựng frontmatter từ record — một chỗ duy nhất, khỏi lệch giữa create/update.
func mdMeta(m *Memo) file.Meta {
	return file.Meta{
		ID: m.ID, UID: m.UID, CreatorID: m.CreatorID,
		CreatedTs: m.CreatedTs, UpdatedTs: m.UpdatedTs,
		Visibility: string(m.Visibility), RowStatus: string(m.RowStatus),
	}
}

func (s *Store) CreateMemo(ctx context.Context, create *Memo) (*Memo, error) {
	if !base.UIDMatcher.MatchString(create.UID) {
		return nil, errors.New("invalid uid")
	}
	memo, err := s.driver.CreateMemo(ctx, create)
	if err != nil {
		return nil, err
	}
	if s.mdStore != nil {
		// Ghi file HỎNG = TẠO MEMO HỎNG. Không nuốt lỗi: file-first mà file không ghi được
		// thì nguồn chân lý không tồn tại — báo lỗi thẳng, đừng để user tưởng đã lưu.
		if err := s.mdStore.Write(mdMeta(memo), memo.Content); err != nil {
			return nil, errors.Wrap(err, "file-first: ghi .md thất bại")
		}
	}
	return memo, nil
}

func (s *Store) ListMemos(ctx context.Context, find *FindMemo) ([]*Memo, error) {
	list, err := s.driver.ListMemos(ctx, find)
	if err != nil {
		return nil, err
	}
	if s.mdStore == nil {
		return list, nil
	}
	for _, m := range list {
		// FILE THẮNG DB: ai sửa .md bằng tay (đúng tinh thần file-first) thì thấy ngay.
		if body, ok, err := s.mdStore.Read(m.UID); err == nil && ok {
			m.Content = body
		}
	}
	return list, nil
}

func (s *Store) GetMemo(ctx context.Context, find *FindMemo) (*Memo, error) {
	list, err := s.ListMemos(ctx, find)
	if err != nil {
		return nil, err
	}
	if len(list) == 0 {
		return nil, nil
	}

	memo := list[0]
	return memo, nil
}

func (s *Store) UpdateMemo(ctx context.Context, update *UpdateMemo) error {
	if update.UID != nil && !base.UIDMatcher.MatchString(*update.UID) {
		return errors.New("invalid uid")
	}
	if err := s.driver.UpdateMemo(ctx, update); err != nil {
		return err
	}
	if s.mdStore == nil {
		return nil
	}
	// Ghi lại file từ TRẠNG THÁI SAU CẬP NHẬT (đọc thẳng driver — tránh vòng lặp qua ListMemos
	// của chính mình, và tránh lấy nội dung cũ từ file).
	list, err := s.driver.ListMemos(ctx, &FindMemo{ID: &update.ID})
	if err != nil || len(list) == 0 {
		return err
	}
	memo := list[0]
	return errors.Wrap(s.mdStore.Write(mdMeta(memo), memo.Content), "file-first: ghi .md thất bại")
}

func (s *Store) DeleteMemo(ctx context.Context, delete *DeleteMemo) error {
	// Lấy uid TRƯỚC khi xoá khỏi DB — xoá xong thì không còn tra được uid để xoá file,
	// file sẽ mồ côi và vẫn tự xưng là "nguồn chân lý" của một memo đã chết.
	var uid string
	if s.mdStore != nil {
		if list, err := s.driver.ListMemos(ctx, &FindMemo{ID: &delete.ID}); err == nil && len(list) > 0 {
			uid = list[0].UID
		}
	}

	// Clean up memo_relation records where this memo is either the source or target.
	if err := s.driver.DeleteMemoRelation(ctx, &DeleteMemoRelation{MemoID: &delete.ID}); err != nil {
		return err
	}
	if err := s.driver.DeleteMemoRelation(ctx, &DeleteMemoRelation{RelatedMemoID: &delete.ID}); err != nil {
		return err
	}
	// Clean up attachments linked to this memo.
	attachments, err := s.ListAttachments(ctx, &FindAttachment{MemoID: &delete.ID})
	if err != nil {
		return err
	}
	for _, attachment := range attachments {
		if err := s.DeleteAttachment(ctx, &DeleteAttachment{ID: attachment.ID}); err != nil {
			return err
		}
	}
	if err := s.driver.DeleteMemo(ctx, delete); err != nil {
		return err
	}
	if s.mdStore != nil && uid != "" {
		return errors.Wrap(s.mdStore.Delete(uid), "file-first: xoá .md thất bại")
	}
	return nil
}
