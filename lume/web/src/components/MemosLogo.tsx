import { useInstance } from "@/contexts/InstanceContext";
import { cn } from "@/lib/utils";

interface Props {
  className?: string;
  collapsed?: boolean;
}

// Lume — logo neumorphic: một "nguồn sáng" nổi mềm (đúng tinh thần soft-UI), thay logo vẹt memos.
function MemosLogo(props: Props) {
  const { collapsed } = props;
  const { generalSetting: instanceGeneralSetting } = useInstance();
  const title = instanceGeneralSetting.customProfile?.title || "Lume";

  return (
    <div className={cn("relative w-full h-auto shrink-0", props.className)}>
      <div className={cn("w-auto flex flex-row justify-start items-center", collapsed ? "px-1" : "px-3")}>
        <span
          className="shrink-0 grid place-items-center"
          style={{
            width: 34, height: 34, borderRadius: 12, background: "var(--neu-bg)",
            boxShadow: "inset 2px 2px 4px var(--neu-dark), inset -2px -2px 4px var(--neu-light)",
          }}
        >
          <span
            style={{
              width: 14, height: 14, borderRadius: "50%",
              background: "radial-gradient(circle at 35% 30%, #fff, var(--neu-accent) 90%)",
              boxShadow: "inset 1px 1px 2px rgba(0,0,0,.15)",
            }}
          />
        </span>
        {!collapsed && (
          <span className="ml-2.5 text-lg font-semibold tracking-tight shrink truncate" style={{ color: "var(--neu-ink)" }}>
            {title}
          </span>
        )}
      </div>
    </div>
  );
}

export default MemosLogo;
