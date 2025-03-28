import { Message } from '@/types/chat';
import { Avatar } from '@/components/ui/avatar';
import { Card } from '@/components/ui/card';

interface MessageProps {
  message: Message;
}

export function ChatMessage({ message }: MessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="h-8 w-8">
          <div className="flex h-full w-full items-center justify-center rounded-full bg-primary text-primary-foreground">
            AI
          </div>
        </Avatar>
      )}
      <Card className={`max-w-[80%] p-4 ${isUser ? 'bg-primary text-primary-foreground' : ''}`}>
        <p className="whitespace-pre-wrap">{message.content}</p>
        <p className="mt-2 text-xs opacity-70">
          {new Date(message.timestamp).toLocaleTimeString()}
        </p>
      </Card>
      {isUser && (
        <Avatar className="h-8 w-8">
          <div className="flex h-full w-full items-center justify-center rounded-full bg-muted">
            U
          </div>
        </Avatar>
      )}
    </div>
  );
} 