import { ChatArea } from '../components/Chat/ChatArea';
import { useAppStore } from '../lib/store';

export function ChatPage() {
  const canvasOpen = useAppStore((s) => s.canvasOpen);

  return (
    <div className="flex h-full overflow-hidden">
      <div className="flex-1 min-w-0">
        <ChatArea />
      </div>
    </div>
  );
}
