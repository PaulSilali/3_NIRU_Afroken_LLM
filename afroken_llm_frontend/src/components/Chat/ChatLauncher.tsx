import { MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChatStore } from '@/store/chatStore';

export function ChatLauncher() {
  const { setIsOpen } = useChatStore();

  return (
    <div className="pointer-events-none fixed bottom-4 right-4 z-40 sm:bottom-6 sm:right-6">
      <Button
        type="button"
        size="lg"
        className="pointer-events-auto flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-glow hover:bg-primary/90 focus-ring"
        onClick={() => setIsOpen(true)}
        aria-label="Open AfroKen chat"
      >
        <span className="relative flex h-8 w-8 items-center justify-center rounded-full bg-primary-foreground/10">
          <MessageCircle className="h-4 w-4" />
          <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-accent shadow-sm" />
        </span>
        <span>Ask AfroKen</span>
      </Button>
    </div>
  );
}


