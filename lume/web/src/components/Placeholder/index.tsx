import { type ReactNode, useState } from "react";
import { cn } from "@/lib/utils";
import { DEFAULT_MESSAGES, type PlaceholderVariant } from "./messages";
import TileSpriteStrip from "./TileSpriteStrip";
import { pickTileSprite } from "./tileSprites";

interface PlaceholderProps {
  variant: PlaceholderVariant;
  message?: string;
  children?: ReactNode;
  className?: string;
}

const DISPLAY_SCALE = 2;

const Placeholder = ({ variant, message, children, className }: PlaceholderProps) => {
  const [sprite] = useState(pickTileSprite);
  const resolvedMessage = message ?? DEFAULT_MESSAGES[variant];
  const isLoading = variant === "loading";

  return (
    <div
      role={isLoading ? "status" : undefined}
      aria-live={isLoading ? "polite" : undefined}
      className={cn("flex flex-col items-center justify-center max-w-md mx-auto px-4 py-8", className)}
    >
      {/* Lume: empty-state neumorphic trung tính, thay sprite pixel-art (rebrand) */}
      <span
        data-testid="placeholder-sprite"
        style={{
          width: 72, height: 72, borderRadius: 24, background: "var(--neu-bg)",
          boxShadow: "inset 5px 5px 10px var(--neu-dark), inset -5px -5px 10px var(--neu-light)",
          display: "grid", placeItems: "center",
        }}
      >
        <span style={{ width: 26, height: 26, borderRadius: "50%", background: "var(--neu-bg)", boxShadow: "3px 3px 6px var(--neu-dark), -3px -3px 6px var(--neu-light)" }} />
      </span>
      <p className="mt-3 font-mono text-sm text-muted-foreground">{resolvedMessage}</p>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
};

export default Placeholder;
