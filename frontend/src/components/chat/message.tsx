import { cn } from '@/lib/utils';
import { Message } from '@/types/chat';
import { CodeEditor } from './code-editor';
import { parseMessageContent } from '@/lib/message-parser';
import { Avatar } from '@/components/ui/avatar';

interface MessageProps {
  message: Message;
}

export function ChatMessage({ message }: MessageProps) {
  const isUser = message.role === 'user';
  const { text, codeBlocks, headings } = parseMessageContent(message.content);

  const renderContent = (part: string, index: number) => {
    // Check if this part is a heading
    const headingMatch = part.match(/\[HEADING_(\d+)\]/);
    if (headingMatch) {
      const headingIndex = parseInt(headingMatch[1]);
      const heading = headings[headingIndex];
      return (
        <div key={index} className="mt-4 first:mt-0">
          <h3 className="font-bold text-lg mb-2">{heading.text}</h3>
        </div>
      );
    }

    // Check if this part is a code block
    const codeMatch = part.match(/\[CODE_BLOCK_(\d+)\]/);
    if (codeMatch) {
      const codeIndex = parseInt(codeMatch[1]);
      const code = codeBlocks[codeIndex];
      return (
        <div key={index} className="mt-2">
          <CodeEditor
            code={code.code}
            className="my-2"
          />
        </div>
      );
    }

    // Regular text
    return <div key={index}>{part}</div>;
  };

  return (
    <div
      className={cn(
        'flex w-full gap-4',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      {!isUser && (
        <Avatar className="h-8 w-8">
          <div className="flex h-full w-full items-center justify-center rounded-full bg-primary text-primary-foreground">
            AI
          </div>
        </Avatar>
      )}
      <div
        className={cn(
          'rounded-lg px-4 py-2 max-w-[80%]',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-muted'
        )}
      >
        <div className="prose prose-sm dark:prose-invert">
          {text.split(/(\[CODE_BLOCK_\d+\]|\[HEADING_\d+\])/).map((part, index) => renderContent(part, index))}
        </div>
        <div className="mt-2 text-xs text-muted-foreground">
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
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