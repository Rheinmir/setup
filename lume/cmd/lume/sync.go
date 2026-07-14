package main

// `lume sync` — ĐẨY memo local lên một instance Lume ở XA. THỦ CÔNG: chỉ chạy khi người gõ lệnh,
// không có nền, không tự động (frame-n07).
//
// CHỈ đẩy memo TRONG KHO CỦA LUME (<data>/memos-md/*.md — thứ người dùng gõ trong app).
// KHÔNG đẩy memo từ mount (llmwiki): llmwiki là NGUỒN CHÂN LÝ ở máy local, không phải nội dung của
// Lume — đẩy nó lên remote là nhân bản kho tri thức ra một nơi không ai quản.

import (
	"fmt"
	"log/slog"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
	"github.com/spf13/viper"

	"github.com/Rheinmir/lume/internal/remotesync"
	"github.com/Rheinmir/lume/store/file"
)

var syncCmd = &cobra.Command{
	Use:   "sync",
	Short: "Đẩy memo local lên Lume remote (thủ công, idempotent). Memo từ --mount (llmwiki) KHÔNG được đẩy.",
	Run: func(cmd *cobra.Command, _ []string) {
		data := viper.GetString("data")
		remote, _ := cmd.Flags().GetString("remote")
		token, _ := cmd.Flags().GetString("token")
		dry, _ := cmd.Flags().GetBool("dry-run")

		if remote == "" {
			slog.Error("thiếu --remote (vd --remote https://lume.example.com)")
			os.Exit(1)
		}
		if token == "" {
			token = os.Getenv("LUME_TOKEN") // token qua ENV, đừng bắt gõ vào shell history
		}
		if token == "" && !dry {
			slog.Error("thiếu --token hoặc biến môi trường LUME_TOKEN")
			os.Exit(1)
		}

		dir := filepath.Join(data, "memos-md")
		st, err := file.New(dir)
		if err != nil {
			slog.Error("không mở được kho memo local", "dir", dir, "error", err)
			os.Exit(1)
		}
		uids, err := st.List() // <- chỉ file trong memos-md ⇒ memo mount KHÔNG lọt vào đây
		if err != nil {
			slog.Error("không đọc được kho memo local", "error", err)
			os.Exit(1)
		}

		var memos []remotesync.Memo
		for _, uid := range uids {
			meta, body, ok, err := st.ReadMeta(uid)
			if err != nil || !ok {
				continue
			}
			memos = append(memos, remotesync.Memo{UID: uid, Content: body, Visibility: meta.Visibility})
		}

		c := remotesync.New(remote, token, data)
		res, err := c.Push(memos, dry)
		if err != nil {
			slog.Error("sync hỏng", "error", err)
			os.Exit(1)
		}

		prefix := ""
		if dry {
			prefix = "[dry-run] "
		}
		fmt.Printf("%s%d memo local · tạo %d · cập nhật %d · bỏ qua (không đổi) %d · hỏng %d → %s\n",
			prefix, len(memos), res.Created, res.Updated, res.Skipped, len(res.Failed), remote)
		for _, f := range res.Failed {
			fmt.Println("  ✗", f)
		}
		// Có memo hỏng ⇒ exit != 0: đừng để script gọi tưởng đã đẩy hết.
		if len(res.Failed) > 0 {
			os.Exit(1)
		}
	},
}

func init() {
	syncCmd.Flags().String("remote", "", "URL instance Lume ở xa, vd https://lume.example.com")
	syncCmd.Flags().String("token", "", "access token của remote (hoặc đặt biến môi trường LUME_TOKEN)")
	syncCmd.Flags().Bool("dry-run", false, "chỉ in ra sẽ đẩy gì, KHÔNG gọi mạng")
	rootCmd.AddCommand(syncCmd)
}
