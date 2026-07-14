import { cn } from "@/lib/utils";

interface Props {
  avatarUrl?: string;
  className?: string;
}

// Lume: KHÔNG dùng logo vẹt nền đen của memos làm avatar mặc định (nó tạo mảng đen nổi
// cộm trên mặt neumorphic sáng — lỗi "span đen"). Không có ảnh → vẽ mark neumorphic
// cùng mặt phẳng (inset, đơn sắc), giữ mặt phẳng đơn sắc của neumorphism.
const UserAvatar = (props: Props) => {
  const { avatarUrl, className } = props;

  if (!avatarUrl) {
    return (
      <div
        className={cn("w-8 h-8 rounded-xl grid place-items-center shrink-0", className)}
        style={{
          background: "var(--neu-bg)",
          boxShadow: "inset 2px 2px 4px var(--neu-dark), inset -2px -2px 4px var(--neu-light)",
        }}
      >
        <span
          style={{
            width: "40%",
            height: "40%",
            borderRadius: "50%",
            background: "radial-gradient(circle at 35% 30%, #fff, var(--neu-accent) 92%)",
          }}
        />
      </div>
    );
  }

  return (
    <div className={cn("w-8 h-8 overflow-clip rounded-xl shrink-0", className)} style={{ border: "none" }}>
      <img className="w-full h-full object-cover" src={avatarUrl} decoding="async" loading="lazy" alt="" />
    </div>
  );
};

export default UserAvatar;
